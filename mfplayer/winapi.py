from ctypes import *
from ctypes.wintypes import *

########################################
# Additional used Windows API types
########################################
LONG_PTR = c_longlong
ULONG_PTR = c_uint64
UINT_PTR = WPARAM
WNDPROC = WINFUNCTYPE(LONG_PTR, HWND, UINT, WPARAM, LPARAM)
MFTIME = c_int64 #c_longlong
LPFLOAT = POINTER(FLOAT)
SIZE_T = c_longlong

def LOWORD(l):
    return WORD(l & 0xFFFF).value

def HIWORD(l):
    return WORD((l >> 16) & 0xFFFF).value

########################################
# Used Windows API structs
########################################
class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]

class OPENFILENAMEW(Structure):
    def __init__(self, *args, **kwargs):
        super(OPENFILENAMEW, self).__init__(*args, **kwargs)
        self.lStructSize = sizeof(OPENFILENAMEW)
    _fields_ = (
        ("lStructSize", DWORD),
        ("hwndOwner", HWND),
        ("hInstance", HINSTANCE),
        ("lpstrFilter", LPWSTR),
        ("lpstrCustomFilter", LPWSTR),
        ("nMaxCustFilter", DWORD),
        ("nFilterIndex", DWORD),
        ("lpstrFile", LPWSTR),
        ("nMaxFile", DWORD),
        ("lpstrFileTitle", LPWSTR),
        ("nMaxFileTitle", DWORD),
        ("lpstrInitialDir", LPCWSTR),
        ("lpstrTitle", LPCWSTR),
        ("Flags", DWORD),
        ("nFileOffset", WORD),
        ("nFileExtension", WORD),
        ("lpstrDefExt", LPCWSTR),
        ("lCustData", LPARAM),
        ("lpfnHook", LPVOID),  # LPOFNHOOKPROC, not used
        ("lpTemplateName", LPCWSTR),
        ("pvReserved", LPVOID),
        ("dwReserved", DWORD),
        ("FlagsEx", DWORD),
    )

class WNDCLASSEXW(Structure):
    def __init__(self, *args, **kwargs):
        super(WNDCLASSEXW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", UINT),
        ("style", UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", INT),
        ("cbWndExtra", INT),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HANDLE)
    ]

class ACCEL(Structure):
    _fields_ = [
        ("fVirt", BYTE),
        ("key", WORD),
        ("cmd", WORD),
    ]

class PAINTSTRUCT(Structure):
    _fields_ = [
        ("hdc",            HDC),
        ("fErase",         BOOL),
        ("rcPaint",        RECT),
        ("fRestore",       BOOL),
        ("fIncUpdate",     BOOL),
        ("rgbReserved",    BYTE * 32),
    ]

class BITMAPINFOHEADER(Structure):
    def __init__(self, *args, **kwargs):
        super(BITMAPINFOHEADER, self).__init__(*args, **kwargs)
        self.biSize = sizeof(BITMAPINFOHEADER)
    _fields_ = [
            ('biSize', DWORD),
            ('biWidth', LONG),
            ('biHeight', LONG),
            ('biPlanes', WORD),
            ('biBitCount', WORD),
            ('biCompression', DWORD),
            ('biSizeImage', DWORD),
            ('biXPelsPerMeter', LONG),
            ('biYPelsPerMeter', LONG),
            ('biClrUsed', DWORD),
            ('biClrImportant', DWORD)
    ]

# Custom struct for writing BMP files
class BMPHEADER(Structure):
    _pack_ = 2
    _fields_ = [
        ('magic', SHORT),
        ('size', DWORD),
        ('reserved', DWORD),
        ('offset', DWORD),
    ]
    def __init__(self, *args, **kwargs):
        super(BMPHEADER, self).__init__(*args, **kwargs)
        self.magic = 0x4D42  # BM
        self.offset = sizeof(self) + sizeof(BITMAPINFOHEADER)

########################################
# Used Windows API functions
########################################
comdlg32 = windll.comdlg32
comdlg32.GetOpenFileNameW.argtypes = (POINTER(OPENFILENAMEW),)

gdi32 = windll.gdi32
gdi32.CreateFontW.argtypes = (INT, INT, INT, INT, INT, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, LPCWSTR)
gdi32.CreateFontW.restype = HFONT
gdi32.CreateSolidBrush.argtypes = (COLORREF,)
gdi32.CreateSolidBrush.restype = HBRUSH
gdi32.GetStockObject.restype = HANDLE

ole32 = windll.ole32
ole32.CoTaskMemFree.argtypes = (LPVOID,)

shell32 = windll.shell32
shell32.DragFinish.argtypes = (WPARAM,)
shell32.DragQueryFileW.argtypes = (WPARAM, UINT, LPWSTR, UINT)

user32 = windll.user32
user32.AppendMenuW.argtypes = (HWND, UINT, UINT_PTR, LPCWSTR)
user32.CreateAcceleratorTableW.argtypes = (LPVOID, INT)
user32.CreateAcceleratorTableW.restype = HACCEL
user32.CreateWindowExW.argtypes = (DWORD, LPCWSTR, LPCWSTR, DWORD, INT, INT, INT, INT, HWND, HMENU, HINSTANCE, LPVOID)
user32.DefWindowProcW.argtypes = (HWND, UINT, WPARAM, LPARAM)
user32.DispatchMessageW.argtypes = (LPMSG,)
user32.EnableWindow.argytpes = (HWND, BOOL)
user32.GetClientRect.argtypes = (HWND, LPRECT)
user32.GetDesktopWindow.restype = HWND
user32.GetMessageW.argtypes = (LPMSG, HWND, UINT, UINT)
user32.GetParent.argtypes = (HWND,)
user32.GetParent.restype = HWND
user32.GetWindowRect.argtypes = (HWND, LPRECT)
user32.InvalidateRect.argtypes = (HWND, LPRECT, BOOL)
user32.IsDialogMessageW.argtypes = (HWND, LPMSG)
user32.IsDialogMessageW.restype = BOOL
user32.MapWindowPoints.argtypes = (HWND, HWND, LPVOID, UINT)
user32.SendMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.SetParent.argtypes = (HWND, HWND)
user32.SetWindowLongPtrW.argtypes = (HWND, LONG_PTR, WNDPROC)
user32.SetWindowLongPtrW.restype = WNDPROC
user32.SetWindowPos.argtypes = (HWND, LONG_PTR, INT, INT, INT, INT, UINT)
user32.SetWindowTextW.argtypes = (HWND, LPCWSTR)
user32.TranslateAcceleratorW.argtypes = (HWND, HACCEL, LPMSG)
user32.TranslateMessage.argtypes = (LPMSG,)

winmm = windll.Winmm

########################################
# Used Windows API constants
########################################
ANSI_CHARSET = 0
BLACK_BRUSH = 4
BN_CLICKED = 0
CLIP_DEFAULT_PRECIS = 0
COLOR_3DFACE = 15
COLOR_WINDOW = 5
CS_DBLCLKS = 8
CS_HREDRAW = 2
CS_OWNDC = 32
CS_PARENTDC = 128
CS_VREDRAW = 1
CW_USEDEFAULT = -2147483648
DEFAULT_PITCH = 0
DEFAULT_QUALITY = 0
FALSE = 0
FALT = 16
FCONTROL = 8
FF_DONTCARE = 0
FSHIFT = 4
FW_DONTCARE = 0
GWL_STYLE = -16
GWL_WNDPROC = -4
HWND_TOPMOST = -1
IDC_ARROW = 32512
MAX_PATH = 260
MF_POPUP = 16
MF_SEPARATOR = 2048
MF_STRING = 0
OFN_ENABLESIZING = 8388608
OFN_PATHMUSTEXIST = 2048
OUT_TT_PRECIS = 4

SWP_NOSIZE = 1
SWP_NOMOVE = 2
SWP_NOZORDER = 4
SWP_NOREDRAW = 8
SWP_NOACTIVATE = 16
SWP_FRAMECHANGED = 32
SWP_SHOWWINDOW = 64
SWP_HIDEWINDOW = 128
SWP_NOCOPYBITS = 256
SWP_NOOWNERZORDER = 512
SWP_NOSENDCHANGING = 1024
SWP_DEFERERASE = 8192
SWP_ASYNCWINDOWPOS = 16384

SW_INVALIDATE = 2
SW_SHOWNORMAL = 1
SW_SHOWMAXIMIZED = 3

TBM_GETPOS = 1024
TBM_SETPAGESIZE = 1045
TBM_SETPOS = 1029
TBM_SETRANGE = 1030
TBM_SETRANGEMAX = 1032
TB_ENDTRACK = 8
TB_LINEDOWN	= 1
TB_LINEUP = 0
TB_PAGEDOWN = 3
TB_PAGEUP = 2
TB_THUMBPOSITION = 4
TRUE = 1
WC_BUTTON = "Button"
WC_TRACKBAR = "msctls_trackbar32"
WM_APP = 32768
WM_CLOSE = 16
WM_COMMAND = 273
WM_DROPFILES = 563
WM_EVENT_NOTIFY = WM_APP + 1
WM_GETMINMAXINFO = 36
WM_HSCROLL = 276
WM_LBUTTONDBLCLK = 515
WM_LBUTTONDOWN = 513
WM_LBUTTONUP = 514
WM_MOUSEWHEEL = 522
WM_PAINT = 15
WM_RBUTTONDBLCLK = 518
WM_RBUTTONDOWN = 516
WM_RBUTTONUP = 517
WM_SETFONT = 48
WM_SIZE = 5
WM_TIMER = 275
WS_CHILD = 1073741824
WS_CLIPCHILDREN = 33554432
WS_CLIPSIBLINGS = 67108864
WS_DISABLED = 134217728
WS_EX_ACCEPTFILES = 16
WS_OVERLAPPED = 0
WS_POPUP = -2147483648
WS_OVERLAPPEDWINDOW = 13565952
WS_VISIBLE = 268435456
