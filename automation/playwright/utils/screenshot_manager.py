import os
import uuid


class ScreenshotManager:
    BASE_DIR = "media/automation/screenshots"

    @classmethod
    def take(cls, page):
        os.makedirs(cls.BASE_DIR, exist_ok=True)
        filename = f"{uuid.uuid4()}.png"
        path = os.path.join(cls.BASE_DIR, filename)
        page.screenshot(path=path)
        return path
