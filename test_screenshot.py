from PIL import ImageGrab
import os

try:
    print("Attempting to take screenshot...")
    img = ImageGrab.grab()
    path = "test_screenshot.png"
    img.save(path)
    print(f"Screenshot saved to {os.path.abspath(path)}")
    os.remove(path)
    print("Test successful, file removed.")
except Exception as e:
    print(f"Screenshot test FAILED: {e}")
