import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
from tqdm import tqdm

def get_clean_name(file_path):
    """Lấy tên file audio đầu tiên, sạch sẽ đuôi rác"""
    name = Path(file_path).stem
    clean_name = name.replace('.txt', '').replace('.mp3', '')
    return clean_name

def get_duration(file_path):
    """Lấy thời lượng file audio bằng ffprobe"""
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    return float(subprocess.check_output(cmd).decode('utf-8').strip())

def create_master_slideshow(image_files, output_path, tmp_base_dir):
    """GIAI ĐOẠN 1: Tạo Master Slideshow mượt mà"""
    fps = 24
    duration_per_img = 10
    
    # Filter Zoom Super-sampling (8000px) để mượt tuyệt đối
    smooth_filter = (
        f"scale=8000x4500,format=yuv420p,"
        f"zoompan=z='zoom+0.0004':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={duration_per_img * fps}:s=1920x1080:fps={fps}"
    )

    # Tạo thư mục temp_parts ngay trong thư mục tmp_base_dir (nằm trong output)
    temp_parts_dir = os.path.join(tmp_base_dir, "master_parts")
    if os.path.exists(temp_parts_dir): shutil.rmtree(temp_parts_dir)
    os.makedirs(temp_parts_dir, exist_ok=True)
    
    parts = []
    print(f"🎨 GIAI ĐOẠN 1: Đang tạo Master Slideshow từ {len(image_files)} ảnh...")
    for idx, img in enumerate(tqdm(image_files, desc="Rendering Slides")):
        part_p = os.path.join(temp_parts_dir, f"p_{idx:04d}.mp4")
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-loop', '1', '-i', os.path.abspath(img),
            '-vf', smooth_filter, 
            '-c:v', 'h264_nvenc', '-preset', 'p7', '-tune', 'hq', 
            '-r', str(fps), '-t', str(duration_per_img), 
            os.path.abspath(part_p)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\n❌ Lỗi FFmpeg tại ảnh {img}: {result.stderr}")
            sys.exit(1)
        parts.append(part_p)

    # Tạo file list để concat ngay trong thư mục temp
    list_p = os.path.join(temp_parts_dir, "master_list.txt")
    with open(list_p, "w", encoding="utf-8") as f:
        for p in parts:
            p_abs_fixed = os.path.abspath(p).replace('\\', '/')
            f.write(f"file '{p_abs_fixed}'\n")
    
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_p, '-c', 'copy', os.path.abspath(output_path)], capture_output=True)

def merge_audio_video(master_v, audio_p, output_p, i, total):
    """GIAI ĐOẠN 2: Stream copy video và ghép audio"""
    duration = get_duration(audio_p)
    filename = Path(audio_p).name
    
    cmd = [
        'ffmpeg', '-y', '-progress', 'pipe:1', '-loglevel', 'error',
        '-stream_loop', '-1', '-i', os.path.abspath(master_v),
        '-i', os.path.abspath(audio_p),
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-map', '0:v:0', '-map', '1:a:0',
        '-t', str(duration), '-shortest', os.path.abspath(output_p)
    ]

    with tqdm(total=int(duration), desc=f"🎬 [{i}/{total}] Khớp nhạc: {filename[:15]}", unit="s", colour='green') as pbar:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            t_match = re.search(r'out_time_ms=(\d+)', line)
            if t_match:
                pbar.n = int(int(t_match.group(1)) / 1000000)
                pbar.refresh()
        process.wait()

def main():
    if len(sys.argv) < 3:
        print("Sử dụng: python code.py <folder_anh> <folder_audio>")
        return

    img_dir = os.path.abspath(sys.argv[1])
    audio_dir = os.path.abspath(sys.argv[2])
    
    # Thiết lập thư mục Output và Temp hoàn toàn trong đường dẫn Audio
    out_dir = os.path.join(audio_dir, "output")
    tmp_dir = os.path.join(out_dir, "temp_processing")
    os.makedirs(tmp_dir, exist_ok=True)
    
    images = sorted([os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    audios = sorted([os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.lower().endswith('.mp3')])

    if not images or not audios:
        print("❌ Lỗi: Kiểm tra lại folder ảnh hoặc audio!")
        return

    clean_final_name = get_clean_name(audios[0]) + ".mp4"
    final_path = os.path.join(out_dir, clean_final_name)

    # 1. Tạo Master Slideshow - Lưu tệp tạm vào trong thư mục output/temp_processing
    master_v = os.path.join(tmp_dir, "master_slide_source.mp4")
    create_master_slideshow(images, master_v, tmp_dir)

    # 2. Khớp từng Audio vào Master Video
    print(f"\n🚀 GIAI ĐOẠN 2: Khớp nhạc (Lặp Video Slide)...")
    v_list = []
    for i, audio in enumerate(audios, 1):
        tmp_v = os.path.join(tmp_dir, f"v_part_{i:04d}.mp4")
        merge_audio_video(master_v, audio, tmp_v, i, len(audios))
        v_list.append(tmp_v)

    # 3. Đóng gói Final
    print(f"\n🔗 GIAI ĐOẠN 3: Đóng gói thành phẩm: {clean_final_name}")
    concat_p = os.path.join(tmp_dir, "final_concat_list.txt") # File txt cũng nằm trong temp
    with open(concat_p, "w", encoding="utf-8") as f:
        for v in v_list:
            v_abs_fixed = os.path.abspath(v).replace('\\', '/')
            f.write(f"file '{v_abs_fixed}'\n")
    
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_p, '-c', 'copy', final_path], capture_output=True)
    
    # 4. Dọn dẹp sạch sẽ thư mục Temp trong Output
    print(f"\n🧹 Đang dọn dẹp các tệp tạm...")
    shutil.rmtree(tmp_dir)
    
    print(f"\n✅ HOÀN TẤT!")
    print(f"📍 Video cuối cùng: {final_path}")

if __name__ == "__main__":
    main()