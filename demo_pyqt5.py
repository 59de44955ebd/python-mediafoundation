import os
import sys

from PyQt5 import QtWidgets, QtGui, QtCore

from mfplayer import *

INITIAL_VOLUME = 50
POSITION_UPDATE_TIME_MS = 200
DOUBLE_CLICK_MS = user32.GetDoubleClickTime()
TIMER_ID_CLICK = 1000


class MySlider(QtWidgets.QSlider):
    """ A horizontal slider that jumps to clicked position
    """

    def mousePressEvent (self, event):
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        sr = self.style().subControlRect(QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderHandle, self)
        self.is_pressed_outside = event.button() == QtCore.Qt.LeftButton and not sr.contains(event.pos())
        if self.is_pressed_outside:
            self.sliderPressed.emit()
            val = int(self.minimum() + ((self.maximum() - self.minimum()) * event.x()) / self.width())
            self.setValue(val)
            self.sliderMoved.emit(val)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_pressed_outside:
            val = int(self.minimum() + ((self.maximum() - self.minimum()) * event.x()) / self.width())
            self.setValue(val)
            self.sliderMoved.emit(val)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent (self, event):
        if self.is_pressed_outside:
            self.sliderReleased.emit()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.sliderMoved.emit(self.value())


class Main(QtWidgets.QMainWindow):
    """A simple media player using Media Foundation and PyQt5
    """

    def __init__(self):
        self.media_duration = 0

        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Media Player")
        self.setAcceptDrops(True)

        self.create_ui()

        ########################################
        #
        ########################################
        def _on_file_loaded(ok):
            if ok:
                self.media_duration = self.mediaplayer.get_duration()
                self.play_pause()
                self.setWindowTitle(os.path.basename(self.media_file))
                # media_duration would be 0 e.g. for HLS livestreams, where seeking is impossible
                self.slider_position.setEnabled(self.media_duration > 0)

        ########################################
        #
        ########################################
        def _on_end_reached():
            self.timer.stop()
            self.stop()

        self.mediaplayer = Player(
            self.hwnd_video_frame,
            volume = INITIAL_VOLUME / 100,
            on_file_loaded = _on_file_loaded,
            on_end_reached = _on_end_reached,
        )

        ########################################
        #
        ########################################
        def _on_scrub_start():
            self.mediaplayer.scrub_start()
            if self.mediaplayer.is_playing():
                self.timer.stop()

        self.slider_position.sliderPressed.connect(_on_scrub_start)

        ########################################
        #
        ########################################
        def _on_scrub_stop():
            pos = self.slider_position.value()
            self.mediaplayer.scrub_stop(self.media_duration * pos / 2000.0)
            if self.mediaplayer.is_playing():
                self.timer.start()

        self.slider_position.sliderReleased.connect(_on_scrub_stop)

        self.resize(640, 480)
        self.show()

        # Timer for updating the position slider when player is playing
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(POSITION_UPDATE_TIME_MS)
        self.timer.timeout.connect(self.update_ui)

        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])

    def dragEnterEvent (self, e):
        if e.mimeData().hasUrls():
            e.accept()

    def dropEvent (self, e):
        self.load_file(e.mimeData().urls()[0].toLocalFile())

    def create_ui(self):
        """Set up the user interface
        """
        file_menu = self.menuBar().addMenu("File")
        action = file_menu.addAction("&Open File")
        action.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        action.triggered.connect(self.open_file)

        action = file_menu.addAction("&Close File")
        action.setShortcut(QtGui.QKeySequence("Ctrl+W"))
        action.triggered.connect(self.close_file)

        file_menu.addSeparator()

        action = file_menu.addAction("&Properties")
        action.setShortcut(QtGui.QKeySequence("Ctrl+I"))
        action.triggered.connect(self.show_properties)

        file_menu.addSeparator()

        action = file_menu.addAction("E&xit")
        action.triggered.connect(self.close)

        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        vboxlayout = QtWidgets.QVBoxLayout()
        vboxlayout.setContentsMargins(0, 0, 0, 0)

        ########################################
        #
        ########################################
        def _window_proc_callback(hwnd, msg, wparam, lparam):
            if msg == WM_LBUTTONDOWN:
                if self.mediaplayer.has_media():
                    user32.SetTimer(hwnd, TIMER_ID_CLICK, DOUBLE_CLICK_MS, 0)

            elif msg == WM_LBUTTONDBLCLK:
                user32.KillTimer(hwnd, TIMER_ID_CLICK)
                if self.mediaplayer.has_video():
                    if self.video_frame.isFullScreen():
                        self.widget.layout().insertWidget(0, self.video_frame)
                        self.setVisible(True)
                    else:
                        self.video_frame.setParent(None)
                        self.video_frame.showFullScreen()
                        self.setVisible(False)

            elif msg == WM_TIMER:
                user32.KillTimer(hwnd, TIMER_ID_CLICK)
                self.play_pause()

            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.windowproc
        newclass.lpszClassName = "VideoFrame"
        newclass.hbrBackground = gdi32.GetStockObject(BLACK_BRUSH)
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        newclass.style = CS_DBLCLKS
        user32.RegisterClassExW(byref(newclass))

        self.hwnd_video_frame = user32.CreateWindowExW(
            0,
            newclass.lpszClassName,
            "VideoFrame",
            WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            int(self.winId()),
            None, None, 0
        )

        self.video_frame = QtWidgets.QWidget.createWindowContainer(QtGui.QWindow.fromWinId(self.hwnd_video_frame), flags=QtCore.Qt.MSWindowsOwnDC)
        vboxlayout.addWidget(self.video_frame)

        self.slider_position = MySlider(QtCore.Qt.Horizontal, self)
        self.slider_position.setToolTip("Position")
        self.slider_position.setMaximum(2000)
        self.slider_position.sliderMoved.connect(self.set_position)
        self.slider_position.setEnabled(False)

        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.setContentsMargins(10, 0, 10, 0)
        hboxlayout.addWidget(self.slider_position)
        vboxlayout.addLayout(hboxlayout)

        hboxlayout = QtWidgets.QHBoxLayout()
        hboxlayout.setContentsMargins(10, 5, 10, 10)

        self.button_play = QtWidgets.QPushButton("Play")
        hboxlayout.addWidget(self.button_play)
        self.button_play.clicked.connect(self.play_pause)

        self.button_stop = QtWidgets.QPushButton("Stop")
        hboxlayout.addWidget(self.button_stop)
        self.button_stop.clicked.connect(self.stop)

        hboxlayout.addStretch(1)

        self.slider_volume = MySlider(QtCore.Qt.Horizontal, self)
        hboxlayout.addWidget(self.slider_volume)
        self.slider_volume.setMinimumWidth(50)
        self.slider_volume.setMaximum(100)
        self.slider_volume.setValue(INITIAL_VOLUME)
        self.slider_volume.setToolTip("Volume")
        self.slider_volume.sliderMoved.connect(self.set_volume)

        vboxlayout.addLayout(hboxlayout)
        self.widget.setLayout(vboxlayout)

    def show_properties(self):
        """Show metadata in message box
        """
        if not self.mediaplayer.has_media():
            return
        data = self.mediaplayer.get_media_infos()
        text = ''
        for k, v in sorted(data.items()):
            text += f'{k} : {v}\n'
        QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'Properties', text[:-1], parent=self).exec()

    def play_pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.button_play.setText("Play")
            if self.media_duration > 0:
                self.timer.stop()
        else:
            if not self.mediaplayer.has_media():
                return self.open_file()
            self.mediaplayer.play()
            self.button_play.setText("Pause")
            if self.media_duration > 0:
                self.timer.start()

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        if self.media_duration > 0:
            self.timer.stop()
            self.slider_position.setValue(0)
        self.button_play.setText("Play")

    def open_file(self):
        """Select and load media file
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Media File")
        if not filename:
            return
        self.load_file(filename)

    def load_file(self, filename):
        """Load media file into player
        """
        if self.mediaplayer.has_media():
            self.close_file()
        self.mediaplayer.load_media_file(filename)
        self.media_file = filename

    def close_file(self):
        """Close/unload current media file
        """
        self.stop()
        self.mediaplayer.close_file()
        self.slider_position.setEnabled(False)
        self.setWindowTitle("Media Player")

    def set_volume(self, volume):
        """Set the volume
        """
        self.mediaplayer.set_volume(volume / 100)

    def set_position(self, pos):
        """Set the media time according to the time slider.
        """
        self.mediaplayer.set_time(self.media_duration * pos / 2000.0)

    def update_ui(self):
        """Update the time slider according to the current media time.
        """
        val = int(self.mediaplayer.get_time() / self.media_duration * 2000)
        self.slider_position.setValue(val)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec())
