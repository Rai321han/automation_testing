import os
import uuid


class ScreenshotManager:
    BASE_DIR = "media/automation/screenshots"

    @classmethod
    def take(cls, page, filename):
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        path = os.path.join(cls.BASE_DIR, filename)
        page.screenshot(path=path)
        return path
