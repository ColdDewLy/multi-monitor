"""Multi-Monitor Layout Switcher — CLI entry point and core logic."""
import base64
import ctypes
import json
import os
import sys

import winapi

PROFILES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles.json")


def _load_profiles():
    if os.path.exists(PROFILES_PATH):
        with open(PROFILES_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_profiles(profiles):
    with open(PROFILES_PATH, "w") as f:
        json.dump(profiles, f, indent=2)


def _get_active_display_info():
    """Get friendly names for active displays via CCD API."""
    result = winapi.query_display_config()
    if not result:
        return []
    paths, modes, num_paths, num_modes = result
    info = []
    for i in range(num_paths):
        path = paths[i]
        src = path.sourceInfo
        tgt = path.targetInfo
        target_name = winapi.get_target_name(tgt.adapterId, tgt.id)
        source_name = winapi.get_source_name(src.adapterId, src.id)
        friendly = target_name.monitorFriendlyDeviceName if target_name else ""
        gdi = source_name.viewGdiDeviceName if source_name else ""
        info.append({"friendly_name": friendly, "device_name": gdi})
    return info


def _refresh_adapter_luids(paths, num_paths, modes, num_modes):
    """Update stale adapter LUIDs in saved config using current system LUIDs."""
    current = winapi.query_display_config()
    if not current:
        return
    cur_paths, _, cur_np, _ = current

    # Map old LUID -> new LUID by matching target IDs (persistent across reboots)
    luid_map = {}
    for i in range(num_paths):
        old = paths[i].targetInfo.adapterId
        old_key = (old.LowPart, old.HighPart)
        if old_key in luid_map:
            continue
        for j in range(cur_np):
            if cur_paths[j].targetInfo.id == paths[i].targetInfo.id:
                new = cur_paths[j].targetInfo.adapterId
                luid_map[old_key] = (new.LowPart, new.HighPart)
                break

    def _update(luid):
        key = (luid.LowPart, luid.HighPart)
        if key in luid_map:
            luid.LowPart, luid.HighPart = luid_map[key]

    for i in range(num_paths):
        _update(paths[i].sourceInfo.adapterId)
        _update(paths[i].targetInfo.adapterId)
    for i in range(num_modes):
        _update(modes[i].adapterId)


# --- Commands ---

def cmd_show():
    # Show all adapters with GDI info
    active_info = {d["device_name"]: d["friendly_name"] for d in _get_active_display_info()}
    fmt = "{:<16} {:<24} {:<8} {:<14} {:<12} {:<7}"
    print(fmt.format("Device", "Name", "Active", "Resolution", "Position", "Primary"))
    print("-" * 85)
    for i in range(32):
        dev = winapi.enum_display_devices(i)
        if not dev:
            break
        name = dev.DeviceName
        active = bool(dev.StateFlags & winapi.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP)
        primary = bool(dev.StateFlags & winapi.DISPLAY_DEVICE_PRIMARY_DEVICE)
        dm = winapi.get_display_settings(name)
        friendly = active_info.get(name, "") or dev.DeviceString
        res = f"{dm.dmPelsWidth}x{dm.dmPelsHeight}" if dm and active else "-"
        pos = f"({dm.dmPositionX},{dm.dmPositionY})" if dm and active else "-"
        pri = "Yes" if primary else ""
        print(fmt.format(name, friendly[:24], "Yes" if active else "No", res, pos, pri))


def cmd_save(name):
    result = winapi.query_display_config()
    if not result:
        print("Failed to query display config.")
        sys.exit(1)
    paths, modes, num_paths, num_modes = result

    # Serialize raw CCD data
    paths_bytes = bytes(paths)[:num_paths * ctypes.sizeof(winapi.DISPLAYCONFIG_PATH_INFO)]
    modes_bytes = bytes(modes)[:num_modes * ctypes.sizeof(winapi.DISPLAYCONFIG_MODE_INFO)]

    # Also store human-readable summary
    display_info = _get_active_display_info()

    profiles = _load_profiles()
    profiles[name] = {
        "num_paths": num_paths,
        "num_modes": num_modes,
        "paths": base64.b64encode(paths_bytes).decode(),
        "modes": base64.b64encode(modes_bytes).decode(),
        "summary": [d["friendly_name"] or d["device_name"] for d in display_info],
    }
    _save_profiles(profiles)
    print(f"Saved profile '{name}' ({num_paths} active display(s): {', '.join(profiles[name]['summary'])}).")


def cmd_list():
    profiles = _load_profiles()
    if not profiles:
        print("No saved profiles.")
        return
    for name, data in profiles.items():
        summary = ", ".join(data.get("summary", []))
        print(f"  {name}: {data['num_paths']} active — {summary}")


def cmd_apply(name):
    profiles = _load_profiles()
    if name not in profiles:
        print(f"Profile '{name}' not found.")
        sys.exit(1)

    data = profiles[name]
    num_paths = data["num_paths"]
    num_modes = data["num_modes"]

    # Deserialize
    paths_bytes = base64.b64decode(data["paths"])
    modes_bytes = base64.b64decode(data["modes"])

    paths = (winapi.DISPLAYCONFIG_PATH_INFO * num_paths)()
    ctypes.memmove(paths, paths_bytes, len(paths_bytes))

    modes = (winapi.DISPLAYCONFIG_MODE_INFO * num_modes)()
    ctypes.memmove(modes, modes_bytes, len(modes_bytes))

    _refresh_adapter_luids(paths, num_paths, modes, num_modes)

    flags = (winapi.SDC_APPLY | winapi.SDC_USE_SUPPLIED_DISPLAY_CONFIG
             | winapi.SDC_ALLOW_CHANGES | winapi.SDC_SAVE_TO_DATABASE)

    ret = winapi.set_display_config(paths, num_paths, modes, num_modes, flags)
    if ret != 0:
        print(f"SetDisplayConfig failed (code {ret}). Retrying without save...")
        # Retry without SDC_SAVE_TO_DATABASE
        flags = winapi.SDC_APPLY | winapi.SDC_USE_SUPPLIED_DISPLAY_CONFIG | winapi.SDC_ALLOW_CHANGES
        ret = winapi.set_display_config(paths, num_paths, modes, num_modes, flags)
        if ret != 0:
            print(f"Failed again (code {ret}).")
            sys.exit(1)

    summary = ", ".join(data.get("summary", []))
    print(f"Applied profile '{name}' ({summary}).")


def cmd_delete(name):
    profiles = _load_profiles()
    if name not in profiles:
        print(f"Profile '{name}' not found.")
        sys.exit(1)
    del profiles[name]
    _save_profiles(profiles)
    print(f"Deleted profile '{name}'.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python monitor.py {show|save|list|apply|delete} [name]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "show":
        cmd_show()
    elif cmd == "save":
        if len(sys.argv) < 3:
            print("Usage: python monitor.py save <name>")
            sys.exit(1)
        cmd_save(sys.argv[2])
    elif cmd == "list":
        cmd_list()
    elif cmd == "apply":
        if len(sys.argv) < 3:
            print("Usage: python monitor.py apply <name>")
            sys.exit(1)
        cmd_apply(sys.argv[2])
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: python monitor.py delete <name>")
            sys.exit(1)
        cmd_delete(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
