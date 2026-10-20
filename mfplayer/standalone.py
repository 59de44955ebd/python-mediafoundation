import os
import sys

from . import *

DOUBLE_CLICK_MS = user32.GetDoubleClickTime()
TIMER_ID_CLICK = 1000


class Main():

    def __init__(
        self,
        resize_to_video = True,
        x = CW_USEDEFAULT, y = CW_USEDEFAULT, cx = CW_USEDEFAULT, cy =CW_USEDEFAULT
    ):

        ########################################
        #
        ########################################
        def _window_proc_callback(hwnd, msg, wparam, lparam):
            if msg == WM_CLOSE:
                user32.PostQuitMessage(0)

            elif msg == WM_TIMER:
                user32.KillTimer(hwnd, TIMER_ID_CLICK)
                self.play_pause()

            elif msg == WM_DROPFILES:
                cnt = shell32.DragQueryFileW(wparam, 0xFFFFFFFF, None, 0)
                file_buffer = create_unicode_buffer(MAX_PATH)
                shell32.DragQueryFileW(wparam, 0, file_buffer, MAX_PATH)
                shell32.DragFinish(wparam)
                self.media_file = file_buffer[:].split('\0', 1)[0]
                self.mediaplayer.load_media_file(self.media_file)

            elif msg == WM_MOUSEWHEEL:
                self.mediaplayer.set_volume(self.mediaplayer.get_volume() + SHORT((wparam >> 16) & 0xFFFF).value / 120 * .05)

            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.windowproc
        newclass.lpszClassName = "MediaPlayer"
        newclass.hbrBackground = gdi32.GetStockObject(BLACK_BRUSH)
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        newclass.style = CS_DBLCLKS  # | CS_VREDRAW | CS_HREDRAW
        user32.RegisterClassExW(byref(newclass))

        self.hwnd = user32.CreateWindowExW(
            WS_EX_ACCEPTFILES,
            newclass.lpszClassName,
            "Media Player - Drop media file into window",
            WS_OVERLAPPEDWINDOW,
            x, y, cx, cy,
            0, None, None, 0
        )

        windll.dwmapi.DwmSetWindowAttribute(self.hwnd, 20, byref(c_int(1)), sizeof(c_int))

        ########################################
        #
        ########################################
        def _on_file_loaded(ok):
            if ok:
                if resize_to_video and self.mediaplayer.has_video():
                    w, h = self.mediaplayer.get_size()
                    rc_win, rc_client = RECT(), RECT()
                    user32.GetWindowRect(self.hwnd, byref(rc_win))
                    user32.GetClientRect(self.hwnd, byref(rc_client))
                    ui_width = rc_win.right - rc_win.left - rc_client.right
                    ui_height = rc_win.bottom - rc_win.top - rc_client.bottom
                    user32.SetWindowPos(self.hwnd, 0, 0, 0, w + ui_width, h + ui_height, SWP_NOMOVE)

                self.play_pause()
                user32.SetWindowTextW(self.hwnd, os.path.basename(self.media_file))
            else:
                print(f"Error: failed to load {self.media_file}", file=sys.stderr)

        self.mediaplayer = Player(
            self.hwnd,
            volume = .75,
            on_file_loaded = _on_file_loaded,
        )

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDOWN(hwnd, wparam, lparam):
            if self.mediaplayer.has_media():
                user32.SetTimer(self.hwnd, TIMER_ID_CLICK, DOUBLE_CLICK_MS, 0)

        self.mediaplayer.register_message_callback(WM_LBUTTONDOWN, _on_WM_LBUTTONDOWN)

        ########################################
        #
        ########################################
        def _on_WM_LBUTTONDBLCLK(hwnd, wparam, lparam):
            user32.KillTimer(self.hwnd, TIMER_ID_CLICK)
            if not self.mediaplayer.has_video():
                return
            self.mediaplayer.set_fullscreen(not self.mediaplayer.is_fullscreen())

        self.mediaplayer.register_message_callback(WM_LBUTTONDBLCLK, _on_WM_LBUTTONDBLCLK)

        user32.ShowWindow(self.hwnd, SW_SHOWNORMAL)

    def load_file(self, filename):
        """Load media file into player
        """
        self.mediaplayer.load_media_file(filename)
        self.media_file = filename

    def run(self):
        msg = MSG()
        while user32.GetMessageW(byref(msg), None, 0, 0):
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        return 0

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
        else:
            self.mediaplayer.play()


if __name__ == "__main__":
    main = Main().run()
    if len(sys.argv) > 1:
        main.load_file(sys.argv[1])
    main.run()
