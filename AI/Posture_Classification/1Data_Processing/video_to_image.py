import cv2
import os

# 폴더 내 모든 비디오 파일을 처리하기 위한 함수
def process_videos_from_folder(folder_path, output_folder, target_fps=15):
    video_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp4', '.avi', '.mov'))]

    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        frame_skip_rate = int(fps / target_fps)

        frame_num = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            if frame_num % frame_skip_rate == 0:
                output_image_path = os.path.join(output_folder, f'{video_file}_frame_{frame_num//frame_skip_rate}.jpg')
                cv2.imwrite(output_image_path, frame)

            frame_num += 1

        cap.release()

# 비디오가 저장된 폴더 경로를 지정
video_folder_path = 'video_path'

# 저장할 이미지의 폴더 경로를 지정
output_folder_path = 'output_path'
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

process_videos_from_folder(video_folder_path, output_folder_path)