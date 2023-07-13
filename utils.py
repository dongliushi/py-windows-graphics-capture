import asyncio

from winsdk.windows.ai.machinelearning import LearningModelDevice, LearningModelDeviceKind
from winsdk.windows.media.capture import MediaCapture


# source code from https://github.com/Avasam/AutoSplit/blob/master/src/utils.py
# and from https://github.com/pywinrt/python-winsdk/issues/11
def get_direct3d_device():
    try:
      direct_3d_device = LearningModelDevice(LearningModelDeviceKind.DIRECT_X_HIGH_PERFORMANCE).direct3_d11_device
    except: # TODO: Unknown potential error, I don't have an older Win10 machine to test.
      direct_3d_device = None 
    if not direct_3d_device:
        # Note: Must create in the same thread (can't use a global) otherwise when ran from not the main thread it will raise:
        # OSError: The application called an interface that was marshalled for a different thread
        media_capture = MediaCapture()

        async def coroutine():
            await (media_capture.initialize_async() or asyncio.sleep(0))
        asyncio.run(coroutine())
        direct_3d_device = media_capture.media_capture_settings and \
            media_capture.media_capture_settings.direct3_d11_device
    if not direct_3d_device:
        raise OSError("Unable to initialize a Direct3D Device.")
    return direct_3d_device
