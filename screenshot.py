import asyncio
import cv2
from utils import get_direct3d_device
from winsdk.windows.graphics.capture.interop import create_for_window
from ctypes.wintypes import HWND
from winsdk.windows.graphics.capture import (
    Direct3D11CaptureFramePool,
    Direct3D11CaptureFrame,
)
from winsdk.windows.graphics.directx import DirectXPixelFormat
from winsdk.system import Object
from winsdk.windows.graphics.imaging import (
    SoftwareBitmap,
    BitmapBufferAccessMode,
    BitmapBuffer,
)
import numpy as np


class Screenshot_WindowsGraphicsCapture:
    def __init__(self, hwnd: HWND) -> None:
        self.device = get_direct3d_device()
        self.item = create_for_window(hwnd)

    async def get_frame(self) -> cv2.Mat:
        event_loop = asyncio.get_running_loop()
        # create frame pool
        self.frame_pool = Direct3D11CaptureFramePool.create_free_threaded(
            self.device,
            DirectXPixelFormat.B8_G8_R8_A8_UINT_NORMALIZED,
            1,
            self.item.size,
        )
        # create capture session
        self.session = self.frame_pool.create_capture_session(self.item)
        self.session.is_border_required = False
        self.session.is_cursor_capture_enabled = False
        fut = event_loop.create_future()

        # callback
        def frame_arrived_callback(
            frame_pool: Direct3D11CaptureFramePool, event_args: Object
        ):
            frame: Direct3D11CaptureFrame = frame_pool.try_get_next_frame()
            fut.set_result(frame)
            self.session.close()

        # set callback 
        self.frame_pool.add_frame_arrived(
            lambda fp, o: event_loop.call_soon_threadsafe(frame_arrived_callback, fp, o)
        )

        # start capture
        self.session.start_capture()

        # await frame and transform frame to bitmap
        frame_fut: Direct3D11CaptureFrame = await fut
        software_bitmap: SoftwareBitmap = (
            await SoftwareBitmap.create_copy_from_surface_async(frame_fut.surface)
        )

        # bitmap -> ndarray
        buffer: BitmapBuffer = software_bitmap.lock_buffer(
            BitmapBufferAccessMode.READ_WRITE
        )
        image = np.frombuffer(buffer.create_reference(), dtype=np.uint8)
        # TODO: resize image 
        image.shape = (self.item.size.height, self.item.size.width, 4)
        return image
