# 🎬 Auto Slideshow Video Builder (FFmpeg + NVENC)

Tool Python tự động tạo video slideshow zoom mượt từ thư mục ảnh và ghép nhiều file MP3 thành một video hoàn chỉnh.

---

## 🚀 Tính năng

- Render slideshow zoom cinematic bằng `zoompan`
- Super-sampling 8000px cho chuyển động cực mịn
- Encode bằng `h264_nvenc` (GPU NVIDIA)
- Tự động lặp video theo thời lượng audio
- Stream copy video khi ghép audio (rất nhanh)
- Hiển thị progress theo thời lượng audio
- Tự động xóa toàn bộ file tạm sau khi hoàn tất
- Xuất video Full HD 1920x1080 – 24fps

---

## 📂 Cấu trúc thư mục

Ví dụ project:

```
project/
│
├── images/          (chứa ảnh .jpg .png .jpeg)
├── audios/          (chứa file .mp3)
│
└── code.py

```

Sau khi chạy:

```
audios/
│
├── output/
│   ├── ten_video.mp4
│   └── temp_processing/  (tự động xóa sau khi hoàn tất)

```

---

## ⚙️ Yêu cầu hệ thống

- Python 3.9+
- FFmpeg (có hỗ trợ NVENC)
- GPU NVIDIA (khuyến nghị)
- tqdm

Cài tqdm:

```
pip install tqdm

```

Kiểm tra NVENC:

```
ffmpeg -encoders | findstr nvenc

```

---

## ▶️ Cách sử dụng

```
python code.py <folder_anh> <folder_audio>

```

Ví dụ:

```
python code.py images audios

```

---

## 🧠 Quy trình hoạt động

### 1️⃣ Tạo Master Slideshow

- Mỗi ảnh hiển thị 10 giây
- Zoom chậm mượt
- Render thành `master_slide_source.mp4`

### 2️⃣ Ghép từng Audio

- Lặp master video vô hạn
- Cắt đúng theo thời lượng mp3
- Stream copy video (`c:v copy`)
- Encode audio AAC 192kbps

### 3️⃣ Đóng gói Final

- Concat toàn bộ video đã ghép
- Xuất file duy nhất trong `output/`

### 4️⃣ Cleanup

- Xóa toàn bộ thư mục `temp_processing`

---

## 🎥 Thông số Video

| Thông số | Giá trị |
| --- | --- |
| Resolution | 1920x1080 |
| FPS | 24 |
| Video Codec | h264_nvenc |
| Audio Codec | AAC 192kbps |
| Hiệu ứng | Zoom Pan |
| Thời lượng | Phụ thuộc audio |

---

## 📌 Lưu ý

- Tên video cuối cùng lấy theo file mp3 đầu tiên.
- Nếu không có GPU NVIDIA → đổi encoder sang `libx264`.
- Toàn bộ file tạm nằm trong `output/temp_processing`.

---

## 💡 Tối ưu hiệu suất

- Master slideshow chỉ render 1 lần.
- Ghép audio sử dụng stream copy → tốc độ rất nhanh.
- Phù hợp làm video truyện dài nhiều tập.
