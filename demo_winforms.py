import os
import sys

import clr
import System
clr.AddReference('System.Windows.Forms')
from System.Threading import Thread, ThreadStart, ApartmentState
import System.Windows.Forms as WinForms
from System.Drawing import Color, Size

from mfplayer import *

INITIAL_VOLUME = 50
POSITION_UPDATE_TIME_MS = 200
DOUBLE_CLICK_MS = user32.GetDoubleClickTime()


class Main(WinForms.Form):
    """A simple media player using Media Foundation and Windows Forms
    """

    def __init__(self):
        self.is_fullscreen = False
        self.media_duration = 0

        super().__init__()

        self.Text = "Media Player"
        self.Size = Size(654, 517)
        self.MinimumSize = Size(320, 129)
        self.StartPosition = WinForms.FormStartPosition.CenterScreen

        self.create_ui()
        self.AllowDrop = True

        ########################################
        #
        ########################################
        def _on_drag(sender, args):
            args.Effect = WinForms.DragDropEffects.Copy

        self.DragEnter += _on_drag

        ########################################
        #
        ########################################
        def _on_drop(sender, args):
            if args.Data.GetDataPresent(WinForms.DataFormats.FileDrop):
                files = args.Data.GetData(WinForms.DataFormats.FileDrop)
                self.load_file(files[0])

        self.DragDrop += _on_drop

        ########################################
        #
        ########################################
        def _on_file_loaded(ok):
            if ok:
                self.media_duration = self.mediaplayer.get_duration()
                self.play_pause()
                self.Text = os.path.basename(self.media_file)
                # media_duration would be 0 e.g. for HLS livestreams, where seeking is impossible
                self.trackbar_position.Enabled = self.media_duration > 0

        ########################################
        #
        ########################################
        def _on_end_reached():
            self.timer_position.Stop()
            self.stop()

        # Create media player
        self.mediaplayer = Player(
            self.video_frame.Handle.ToInt32(),
            volume = INITIAL_VOLUME / 100,
            on_file_loaded = _on_file_loaded,
            on_end_reached = _on_end_reached,
        )

        ########################################
        #
        ########################################
        def _on_click(sender, args):
            if self.mediaplayer.has_media():
                self.timer_click.Start()

        self.video_frame.Click += _on_click

        ########################################
        #
        ########################################
        def _on_dblclick(sender, args):
            self.timer_click.Stop()
            if not self.mediaplayer.has_video():
                return
            self.is_fullscreen = not self.is_fullscreen
            hwnd_video_frame = self.video_frame.Handle.ToInt32()
            if self.is_fullscreen:
                rc = RECT()
                user32.GetWindowRect(user32.GetDesktopWindow(), byref(rc))
                user32.SetParent(hwnd_video_frame, None)
                self.video_frame.Dock = getattr(WinForms.DockStyle, 'None')
                user32.SetWindowPos(hwnd_video_frame, HWND_TOPMOST, 0, 0, rc.right, rc.bottom, 0)
            else:
                user32.SetParent(hwnd_video_frame, self.Handle.ToInt32())
                self.video_frame.Dock = WinForms.DockStyle.Fill

        self.video_frame.DoubleClick += _on_dblclick

        # Timer for updating the position slider when player is playing
        self.timer_position = WinForms.Timer()
        self.timer_position.Interval = POSITION_UPDATE_TIME_MS
        self.timer_position.Tick += self.update_ui

        # Timer for distinguishing single and double clicks
        self.timer_click = WinForms.Timer()
        self.timer_click.Interval = DOUBLE_CLICK_MS
        self.timer_click.Tick += self.play_pause

        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])

    def create_ui(self):
        """Set up the user interface
        """
        self.SuspendLayout()

        self.Menu = WinForms.MainMenu()
        m = WinForms.MenuItem('&File')
        self.Menu.MenuItems.Add(m)

        action_item = WinForms.MenuItem('&Open File')
        action_item.Shortcut = WinForms.Shortcut.CtrlO
        action_item.Click += self.open_file
        m.MenuItems.Add(action_item)

        action_item = WinForms.MenuItem('&Close File')
        action_item.Shortcut = WinForms.Shortcut.CtrlW
        action_item.Click += self.close_file
        m.MenuItems.Add(action_item)

        m.MenuItems.Add(WinForms.MenuItem('-'))

        action_item = WinForms.MenuItem('&Properties')
        action_item.Shortcut = WinForms.Shortcut.CtrlI
        action_item.Click += self.show_properties
        m.MenuItems.Add(action_item)

        m.MenuItems.Add(WinForms.MenuItem('-'))

        action_item = WinForms.MenuItem('E&xit')
        action_item.Click += self.quit
        m.MenuItems.Add(action_item)

        self.video_frame = WinForms.UserControl()
        self.video_frame.BackColor = Color.Black
        self.video_frame.Dock = WinForms.DockStyle.Fill
        self.Controls.Add(self.video_frame)

        self.panel = WinForms.TableLayoutPanel()
        self.panel.Padding = WinForms.Padding(7, 0, 7, 0)
        self.panel.Height = 70
        self.panel.Dock = WinForms.DockStyle.Bottom
        self.panel.ColumnCount = 3
        self.panel.RowCount = 2
        self.Controls.Add(self.panel)

        self.trackbar_position = WinForms.TrackBar()
        self.trackbar_position.Maximum = 2000
        self.trackbar_position.Dock = WinForms.DockStyle.Bottom
        self.trackbar_position.AutoSize = False
        self.trackbar_position.Height = 30
        self.trackbar_position.TickStyle = getattr(WinForms.TickStyle, 'None')
        self.trackbar_position.Anchor = WinForms.AnchorStyles.Left | WinForms.AnchorStyles.Top | WinForms.AnchorStyles.Right
        self.trackbar_position.Enabled = False
        self.panel.Controls.Add(self.trackbar_position, 0, 0)
        self.panel.SetColumnSpan(self.trackbar_position, 3)
        self.trackbar_position.Scroll += lambda sender, args: self.set_position(self.trackbar_position.Value)

        ########################################
        #
        ########################################
        def _on_scrub_start(sender, args):
            self.mediaplayer.scrub_start()
            if self.mediaplayer.is_playing():
                self.timer_position.Stop()
            w = self.trackbar_position.Width - 28
            x = args.X - 14
            pos = max(0, min(2000, int(x / w * 2000)))
            self.trackbar_position.Value = pos
            self.set_position(pos)

        self.trackbar_position.MouseDown += _on_scrub_start

        ########################################
        #
        ########################################
        def _on_scrub_stop(sender, args):
            pos = self.trackbar_position.Value
            self.mediaplayer.scrub_stop(self.media_duration * pos / 2000.0)
            if self.mediaplayer.is_playing():
                self.timer_position.Start()

        self.trackbar_position.MouseUp += _on_scrub_stop

        self.button_play = WinForms.Button()
        self.button_play.Text = "Play"
        self.button_play.Anchor = WinForms.AnchorStyles.Left | WinForms.AnchorStyles.Top
        self.panel.Controls.Add(self.button_play, 0, 1)
        self.button_play.Click += self.play_pause

        self.button_stop = WinForms.Button()
        self.button_stop.Text = "Stop"
        self.button_stop.Anchor = WinForms.AnchorStyles.Left | WinForms.AnchorStyles.Top
        self.panel.Controls.Add(self.button_stop, 1, 1)
        self.button_stop.Click += self.stop

        self.trackbar_volume = WinForms.TrackBar()
        self.trackbar_volume.Maximum = 100
        self.trackbar_volume.Anchor = WinForms.AnchorStyles.Right | WinForms.AnchorStyles.Top
        self.trackbar_volume.AutoSize = False
        self.trackbar_volume.Height = 20
        self.trackbar_volume.TickStyle = getattr(WinForms.TickStyle, 'None')
        self.trackbar_volume.Value = INITIAL_VOLUME
        self.panel.Controls.Add(self.trackbar_volume, 2, 1)
        self.trackbar_volume.Scroll += lambda *_: self.set_volume(self.trackbar_volume.Value)

        ########################################
        #
        ########################################
        def _on_click(sender, args):
            w = self.trackbar_volume.Width - 28
            x = args.X - 14
            pos = max(0, min(100, int(x / w * 100)))
            self.trackbar_volume.Value = pos
            self.set_volume(pos)

        self.trackbar_volume.MouseDown += _on_click

        self.ResumeLayout(False)
        self.PerformLayout()

    def show_properties(self, *_):
        """Show metadata in message box
        """
        if not self.mediaplayer.has_media():
            return
        data = self.mediaplayer.get_media_infos()
        text = ''
        for k, v in sorted(data.items()):
            text += f'{k} : {v}\n'
        WinForms.MessageBox.Show(text[:-1], 'Properties', WinForms.MessageBoxButtons.OK, getattr(WinForms.MessageBoxIcon, 'None'))

    def open_file(self, *_):
        """Select and load media file
        """
        ofd = WinForms.OpenFileDialog()
        ofd.Filter = "All Files (*.*)|*.*"
        ofd.RestoreDirectory = True
        if ofd.ShowDialog() != WinForms.DialogResult.OK:
            return
        self.load_file(ofd.FileName)

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
        self.trackbar_position.Enabled = False
        self.Text = "Media Player"

    def play_pause(self, *_):
        """Toggle play/pause status
        """
        self.timer_click.Stop()
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.button_play.Text = "Play"
            if self.media_duration > 0:
                self.timer_position.Stop()
        else:
            if not self.mediaplayer.has_media():
                return self.open_file()
            self.mediaplayer.play()
            self.button_play.Text = "Pause"
            if self.media_duration > 0:
                self.timer_position.Start()

    def stop(self, *_):
        """Stop player
        """
        self.mediaplayer.stop()
        self.timer_position.Stop()
        self.button_play.Text = "Play"
        self.trackbar_position.Value = 0

    def quit(self, *_):
        WinForms.Application.Exit()

    def set_volume(self, volume):
        """Set the volume
        """
        self.mediaplayer.set_volume(volume / 100)

    def set_position(self, pos):
        """Set the media time according to the time slider
        """
        self.mediaplayer.set_time(self.media_duration * pos / 2000.0)

    def update_ui(self, *_):
        """Update the time slider according to the current media time.
        """
        val = int(self.mediaplayer.get_time() / self.media_duration * 2000)
        self.trackbar_position.Value = val


def app_thread():
    main = Main()
    WinForms.Application.Run(main)
    main.Dispose()

if __name__ == "__main__":
    thread = Thread(ThreadStart(app_thread))
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()
    thread.Join()
