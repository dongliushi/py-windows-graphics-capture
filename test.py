
import asyncio
import ctypes

from screenshot import Screenshot_WindowsGraphicsCapture
import cv2

async def main():
    user32 = ctypes.windll.user32

    # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-findwindoww
    handle = user32.FindWindowW(None, "Here fill in the window title you want to capture")
    snapshot = Screenshot_WindowsGraphicsCapture(handle)
    
    # call async func
    image = await snapshot.get_frame()

    # show capture frame
    cv2.imshow('image',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return


if __name__ == "__main__":
    asyncio.run(main())