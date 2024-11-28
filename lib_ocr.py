import time
import pyautogui
import pytesseract
from PIL import Image
import cv2
import os
import time
import threading

# Cấu hình đường dẫn Tesseract (thay đổi nếu khác vị trí cài đặt)
pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def capture_screen(region=None, output_path="region_screenshot.png"):
    """
    Chụp ảnh màn hình và lưu vào tệp.

    Args:
        region (tuple): Vùng để cắt (left, top, width, height). Nếu None, chụp toàn màn hình.
        output_path (str): Đường dẫn lưu tệp ảnh.

    Returns:
        str: Đường dẫn tệp ảnh đã lưu.
    """
    try:
        # Chụp ảnh màn hình
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(output_path)
        print(f"Ảnh đã được lưu vào: {output_path}")
        return output_path
    except Exception as e:
        print(f"Lỗi khi chụp ảnh màn hình: {e}")
        return None

def extract_text_from_image(image_path, output_file, lang='vie'):
    """
    Nhận diện văn bản từ ảnh bằng Tesseract OCR.

    Args:
        image_path (str): Đường dẫn tệp ảnh.
        output_file (str): Đường dẫn tệp lưu kết quả văn bản.
        lang (str): Mã ngôn ngữ cho Tesseract (vd: 'vie' cho tiếng Việt).

    Returns:
        str: Văn bản được nhận diện.
    """
    try:
        # Kiểm tra file ảnh tồn tại
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File không tồn tại: {image_path}")
        
        # Đọc ảnh
        img = cv2.imread(image_path)
        
        # Kiểm tra đọc ảnh thành công
        if img is None:
            raise ValueError(f"Không thể đọc được ảnh từ đường dẫn: {image_path}")
        
        # Chuyển đổi BGR -> RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Nhận diện văn bản
        text = pytesseract.image_to_string(img, lang=lang)
        print("Văn bản nhận diện được:")
        print(text)
        
        # Ghi kết quả vào file
        with open(output_file, 'a', encoding='utf-8') as f:
            f.writelines(text + '\n')
        
        print(f"Văn bản đã được lưu vào file: {output_file}")
        return text
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
        return None

# Biến toàn cục để dừng vòng lặp
stop_capture = False


def capture_loop(region, output_img, output_text):
    """
    Hàm thực hiện vòng lặp chụp màn hình và OCR mỗi 30 giây.
    Args:
        region (tuple): Vùng cần chụp (x1, y1, x2, y2).
        output_img (str): Tên file ảnh đầu ra.
        output_text (str): Tên file kết quả OCR.
    """
    global stop_capture

    while not stop_capture:
        print("Đang chụp ảnh màn hình...")
        screenshot_path = capture_screen(region=region, output_path=output_img)

        if screenshot_path:
            print("Thực hiện OCR trên ảnh vừa chụp...")
            extract_text_from_image(screenshot_path, output_text, lang="vie")
            print(f"Kết quả OCR đã được lưu vào: {output_text}")
        else:
            print("Lỗi khi chụp ảnh màn hình!")

        # Tạm dừng 30 giây trước khi lặp lại
        time.sleep(10)


def stop_loop():
    """
    Hàm dừng vòng lặp khi người dùng nhập lệnh dừng.
    """
    global stop_capture

    while True:
        command = input("Nhập 'stop' để dừng vòng lặp: ").strip().lower()
        if command == "stop":
            print("Đã nhận lệnh dừng, kết thúc vòng lặp.")
            stop_capture = True
            break

# sử dụng thư viện
if __name__ == "__main__":
    
    print("Đang chờ 30 giây trước khi chụp màn hình...")