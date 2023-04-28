import os
from pydub import AudioSegment
from pydub.silence import detect_silence
import zipfile

input_dir = input("请输入要导入的文件夹位置（回车确认）：")
mac_input_dir = input_dir
# input_dir = os.path.normpath(input_dir)

if "\\" in input_dir:
    input_dir = input_dir.strip('"')
else:
    input_dir += "/"

#print(input_dir)
output_dir = input("请输入要导出的文件夹位置（回车确认）：")
# output_dir = os.path.normpath(output_dir)

if "\\" in output_dir:
    output_dir = output_dir.strip('"')
else:
    output_dir += "/"

#print(output_dir)
is_zip = int(input("是否需要压缩（1需要，0不需要，回车确认）："))
if "/" in input_dir: 
    if is_zip:
        zip_name = input("请输入要导出的压缩包名（直接回车则默认使用导入的文件夹名称）：")
        if not zip_name:
            zip_name = os.path.basename(mac_input_dir)
else:
    if is_zip:
        zip_name = input("请输入要导出的压缩包名（直接回车则默认使用导入的文件夹名称）：")
        if not zip_name:
            zip_name = os.path.basename(input_dir)


# input_dir += "/"
# output_dir += "/"
# 定义可处理的文件格式列表
ALLOWED_EXTENSIONS = {'wav', 'm4a', 'aac', 'mp3'}


# 检查文件是否在可处理的文件格式列表中
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


for file_name in os.listdir(input_dir):
    if not allowed_file(file_name):
        print(f"跳过不可处理的文件：{file_name}")
        continue
    file_path = os.path.join(input_dir, file_name)
    print(f"处理文件：{file_path}")
    audio = AudioSegment.from_file(file_path, frame_rate=8000, channels=1)

    # 如果是立体声，删除一个声道
    if audio.channels == 2:
        audio = audio.set_channels(1)

    # 剪切静音段
    silent_ranges = detect_silence(audio, min_silence_len=1, silence_thresh=-28)
    print(f"音频长度：{len(audio)} ms")
    print(f"平均音量：{audio.dBFS} dBFS")

    # for i, (start, end) in enumerate(silent_ranges):
    # print(f"静音段{i+1}: {start} ms - {end} ms")

    if silent_ranges:
        start_trim = silent_ranges[0][1]  # 起始时间为第一个静音段的结束时间
        end_trim = silent_ranges[-1][0]  # 结束时间为最后一个静音段的起始时间
        audio = audio[start_trim:end_trim]  # 裁剪音频文件

    # 导出音频文件
    output_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + '.wav')
    audio.export(output_path, format="wav", bitrate="128k", parameters=["-ar", "8000"])
    print(f"导出文件：{output_path}")
    # audio.export(output_path, format="wav")

if is_zip:
    zip_name += '.zip'
    zip_path = os.path.join(output_dir, zip_name)  # zip文件的输出路径
    zip_file = zipfile.ZipFile(zip_path, mode='w')
    for file_name in os.listdir(output_dir):
        if allowed_file(file_name):
            file_path = os.path.join(output_dir, file_name)
            zip_file.write(file_path, arcname=file_name)  # 添加
    zip_file.close()
    print(f"压缩包已导出到：{zip_path}")

input("按回车键退出...")
