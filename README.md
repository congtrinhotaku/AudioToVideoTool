🎬 Auto Slideshow Video Builder (FFmpeg + NVENC)

Tool Python tự động tạo video slideshow mượt (zoom cinematic) từ thư mục ảnh và ghép nhiều file MP3 thành một video hoàn chỉnh.

Hệ thống được tối ưu theo mô hình:

Ảnh → Master Slideshow (1 lần duy nhất)
     → Ghép từng Audio (stream copy video)
     → Concat thành 1 file Final
     → Xóa toàn bộ file tạm
🚀 Tính năng chính

Render slideshow zoom mượt bằng zoompan

Super-sampling 8000px cho chuyển động cực mịn

Encode bằng h264_nvenc (GPU NVIDIA)

Tự động lặp video theo thời lượng audio

Stream copy video khi ghép audio (cực nhanh)

Hiển thị progress theo thời lượng audio

Tự động dọn sạch thư mục temp sau khi hoàn tất

Xuất video 1920x1080 – 24fps

📂 Cấu trúc thư mục

Ví dụ:

project/
│
├── images/          (chứa ảnh .jpg .png)
├── audios/          (chứa file .mp3)
│
└── code.py

Sau khi chạy:

audios/
│
├── output/
│   ├── video_final.mp4
│   └── temp_processing/  (tự động xóa sau khi xong)
⚙️ Yêu cầu hệ thống

Python 3.9+

FFmpeg (có hỗ trợ NVENC)

GPU NVIDIA (khuyến nghị)

tqdm (pip install tqdm)

Kiểm tra NVENC:

ffmpeg -encoders | findstr nvenc
▶️ Cách sử dụng
python code.py <folder_anh> <folder_audio>

Ví dụ:

python code.py images audios
🧠 Quy trình hoạt động
Giai đoạn 1 – Tạo Master Slideshow

Mỗi ảnh hiển thị 10 giây

Zoom chậm mượt

Render thành master_slide_source.mp4

Giai đoạn 2 – Ghép từng Audio

Lặp master video vô hạn

Cắt đúng theo thời lượng mp3

Stream copy video (không encode lại)

Encode audio AAC 192kbps

Giai đoạn 3 – Đóng gói Final

Concat toàn bộ các video đã ghép

Xuất file duy nhất trong output/

Giai đoạn 4 – Cleanup

Xóa toàn bộ temp_processing

🎥 Thông số Video
Thông số	Giá trị
Resolution	1920x1080
FPS	24
Codec Video	h264_nvenc
Codec Audio	AAC 192kbps
Hiệu ứng	Zoom Pan Cinematic
Thời lượng	Phụ thuộc tổng thời lượng audio
📌 Lưu ý

Tên file video cuối cùng sẽ lấy theo file mp3 đầu tiên.

Nếu không có GPU NVIDIA → cần đổi encoder sang libx264.

Toàn bộ file tạm được lưu trong output/temp_processing.

💡 Tối ưu hiệu suất

Master slideshow chỉ render 1 lần.

Ghép audio sử dụng -c:v copy → tốc độ cực nhanh.

Phù hợp làm video truyện dài nhiều tập.
