"""Make Right Alt act as the Left Windows key (Windows only, stdlib only, no admin).

Installs a per-user low-level keyboard hook. Right Alt events are swallowed and
replaced by Left Win events, so taps open Start and combos like RAlt+E work.
Press Ctrl+C in the console (or end pythonw.exe) to stop; nothing persists.
"""
import ctypes
import sys
from ctypes import wintypes

if sys.platform != "win32":
    sys.exit("winkey.py only works on Windows")

WH_KEYBOARD_LL = 13
VK_RMENU = 0xA5  # Right Alt
VK_LWIN = 0x5B
LLKHF_UP = 0x80
LLKHF_INJECTED = 0x10
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x1
KEYEVENTF_KEYUP = 0x2
QS_ALLINPUT = 0x04FF
PM_REMOVE = 1

ULONG_PTR = ctypes.c_size_t
LRESULT = ctypes.c_ssize_t


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]

    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.CallNextHookEx.restype = LRESULT
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
user32.MsgWaitForMultipleObjects.argtypes = [wintypes.DWORD, ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD, wintypes.DWORD]
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE

hook_handle = None


def send_lwin(key_up):
    flags = KEYEVENTF_EXTENDEDKEY | (KEYEVENTF_KEYUP if key_up else 0)
    inp = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=VK_LWIN, dwFlags=flags))
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def low_level_proc(n_code, w_param, l_param):
    if n_code >= 0:
        kb = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        if kb.vkCode == VK_RMENU and not kb.flags & LLKHF_INJECTED:
            send_lwin(bool(kb.flags & LLKHF_UP))
            return 1  # swallow the original Right Alt event
    return user32.CallNextHookEx(hook_handle, n_code, w_param, l_param)


# Keep a module-level reference so the callback is not garbage collected.
callback = HOOKPROC(low_level_proc)


def main():
    global hook_handle
    hook_handle = user32.SetWindowsHookExW(
        WH_KEYBOARD_LL, callback, kernel32.GetModuleHandleW(None), 0
    )
    if not hook_handle:
        sys.exit(f"SetWindowsHookEx failed: {ctypes.get_last_error()}")
    print("Right Alt now acts as the Windows key. Ctrl+C to stop.")
    msg = wintypes.MSG()
    try:
        while True:
            # Wake on any message (hook callbacks run while we pump) but time out
            # periodically so Ctrl+C can interrupt.
            user32.MsgWaitForMultipleObjects(0, None, False, 200, QS_ALLINPUT)
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWindowsHookEx(hook_handle)


if __name__ == "__main__":
    main()
