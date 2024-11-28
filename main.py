import os
import time
import threading
import re
import lib_ocr
import google.generativeai as genai
from dotenv import load_dotenv
from pytesseract import image_to_string
from PIL import Image

# Load môi trường
load_dotenv()

# Cấu hình API GPT
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Hàm khởi tạo mô hình
def initialize_model(model_name="gemini-1.5-flash"):
    return genai.GenerativeModel(model_name)

# Hàm gửi câu hỏi tới GPT
def get_response(model, model_behavior, prompt):
    response = model.generate_content([model_behavior, prompt])
    return response.text

def extract_last_sentence(text):
    lines = text.strip().splitlines()
    if lines:
        return lines[-1]
    else:
        return None
    
history_save = "answered_history.txt"

def load_history():
    """Tải lịch sử câu trả lời từ file."""
    try:
        with open(history_save, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()
    
def save_to_history(last_sentence):
    """Ghi câu hỏi vào file lịch sử."""
    try:
        with open(history_save, 'a', encoding='utf-8') as f:
            f.write(last_sentence + '\n')
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử: {e}")


# Hàm xử lý OCR và gửi câu hỏi
def perform_ocr_and_ask(image_path, model, model_behavior):
    # Đường dẫn để lưu văn bản trích xuất
    output_text_file = "ocr_output.txt"

    history=load_history()

    # Trích xuất văn bản từ ảnh bằng Tesseract OCR
    image = Image.open(image_path)
    text_from_image = image_to_string(image, lang="vie")  # Chọn ngôn ngữ OCR, ví dụ: "vie" hoặc "eng"
    
    # Ghi văn bản vào file để kiểm tra sau
    with open(output_text_file, "w", encoding="utf-8") as file:
        file.write(text_from_image)
    
    print(f"Văn bản OCR đã nhận diện:\n{text_from_image}")
    
    # Trích xuất câu hỏi từ văn bản OCR
    last_sentence = extract_last_sentence(text_from_image)
    if not last_sentence:
        return "Không tìm thấy dòng văn bản rõ ràng."
    
    # Phân tích từng câu hỏi
    responses = []
    for last_sentence in last_sentence.split("\n"):
        if last_sentence in history:
            print(f"Bỏ qua câu hỏi đã trả lời: {last_sentence}")
            continue
        
        # Gửi câu hỏi tới mô hình GPT
        response = get_response(model, model_behavior, last_sentence)
        responses.append(f"Câu hỏi: {last_sentence}\nPhản hồi: {response}\n")
        
        # Lưu câu hỏi vào lịch sử
        save_to_history(last_sentence)
    # Trả về toàn bộ phản hồi hoặc thông báo nếu không có câu hỏi mới
    return "\n".join(responses) if responses else "Không có câu hỏi mới cần trả lời."

# Hàm chính: chụp màn hình và xử lý
def capture_loop_and_send(region, output_img, model, model_behavior, interval=15):
    try:
        while True:
            # Chụp ảnh màn hình
            capture_screen(region, output_img)
            print(f"Ảnh đã được lưu tại: {output_img}")
            
            # Gửi OCR và GPT
            response = perform_ocr_and_ask(output_img, model, model_behavior)
            print(f"Phản hồi từ GPT: {response}")
            
            # Đợi một khoảng thời gian trước lần lặp tiếp theo
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Dừng chương trình do người dùng nhấn Ctrl+C.")

# Hàm dừng chương trình
def stop_loop():
    try:
        input("Nhấn Enter để dừng chương trình...\n")
        os._exit(0)
    except Exception as e:
        print(f"Đã xảy ra lỗi khi dừng chương trình: {e}")

# --- Chương trình chính ---
if __name__ == "__main__":
    # Cấu hình vùng cần chụp và tệp kết quả
    region = (950, 55, 976, 800)  # Tọa độ vùng chụp (x1, y1, x2, y2)
    output_img = "region_screenshot.png"

    # Khởi tạo mô hình
    model = initialize_model("gemini-1.5-flash")
    model_behavior = """
        Bạn là trợ lý ảo chuyên hỗ trợ giải đáp mọi thắc mắc của khách hàng.
        Chỉ tập trung trả lời câu hỏi, không cung cấp thông tin thừa.
    """

    # Tạo một luồng riêng để lắng nghe lệnh dừng
    stop_thread = threading.Thread(target=stop_loop)
    stop_thread.daemon = True  # Đảm bảo luồng sẽ dừng khi chương trình kết thúc
    stop_thread.start()

    # Chạy vòng lặp chụp ảnh và gửi GPT
    capture_loop_and_send(region, output_img, model, model_behavior, interval=15)