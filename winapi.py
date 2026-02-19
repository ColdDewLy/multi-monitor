"""Win32 API structs, constants, and function wrappers for display configuration."""
import ctypes
from ctypes import wintypes

# --- Constants ---
ENUM_CURRENT_SETTINGS = -1

DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

QDC_ONLY_ACTIVE_PATHS = 0x00000002
DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME = 2
DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME = 1

# SetDisplayConfig flags
SDC_APPLY = 0x00000080
SDC_USE_SUPPLIED_DISPLAY_CONFIG = 0x00000020
SDC_SAVE_TO_DATABASE = 0x00000200
SDC_ALLOW_CHANGES = 0x00000400
SDC_NO_OPTIMIZATION = 0x00000100

# --- Legacy API Structs ---

class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cb = ctypes.sizeof(self)


class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPositionX", wintypes.LONG),
        ("dmPositionY", wintypes.LONG),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * 32),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dmSize = ctypes.sizeof(self)


# --- CCD API Structs ---

class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]


class DISPLAYCONFIG_PATH_SOURCE_INFO(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", wintypes.UINT),
        ("modeInfoIdx", wintypes.UINT),
        ("statusFlags", wintypes.UINT),
    ]


class DISPLAYCONFIG_PATH_TARGET_INFO(ctypes.Structure):
    _fields_ = [
        ("adapterId", LUID),
        ("id", wintypes.UINT),
        ("modeInfoIdx", wintypes.UINT),
        ("outputTechnology", wintypes.UINT),
        ("rotation", wintypes.UINT),
        ("scaling", wintypes.UINT),
        ("refreshRate_numerator", wintypes.UINT),
        ("refreshRate_denominator", wintypes.UINT),
        ("scanLineOrdering", wintypes.UINT),
        ("targetAvailable", wintypes.BOOL),
        ("statusFlags", wintypes.UINT),
    ]


class DISPLAYCONFIG_PATH_INFO(ctypes.Structure):
    _fields_ = [
        ("sourceInfo", DISPLAYCONFIG_PATH_SOURCE_INFO),
        ("targetInfo", DISPLAYCONFIG_PATH_TARGET_INFO),
        ("flags", wintypes.UINT),
    ]


class DISPLAYCONFIG_MODE_INFO(ctypes.Structure):
    _fields_ = [
        ("infoType", wintypes.UINT),
        ("id", wintypes.UINT),
        ("adapterId", LUID),
        ("data", ctypes.c_byte * 64),
    ]


class DISPLAYCONFIG_DEVICE_INFO_HEADER(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.UINT),
        ("size", wintypes.UINT),
        ("adapterId", LUID),
        ("id", wintypes.UINT),
    ]


class DISPLAYCONFIG_TARGET_DEVICE_NAME(ctypes.Structure):
    _fields_ = [
        ("header", DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ("flags", wintypes.UINT),
        ("outputTechnology", wintypes.UINT),
        ("edidManufactureId", wintypes.USHORT),
        ("edidProductCodeId", wintypes.USHORT),
        ("connectorInstance", wintypes.UINT),
        ("monitorFriendlyDeviceName", wintypes.WCHAR * 64),
        ("monitorDevicePath", wintypes.WCHAR * 128),
    ]


class DISPLAYCONFIG_SOURCE_DEVICE_NAME(ctypes.Structure):
    _fields_ = [
        ("header", DISPLAYCONFIG_DEVICE_INFO_HEADER),
        ("viewGdiDeviceName", wintypes.WCHAR * 32),
    ]


# --- Function Prototypes ---

user32 = ctypes.windll.user32

user32.EnumDisplayDevicesW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DISPLAY_DEVICEW), wintypes.DWORD]
user32.EnumDisplayDevicesW.restype = wintypes.BOOL

user32.EnumDisplaySettingsExW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
user32.EnumDisplaySettingsExW.restype = wintypes.BOOL

user32.GetDisplayConfigBufferSizes.argtypes = [wintypes.UINT, ctypes.POINTER(wintypes.UINT), ctypes.POINTER(wintypes.UINT)]
user32.GetDisplayConfigBufferSizes.restype = wintypes.LONG

user32.QueryDisplayConfig.argtypes = [wintypes.UINT, ctypes.POINTER(wintypes.UINT), ctypes.c_void_p, ctypes.POINTER(wintypes.UINT), ctypes.c_void_p, ctypes.c_void_p]
user32.QueryDisplayConfig.restype = wintypes.LONG

user32.SetDisplayConfig.argtypes = [wintypes.UINT, ctypes.c_void_p, wintypes.UINT, ctypes.c_void_p, wintypes.UINT]
user32.SetDisplayConfig.restype = wintypes.LONG

user32.DisplayConfigGetDeviceInfo.argtypes = [ctypes.c_void_p]
user32.DisplayConfigGetDeviceInfo.restype = wintypes.LONG


# --- Functions ---

def enum_display_devices(index, flags=0):
    dev = DISPLAY_DEVICEW()
    if user32.EnumDisplayDevicesW(None, index, ctypes.byref(dev), flags):
        return dev
    return None


def get_display_settings(device_name, mode=ENUM_CURRENT_SETTINGS):
    dm = DEVMODEW()
    if user32.EnumDisplaySettingsExW(device_name, mode, ctypes.byref(dm), 0):
        return dm
    return None


def query_display_config():
    """Query active display config. Returns (paths_array, modes_array, num_paths, num_modes) or None."""
    num_paths = wintypes.UINT()
    num_modes = wintypes.UINT()
    ret = user32.GetDisplayConfigBufferSizes(QDC_ONLY_ACTIVE_PATHS, ctypes.byref(num_paths), ctypes.byref(num_modes))
    if ret != 0:
        return None
    paths = (DISPLAYCONFIG_PATH_INFO * num_paths.value)()
    modes = (DISPLAYCONFIG_MODE_INFO * num_modes.value)()
    ret = user32.QueryDisplayConfig(QDC_ONLY_ACTIVE_PATHS, ctypes.byref(num_paths), paths, ctypes.byref(num_modes), modes, None)
    if ret != 0:
        return None
    return paths, modes, num_paths.value, num_modes.value


def set_display_config(paths, num_paths, modes, num_modes, flags):
    """Apply display configuration. Returns 0 on success."""
    return user32.SetDisplayConfig(num_paths, paths, num_modes, modes, flags)


def get_target_name(adapter_id, target_id):
    name = DISPLAYCONFIG_TARGET_DEVICE_NAME()
    name.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME
    name.header.size = ctypes.sizeof(name)
    name.header.adapterId = adapter_id
    name.header.id = target_id
    if user32.DisplayConfigGetDeviceInfo(ctypes.byref(name)) != 0:
        return None
    return name


def get_source_name(adapter_id, source_id):
    name = DISPLAYCONFIG_SOURCE_DEVICE_NAME()
    name.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME
    name.header.size = ctypes.sizeof(name)
    name.header.adapterId = adapter_id
    name.header.id = source_id
    if user32.DisplayConfigGetDeviceInfo(ctypes.byref(name)) != 0:
        return None
    return name
