import os
import sys
from sysconfig import get_platform
import time
from .winapi import *

LPFLOAT = POINTER(FLOAT)
MFTIME = c_longlong
SIZE_T = c_longlong

if getattr(sys, 'frozen', False):
    dll_file = os.path.join(os.path.dirname(__file__), 'mfplayer.dll')
else:
    dll_file = os.path.join(os.path.dirname(__file__), 'native', get_platform(), 'mfplayer.dll')

_mf = CDLL(dll_file)
#STDAPI Init(HWND hVideo, HWND hEvent)
_mf.Init.argtypes = (HWND, HWND)
#STDAPI CloseFile()
#STDAPI GetAspectRatio(LPDWORD pRatio)
#STDAPI GetCapabilities(LPDWORD pCaps)
#STDAPI GetCharacteristics(LPDWORD pCaps)
#STDAPI GetCurrentImage(BITMAPINFOHEADER *pBih, BYTE **pDib, DWORD *pcbDib, LONGLONG *pTimeStamp)
_mf.GetCurrentImage.argtypes = (POINTER(BITMAPINFOHEADER), POINTER(LPBYTE), LPDWORD, POINTER(c_longlong))
#STDAPI GetDuration(UINT64 *pDur)
_mf.GetDuration.argtypes = (POINTER(MFTIME),)
#STDAPI GetFrameRate(float *pfRate)
_mf.GetFrameRate.argtypes = (LPFLOAT,)
#STDAPI GetMetadata(BYTE **pData, DWORD *pDataSize)
_mf.GetMetadata.argtypes = (POINTER(LPBYTE), LPDWORD)
#STDAPI GetMute(BOOL *pbMute)
#STDAPI GetRate(float *pfRate)
_mf.GetRate.argtypes = (LPFLOAT,)
#STDAPI GetSize(LPDWORD pSize)
_mf.GetSize.argtypes = (LPDWORD,)
#STDAPI GetState(LPINT pState)
#STDAPI GetStream(DWORD idx, LPDWORD pType, LPDWORD pFourCC, LPBOOL pSelected, LPWSTR lang, size_t lang_buf_size)
_mf.GetStream.argtypes = (DWORD, LPDWORD, LPDWORD, LPBOOL, LPWSTR, SIZE_T)
#STDAPI GetStreamCount(LPDWORD pCount)
_mf.GetStreamCount.argtypes = (LPDWORD,)
#STDAPI GetTime(MFTIME *pTime)
_mf.GetTime.argtypes = (POINTER(MFTIME),)
#STDAPI GetVolume(float *pfLevel)
#STDAPI HasAudio(LPBOOL pHasAudio)
_mf.HasAudio.argtypes = (LPBOOL,)
#STDAPI HasVideo(LPBOOL pHasVideo)
_mf.HasVideo.argtypes = (LPBOOL,)
#STDAPI LoadFile(LPCWSTR url)
_mf.LoadFile.argtpyes = (LPCWSTR,)
#STDAPI Pause()
#STDAPI Play()
#STDAPI Repaint()
#STDAPI ResizeVideo(WORD width, WORD height)
#STDAPI SelectAudioStream(DWORD idx)
#STDAPI SelectVideoStream(DWORD idx)
#STDAPI SetAspectRatioMode(DWORD mode)
#STDAPI SetFullscreen(BOOL fFullscreen)
#STDAPI SetMute(BOOL bMute)
#STDAPI SetProcAmpValue(DWORD dwProperty, float value)
_mf.SetProcAmpValue.argtypes = (DWORD, FLOAT)
#STDAPI SetRate(float rate)
_mf.SetRate.argtypes = (FLOAT,)
#STDAPI SetTime(MFTIME time)
_mf.SetTime.argtypes = (MFTIME,)
#STDAPI SetVideoRect(RECT rc)
#STDAPI SetVolume(float fLevel)
_mf.SetVolume.argtypes = (FLOAT,)
#STDAPI Shutdown()
#STDAPI Stop()

WM_APP_NOTIFY = WM_APP + 1

STATE_CLOSED = 0        # No session.
STATE_PLAYING = 1       # Session is playing a file.
STATE_PAUSED = 2        # Session is paused.
STATE_STOPPED = 3       # Session is stopped (ready to play).

SCRUB_NONE = 0
SCRUB_ACTIVE = 1
SCRUB_CLOSING = 2

# Events
class Event:
    MEUnknown = 0
    MEError = 1
    MEExtendedType = 2
    MENonFatalError = 3
    MESessionUnknown = 100
    MESessionTopologySet = 101
    MESessionTopologiesCleared = 102
    MESessionStarted = 103
    MESessionPaused = 104
    MESessionStopped = 105
    MESessionClosed = 106
    MESessionEnded = 107
    MESessionRateChanged = 108
    MESessionScrubSampleComplete = 109
    MESessionCapabilitiesChanged = 110
    MESessionTopologyStatus = 111
    MESessionNotifyPresentationTime = 112
    MENewPresentation = 113
    MELicenseAcquisitionStart = 114
    MELicenseAcquisitionCompleted = 115
    MEIndividualizationStart = 116
    MEIndividualizationCompleted = 117
    MEEnablerProgress = 118
    MEEnablerCompleted = 119
    MEPolicyError = 120
    MEPolicyReport = 121
    MEBufferingStarted = 122
    MEBufferingStopped = 123
    MEConnectStart = 124
    MEConnectEnd = 125
    MEReconnectStart = 126
    MEReconnectEnd = 127
    MERendererEvent = 128
    MESessionStreamSinkFormatChanged = 129
    MESourceUnknown = 200,
    MESourceStarted = 201
    MEStreamStarted = 202
    MESourceSeeked = 203
    MEStreamSeeked = 204
    MENewStream = 205
    MEUpdatedStream = 206
    MESourceStopped = 207
    MEStreamStopped = 208
    MESourcePaused = 209
    MEStreamPaused = 210
    MEEndOfPresentation = 211
    MEEndOfStream = 212
    MEMediaSample = 213
    MEStreamTick = 214
    MEStreamThinMode = 215
    MEStreamFormatChanged = 216
    MESourceRateChanged = 217
    MEEndOfPresentationSegment = 218
    MESourceCharacteristicsChanged = 219
    MESourceRateChangeRequested = 220
    MESourceMetadataChanged = 221

# For debugging reveived events
#DEBUG_EVENT_NAMES = {}
#for k, v in Event.__dict__.items():
#    if not k.startswith('_'):
#        DEBUG_EVENT_NAMES[v] = k

MF_TOPOSTATUS_READY = 100

MF_UNITS_PER_SEC = 10000000

# enum MFVideoAspectRatioMode
MFVideoARMode_None = 0
MFVideoARMode_PreservePicture = 0x1

DXVA2_ProcAmp_Brightness = 0x1
DXVA2_ProcAmp_Contrast = 0x2
DXVA2_ProcAmp_Hue = 0x4
DXVA2_ProcAmp_Saturation = 0x8

class PlayerException(Exception):
    pass

def _fourcc_to_str(four_cc):
    s = hex(int(four_cc))[2:]
    return ''.join([chr(int(s[i:i+2], 16)) for i in range(6, -2, -2)])

AUDIO_TYPES = {
    1:      'PCM',
    0x00FF: 'RAW AAC',
    0x1610: 'AAC',
    0x1600: 'ADTS',
    0x6C61: 'ALAC',
    0x0092: 'AC3 SPDIF',
    0xE06D802C: 'AC3',
    0x0009: 'DRM',
    0x0008: 'DTS',
    0xF1AC: 'FLAC',
    0x0003: 'IEEE FLOAT',
    0x0055: 'MP3',
    0x0050: 'MPEG',
    0x000A: 'MSP1',
    0x704F: 'OPUS',
    0x0164: 'WMA SPDIF',
    0x0163: 'WMA LOSSLESS',
    0x0161: 'WMA 2',
    0x0162: 'WMA 3',
}


########################################
#
########################################
class Player():

    ########################################
    #
    ########################################
    def __init__(
        self,
        hwnd: int,
        volume: float = .75,
        on_file_loaded = None,
        on_end_reached = None,
    ):
        self._hwnd = hwnd
        self._volume = volume

        self._listeners = {}
        self._message_map = {}
        self._new_proc = None
        self._old_proc = None

        self._loop = False
        self._fullscreen = False

        self._frame_step = 0
        self._has_media = False
        self._has_video = False
        self._is_track_update = False
        self._scrub_pending = False
        self._scrub_state = SCRUB_NONE
        self._state = STATE_CLOSED

        _mf.Init(hwnd, hwnd)

        ########################################
        #
        ########################################
        def _on_WM_APP_NOTIFY(hwnd, wparam, lparam):
            event_type, hr = wparam, lparam

            if event_type == Event.MESessionTopologyStatus:
                if hr == MF_TOPOSTATUS_READY:

                    hr = _mf.SetVolume(self._volume)

                    d = MFTIME()
                    hr = _mf.GetDuration(byref(d))
                    self._duration = d.value

                    flag = BOOL()
                    hr = _mf.HasVideo(byref(flag))
                    self._has_video = bool(flag.value)

                    if self._has_video:
                        fps = self._get_frame_rate()
                        if fps > 0:
                            self._frame_step = 1 / fps

                    if self._is_track_update:
                        self._is_track_update = False
                        if not self.is_playing():
                            hr = _mf.Pause()
                            hr = _mf.SetRate(1.0)
                    else:
                        self._has_media = True
                        hr = _mf.Play()
                        if on_file_loaded:
                            on_file_loaded(True)

            elif event_type == Event.MESessionScrubSampleComplete:
                self._scrub_pending = False
                if self._scrub_state == SCRUB_CLOSING:
                    self._scrub_state == SCRUB_NONE

                    self._set_rate(1.0)

                    if self._state == STATE_PLAYING:
                        hr = _mf.Play()

                    elif self.has_video():
                        ########################################
                        # We even start it if it was paused before to fix a bug in Media Foundations's
                        # EVR, otherwise it occasionally stops painting the video when paused.
                        ########################################
                        _mf.Play()
                        _mf.Pause()
                        time.sleep(.1)
                        _mf.SetVolume(self._volume)

            elif event_type == Event.MEEndOfPresentation:
                # The MEEndOfPresentation event signals that playback has reached the end of the file.
                # The Media Session automatically switches back to the stopped state.

                _mf.SetTime(0)
                if not self._loop:
                    _mf.Pause()
                    self._state = STATE_STOPPED
                    if on_end_reached:
                        on_end_reached()

        self.register_message_callback(WM_APP_NOTIFY, _on_WM_APP_NOTIFY)

        ########################################
        #
        ########################################
        def _on_WM_PAINT(hwnd, wparam, lparam):
            if self._has_video:
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, byref(ps))
                _mf.Repaint()
                user32.EndPaint(hwnd, byref(ps))

        self.register_message_callback(WM_PAINT, _on_WM_PAINT)

        ########################################
        #
        ########################################
        def _on_WM_SIZE(hwnd, wparam, lparam):
            width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
            if self._has_video:
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, byref(ps))
                _mf.ResizeVideo(width, height)
                _mf.Repaint()
                user32.EndPaint(hwnd, byref(ps))

        self.register_message_callback(WM_SIZE, _on_WM_SIZE)

    ########################################
    #
    ########################################
    def _window_proc_callback(self, hwnd, msg, wparam, lparam):
        if msg in self._message_map:
            for callback in self._message_map[msg]:
                res = callback(hwnd, wparam, lparam)
                if res is not None:
                    return res
        return self._old_proc(hwnd, msg, wparam, lparam)

    ########################################
    #
    ########################################
    def _redraw(self):
        user32.ShowWindow(self._hwnd, SW_INVALIDATE)
        user32.ShowWindow(self._hwnd, SW_SHOWNORMAL)

    ########################################
    #
    ########################################
    def _get_rate(self) -> float:
        f = FLOAT()
        hr = _mf.GetRate(byref(f))
        return f.value

    ########################################
    # We use this to switch from rate 0 to 1 and v.v., which requires paused state
    ########################################
    def _set_rate(self, rate: float):
        _mf.Pause()
        hr = _mf.SetRate(rate)

    ########################################
    #
    ########################################
    def has_media(self) -> bool:
        return self._has_media

    ########################################
    #
    ########################################
    def has_video(self) -> bool:
        return self._has_video

    ########################################
    #
    ########################################
    def has_audio(self) -> bool:
        flag = BOOL()
        hr = _mf.HasAudio(byref(flag))
        return flag.value

    ########################################
    #
    ########################################
    def load_media_file(self, media_file: str) -> bool:
        self.close_file()

        return _mf.LoadFile(media_file) == 0

    ########################################
    #
    ########################################
    def close_file(self):
        if self._has_media:
            hr = _mf.CloseFile()

            self._frame_step = 0
            self._has_media = False
            self._has_video = False
            self._is_track_update = False
            self._scrub_pending = False
            self._scrub_state = SCRUB_NONE
            self._state = STATE_CLOSED

    ########################################
    #
    ########################################
    def pause(self):
        hr = _mf.Pause()
        if hr == 0:
            self._state = STATE_PAUSED

    ########################################
    #
    ########################################
    def play(self):
        hr = _mf.Play()
        if hr == 0:
            self._state = STATE_PLAYING

    ########################################
    #
    ########################################
    def stop(self):
        _mf.SetTime(0)
        _mf.Stop()
        self._state = STATE_STOPPED

    ########################################
    # -1..1, 0=default
    ########################################
    def set_brightness(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Brightness, val)

    ########################################
    # -1..1, 0=default
    ########################################
    def set_contrast(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Contrast, val)

    ########################################
    # -1..1, 0=default
    ########################################
    def set_hue(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Hue, val)

    ########################################
    # -1..1, 0=default
    ########################################
    def set_saturation(self, val: float):
        hr = _mf.SetProcAmpValue(DXVA2_ProcAmp_Saturation, val)

    ########################################
    #
    ########################################
    def set_loop(self, flag: bool):
        self._loop = flag

    ########################################
    #
    ########################################
    def is_fullscreen(self) -> bool:
        return self._fullscreen

    ########################################
    #
    ########################################
    def set_fullscreen(self, flag: bool):
        if self._fullscreen == flag:
            return

        if flag:
            # Save window's parent, rect and style
            self._rc_window = RECT()
            self._hwnd_parent = user32.GetParent(self._hwnd)
            user32.GetWindowRect(self._hwnd, byref(self._rc_window))
            self._window_style = user32.GetWindowLongA(self._hwnd, GWL_STYLE)
            if self._hwnd_parent:
                user32.SetParent(self._hwnd, None)
            # Show it maximized as undecorated window
            user32.SetWindowLongA(self._hwnd, GWL_STYLE, WS_OVERLAPPED)
            user32.ShowWindow(self._hwnd, SW_SHOWMAXIMIZED)
        else:
            # Restore previous parent (if it had one)
            if self._hwnd_parent:
                user32.SetParent(self._hwnd, self._hwnd_parent)
                user32.MapWindowPoints(None, self._hwnd_parent, byref(self._rc_window), 2)
            # Restore previous window rect and style
            user32.SetWindowPos(
                self._hwnd, 0,
                self._rc_window.left, self._rc_window.top,
                self._rc_window.right - self._rc_window.left, self._rc_window.bottom - self._rc_window.top,
                SWP_NOZORDER | SWP_NOACTIVATE, #SWP_FRAMECHANGED
            )
            user32.SetWindowLongA(self._hwnd, GWL_STYLE, self._window_style)

        self._fullscreen = flag

    ########################################
    #
    ########################################
    def is_playing(self) -> bool:
        return self._state == STATE_PLAYING

    ########################################
    #
    ########################################
    def skip_back(self, secs: float):
        self.set_time(max(0, self.get_time() - secs))

    ########################################
    #
    ########################################
    def skip_forward(self, secs: float):
        self.set_time(self.get_time() + secs)

    ########################################
    #
    ########################################
    def step_back(self, frames: int = 1):
        if self._frame_step == 0:
            return
        self.set_time(max(0, self.get_time() - frames * self._frame_step))

    ########################################
    #
    ########################################
    def step_forward(self, frames: int = 1):
        if self._frame_step == 0:
            return
        self.set_time(self.get_time() + frames * self._frame_step)

    ########################################
    #
    ########################################
    def get_duration(self) -> float:
        d = MFTIME()
        if _mf.GetDuration(byref(d)) != 0:
            raise PlayerException()
        return d.value / MF_UNITS_PER_SEC

    ########################################
    #
    ########################################
    def _get_frame_rate(self) -> float:
        f = FLOAT()
        if _mf.GetFrameRate(byref(f)) != 0:
            raise PlayerException()
        return f.value

    ########################################
    #
    ########################################
    def get_size(self) -> tuple:
        size = DWORD()
        if _mf.GetSize(byref(size)) != 0:
            raise PlayerException()
        return size.value & 0xFFFF, (size.value >> 16) & 0xFFFF

    ########################################
    #
    ########################################
    def get_audio_tracks(self) -> list:
        cnt = DWORD()
        if _mf.GetStreamCount(byref(cnt)) != 0:
            raise PlayerException()
        stream_type = DWORD()
        four_cc = DWORD()
        selected = BOOL()
        streams = []
        lang = create_unicode_buffer(16)
        for i in range(cnt.value):
            _mf.GetStream(i, byref(stream_type), byref(four_cc), byref(selected), lang, 16)
            if stream_type.value == 1:
                name = 'Audio'
                if four_cc.value and four_cc.value in AUDIO_TYPES:
                    name += ' ' + AUDIO_TYPES[four_cc.value]
                if lang.value:
                    name += f' ({lang.value})'
                streams.append((i, name, selected.value))
        return streams

    ########################################
    #
    ########################################
    def get_video_tracks(self) -> list:
        cnt = DWORD()
        if _mf.GetStreamCount(byref(cnt)) != 0:
            raise PlayerException()
        stream_type = DWORD()
        four_cc = DWORD()
        selected = BOOL()
        streams = []
        lang = create_unicode_buffer(16)
        for i in range(cnt.value):
            _mf.GetStream(i, byref(stream_type), byref(four_cc), byref(selected), lang, 16)
            if stream_type.value == 0:
                name = 'Video'
                if four_cc.value:
                    name += ' ' + _fourcc_to_str(four_cc.value)
                if lang.value:
                    name += f' ({lang.value})'
                streams.append((i, name, selected.value))
        return streams

    ########################################
    #
    ########################################
    def get_time(self) -> float:
        t = MFTIME()
        if _mf.GetTime(byref(t)) != 0:
            raise PlayerException()
        return t.value / MF_UNITS_PER_SEC

    ########################################
    #
    ########################################
    def set_time(self, secs: float):
        if self._scrub_state == SCRUB_ACTIVE:
            if self._scrub_pending:
                ########################################
                # To keep things simple, instead of queuing we just ignore.
                ########################################
                return
            self._scrub_pending = True
            # Dont't allow to scrub beyond duration, otherwise it gets tricky
            hr = _mf.SetTime(int(min(secs * MF_UNITS_PER_SEC, self._duration - MF_UNITS_PER_SEC / 5)))

        else:
            hr = _mf.SetTime(int(secs * MF_UNITS_PER_SEC))

    ########################################
    #
    ########################################
    def scrub_start(self):
        self._scrub_state = SCRUB_ACTIVE

        self._set_rate(0.0)

        if self._state != STATE_PLAYING and self.has_video():
            _mf.SetVolume(0)

    ########################################
    #
    ########################################
    def scrub_stop(self, secs: float = None):
        self._scrub_state = SCRUB_CLOSING

        # Dont't allow to scrub beyond duration, otherwise it gets tricky
        hr = _mf.SetTime(int(min(secs * MF_UNITS_PER_SEC, self._duration - MF_UNITS_PER_SEC / 5)))

    ########################################
    #
    ########################################
    def select_audio_track(self, track_id: int):
        self._is_track_update = True
        hr = _mf.SelectAudioStream(track_id)

    ########################################
    #
    ########################################
    def select_video_track(self, track_id: int):
        self._is_track_update = True
        hr = _mf.SelectVideoStream(track_id)

    ########################################
    #
    ########################################
    def set_keep_aspect_ratio(self, keep: bool):
        _mf.SetAspectRatioMode(MFVideoARMode_PreservePicture if keep else MFVideoARMode_None)
        if not self.is_playing():
            self._redraw()

    ########################################
    # 0..1
    ########################################
    def get_volume(self) -> float:
        return self._volume

    ########################################
    # 0..1
    ########################################
    def set_volume(self, v: float):
        self._volume = max(0, min(1, v))
        _mf.SetVolume(self._volume)

    ########################################
    #
    ########################################
    def take_snapshot(self, filename: str):
        bih = BITMAPINFOHEADER()
        pDib = POINTER(BYTE)()
        cbDib = DWORD()
        ts = c_longlong()
        if _mf.GetCurrentImage(byref(bih), byref(pDib), byref(cbDib), byref(ts)) != 0:
            raise PlayerException()
        dib_size = cbDib.value
        dib = cast(pDib, POINTER(BYTE * dib_size))
        header = BMPHEADER(size=sizeof(BMPHEADER) + sizeof(BITMAPINFOHEADER) +  dib_size)
        with open(filename, 'wb') as f:
            f.write(bytes(header))
            f.write(bytes(bih))
            f.write(bytes(dib.contents))
        ole32.CoTaskMemFree(pDib)

    ########################################
    #
    ########################################
    def get_metadata(self) -> dict:
        data_ptr = POINTER(BYTE)()
        data_size = DWORD()
        if _mf.GetMetadata(byref(data_ptr), byref(data_size)) != 0:
            raise PlayerException()
        meta_data = cast(data_ptr, POINTER(WCHAR * data_size.value)).contents.value.strip()
        ole32.CoTaskMemFree(data_ptr)
        data = {}
        for row in meta_data.split('\n'):
            k, v = row.split('\t')
            if k == 'Video_FourCC':
                s = hex(int(v))[2:]
                v = ''.join([chr(int(s[i:i+2], 16)) for i in range(6, -2, -2)])
            elif k == 'Media_Duration':
                v = float(v) / 10000000
            data[k] = v
        return data

    ########################################
    #
    ########################################
    def register_message_callback(self, msg: int, callback):
        if msg not in self._message_map:
            self._message_map[msg] = []
        self._message_map[msg].append(callback)
        if self._new_proc is None:
            self._new_proc = WNDPROC(self._window_proc_callback)
            self._old_proc = user32.SetWindowLongPtrW(self._hwnd, GWL_WNDPROC, self._new_proc)

    ########################################
    #
    ########################################
    def unregister_message_callback(self, msg: int, callback=None):
        if msg in self._message_map:
            if callback is None:
                del self._message_map[msg]
            elif callback in self._message_map[msg]:
                self._message_map[msg].remove(callback)
                if len(self._message_map[msg]) == 0:
                    del self._message_map[msg]
