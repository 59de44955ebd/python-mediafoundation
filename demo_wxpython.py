import os
import sys

import wx

from mfplayer import *

INITIAL_VOLUME = 50
POSITION_UPDATE_TIME_MS = 200
DOUBLE_CLICK_MS = user32.GetDoubleClickTime()


class MySlider(wx.Slider):
    """ A horizontal slider that jumps to clicked position
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ########################################
        #
        ########################################
        def _on_mouse_down(event):
            pt = POINT()
            user32.GetCursorPos(byref(pt))
            hwnd = self.GetHandle()
            user32.MapWindowPoints(None, hwnd, byref(pt), 1)
            rc = RECT()
            user32.GetWindowRect(hwnd, byref(rc))
            v = int((pt.x - 10) / (rc.right - rc.left - 20) * self.GetMax())
            self.SetValue(v)
            event = wx.PyCommandEvent(wx.EVT_SCROLL_THUMBTRACK.typeId, self.GetId())
            self.GetEventHandler().ProcessEvent(event)

        self.Bind(wx.EVT_SCROLL_PAGEUP, _on_mouse_down, self)
        self.Bind(wx.EVT_SCROLL_PAGEDOWN, _on_mouse_down, self)


class Main(wx.Frame):
    """A simple media player using Media Foundation and wxPython
    """

    def __init__(self):
        self.is_fullscreen = False
        self.media_duration = 0

        super().__init__(
            None, -1, title="Media Player",
            pos=wx.DefaultPosition, size=(654, 517)
        )

        self.SetMinSize((320, 125))

        self.create_ui()

        ########################################
        #
        ########################################
        def _on_file_loaded(ok):
            if ok:
                self.media_duration = self.mediaplayer.get_duration()
                self.play_pause()
                self.SetTitle(os.path.basename(self.media_file))
                if self.media_duration > 0:
                    # media_duration would be 0 e.g. for HLS livestreams, where seeking is impossible
                    self.slider_position.Enable()

        ########################################
        #
        ########################################
        def _on_end_reached():
            self.timer_position.Stop()
            self.stop()

        # Create media player
        self.mediaplayer = Player(
            self.video_panel.GetHandle(),
            volume = INITIAL_VOLUME / 100,
            on_file_loaded = _on_file_loaded,
            on_end_reached = _on_end_reached,
        )

        ########################################
        #
        ########################################
        def _on_clicked(*_):
            if self.mediaplayer.has_media():
                self.timer_click.StartOnce(DOUBLE_CLICK_MS)

        self.video_panel.Bind(wx.EVT_LEFT_DOWN, _on_clicked)

        ########################################
        #
        ########################################
        def _on_double_clicked(*_):
            self.timer_click.Stop()
            if not self.mediaplayer.has_video():
                return
            self.is_fullscreen = not self.is_fullscreen
            if self.is_fullscreen:
                rc = RECT()
                user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc))
                hwnd_video_frame = self.video_panel.GetHandle()
                user32.SetParent(hwnd_video_frame, None)
                user32.SetWindowPos(hwnd_video_frame, HWND_TOPMOST, 0, 0, rc.right, rc.bottom, 0)
            else:
                user32.SetParent(self.video_panel.GetHandle(), self.GetHandle())
                self.Layout()

        self.video_panel.Bind(wx.EVT_LEFT_DCLICK, _on_double_clicked)

        # Timer for updating the position slider when player is playing
        self.timer_position = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_ui, self.timer_position)

        # Timer for distinguishing single and double clicks
        self.timer_click = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.play_pause, self.timer_click)

        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])
        else:
            self.slider_position.Disable()

        class FileDropTarget(wx.FileDropTarget):
            def OnDropFiles(me, x, y, filenames):
                self.load_file(filenames[0])
                return True

        self.SetDropTarget(FileDropTarget())

        self.Centre()
        self.Show()

    def create_ui(self):
        """Set up the user interface
        """
        # Menu Bar
        frame_menubar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(1, "&Open File\tCtrl+O")
        file_menu.Append(2, "&Close File\tCtrl+W")
        file_menu.AppendSeparator()
        file_menu.Append(3, "&Properties\tCtrl+I")
        file_menu.AppendSeparator()
        file_menu.Append(4, "E&xit")

        self.Bind(wx.EVT_MENU, self.open_file, id=1)
        self.Bind(wx.EVT_MENU, self.close_file, id=2)
        self.Bind(wx.EVT_MENU, self.show_properties, id=3)
        self.Bind(wx.EVT_MENU, lambda *_: self.Close(), id=4)

        frame_menubar.Append(file_menu, "&File")
        self.SetMenuBar(frame_menubar)

        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))

        sizer = wx.BoxSizer(wx.VERTICAL)

        # The first panel holds the video and it's all black
        self.video_panel = wx.Panel(self, -1)
        self.video_panel.SetBackgroundColour(wx.BLACK)
        sizer.Add(self.video_panel, 1, flag=wx.EXPAND, border=0)

        self.slider_position = MySlider(self, -1, 0, 0, 2000)
        sizer.Add(self.slider_position, flag=wx.EXPAND | wx.BOTTOM, border=0)

        sizer.AddSpacer(7)

        # The second panel holds controls
        ctrl_panel = wx.Panel(self, -1)
        ctrl_box = wx.BoxSizer(wx.HORIZONTAL)
        self.button_play = wx.Button(ctrl_panel, label="Play")
        self.button_stop = wx.Button(ctrl_panel, label="Stop")

        ctrl_box.AddSpacer(7)
        ctrl_box.Add(self.button_play, flag=wx.RIGHT, border=5)
        ctrl_box.Add(self.button_stop)
        ctrl_box.Add((-1, -1), 1)
        self.slider_volume = MySlider(ctrl_panel, -1, INITIAL_VOLUME, 0, 100, size=(100, -1))
        ctrl_box.Add(self.slider_volume, flag=wx.TOP | wx.LEFT)
        ctrl_panel.SetSizer(ctrl_box)
        sizer.Add(ctrl_panel, flag=wx.EXPAND | wx.BOTTOM)

        sizer.AddSpacer(7)

        # Bind controls to events
        self.button_play.Bind(wx.EVT_BUTTON, self.play_pause)
        self.button_stop.Bind(wx.EVT_BUTTON, self.stop)

        for e in (wx.EVT_SCROLL_THUMBTRACK, wx.EVT_SCROLL_LINEDOWN, wx.EVT_SCROLL_LINEUP):
            self.slider_position.Bind(e, lambda _: self.set_position(self.slider_position.GetValue()))
            self.slider_volume.Bind(e, lambda _: self.set_volume(self.slider_volume.GetValue()))

        ########################################
        #
        ########################################
        def _on_scrub_start(event):
            self.mediaplayer.scrub_start()
            if self.mediaplayer.is_playing():
                self.timer_position.Stop()
            event.Skip(True)

        self.slider_position.Bind(wx.EVT_LEFT_DOWN, _on_scrub_start)

        ########################################
        #
        ########################################
        def _on_scrub_stop(event):
            pos = self.slider_position.GetValue()
            self.mediaplayer.scrub_stop(self.media_duration * pos / 2000.0)
            if self.mediaplayer.is_playing():
                self.timer_position.Start(POSITION_UPDATE_TIME_MS)
            event.Skip(True)

        self.slider_position.Bind(wx.EVT_LEFT_UP, _on_scrub_stop)

        self.SetSizer(sizer)

    def show_properties(self, *_):
        """Show metadata in message box
        """
        if not self.mediaplayer.has_media():
            return
        data = self.mediaplayer.get_metadata()
        text = ''
        for k, v in sorted(data.items()):
            text += f'{k} : {v}\n'
        wx.MessageDialog(self, text[:-1], caption='Properties', style=wx.ICON_NONE | wx.OK).ShowModal()

    def play_pause(self, *_):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.button_play.Label = "Play"
            if self.media_duration > 0:
                self.timer_position.Stop()
        else:
            if not self.mediaplayer.has_media():
                return self.open_file()
            self.mediaplayer.play()
            self.button_play.Label = "Pause"
            if self.media_duration > 0:
                self.timer_position.Start(POSITION_UPDATE_TIME_MS)

    def stop(self, *_):
        """Stop the player.
        """
        self.mediaplayer.stop()
        self.button_play.Label = "Play"
        if self.media_duration > 0:
            self.timer_position.Stop()
            self.slider_position.SetValue(0)

    def open_file(self, *_):
        """Select and load media file
        """
        dlg = wx.FileDialog(self, "Choose a video file", "", "", "*.*", wx.FD_OPEN)
        filename = os.path.join(dlg.GetDirectory(), dlg.GetFilename()) if dlg.ShowModal() == wx.ID_OK else None
        dlg.Destroy()
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Load media file into player
        """
        if self.mediaplayer.has_media():
            self.close_file()
        self.mediaplayer.load_media_file(filename)
        self.media_file = filename

    def close_file(self, *_):
        """Close/unload current media file
        """
        self.stop()
        self.mediaplayer.close_file()
        self.slider_position.Disable()
        self.SetTitle("Media Player")

    def set_volume(self, pos):
        """Set the volume according to the volume sider.
        """
        self.mediaplayer.set_volume(pos / 100)

    def set_position(self, pos):
        """Set the media time according to the time slider
        """
        self.mediaplayer.set_time(self.media_duration * pos / 2000.0)

    def update_ui(self, evt):
        """Update the time slider according to the current media time.
        """
        val = int(self.mediaplayer.get_time() / self.media_duration * 2000)
        self.slider_position.SetValue(val)


if __name__ == "__main__":
    app = wx.App()
    main = Main()
    app.MainLoop()
