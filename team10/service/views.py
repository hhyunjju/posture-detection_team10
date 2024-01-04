# service/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import CameraImage


#임시로 만들었습니다
def model(request):
    return render(request, 'service/model.html')
def service(request):
    return render(request, 'service/service.html')
def statistics(request):
    return render(request, 'service/statistics.html')
def game(request):
    return render(request, 'service/game.html')


# def test2(request):
#     if request.method == 'POST':
#         image = request.FILES.get('camera-image')
#         CameraImage.objects.create(image=image)
#     images = CameraImage.objects.all()
#     context = {
#         'images':images
#     }
#     return render(request, 'service/service.html', context)

def upload(request):
    if request.method == 'POST' and request.FILES['files']:
        image = request.FILES.get('camera-image')
        CameraImage.objects.create(image=image)
    images = CameraImage.objects.all()
    context = {
        'images':images
    }
    return render(request, 'service/service.html', context)

from django.http import FileResponse
import cv2
import mediapipe as mp
import joblib
import numpy as np
import pandas as pd
from .preprocessing import calculate_angle, calculate_distance, selected_landmarks, landmark_description
import os

# num = 0

# def send_image(request):
#     if request.method == 'POST':
#         image_file = request.FILES.get('img_file')
#         return FileResponse(image_file, content_type='image/png')
        
        
def send_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('img_file')
        mp_holistic = mp.solutions.holistic
        model_path = os.path.join(os.getcwd(), 'service\pose_classification_model.pkl')
        model = joblib.load(model_path) # 여기 삭제하고 특정 이벤트 발생시 모델을 로드하도록.
        display_text = "Waiting..."
 
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            if image_file:
                # Convert image file to an array that OpenCV can use
                nparr = np.fromstring(image_file.read(), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
 
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
 
                visibility = [landmark.visibility for landmark in results.pose_landmarks.landmark] if results.pose_landmarks else []
                avg_visibility = np.mean(visibility) if visibility else 0
 
                if avg_visibility > 0.1:  # 사람이 화면에 있을 경우
                    pose_landmarks = results.pose_landmarks.landmark
                    row = []
                   
                    # 선택된 랜드마크의 위치 및 가시성 데이터
                    for i in selected_landmarks:
                        landmark = pose_landmarks[i]
                        row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
                           
                    # 거리 계산 및 상대적인 거리 계산
                    distances = {}  # 각 거리 값을 저장하는 딕셔너리
                    for i, landmark_i in enumerate(selected_landmarks):
                        for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1):
                            distance = calculate_distance([pose_landmarks[landmark_i].x, pose_landmarks[landmark_i].y, pose_landmarks[landmark_i].z],
                                                        [pose_landmarks[landmark_j].x, pose_landmarks[landmark_j].y, pose_landmarks[landmark_j].z])
                            row.append(distance)
                            distances[(landmark_i, landmark_j)] = distance
                   
                    reference_distance = distances.get('distance_between_left_eye_and_right_eye', 1)
 
                    # 상대적인 거리 계산
                    relative_distances = [distance / reference_distance for distance in distances.values()]
                    row.extend(relative_distances)
                   
                    for i, landmark_i in enumerate(selected_landmarks):
                        for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1):
                            for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1):
                                angle = calculate_angle([pose_landmarks[landmark_i].x, pose_landmarks[landmark_i].y, pose_landmarks[landmark_i].z],
                                                        [pose_landmarks[landmark_j].x, pose_landmarks[landmark_j].y, pose_landmarks[landmark_j].z],
                                                        [pose_landmarks[landmark_k].x, pose_landmarks[landmark_k].y, pose_landmarks[landmark_k].z])
                                row.append(angle)                        
 
                    # 컬럼명 생성 (선택된 랜드마크 기반)
                    csv_columns = [f'{landmark_description[i]}_{dim}' for i in selected_landmarks for dim in ['x', 'y', 'z', 'visibility']]
                    csv_columns += [f'distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
                    csv_columns += [f'relative_distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
                    csv_columns += [f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1) for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1)]
                   
                    row_df = pd.DataFrame([row], columns=csv_columns)  # 컬럼명 적용
                    row_df.to_csv('test.csv')
 
                    # RandomForest 모델을 사용하여 자세 예측
                    prediction = model.predict(row_df)
                    class_name = prediction[0] # 여기를 DB로 넘김
                    print("클래스 : ", class_name)
                   
                    if class_name == 0:
                        message = "good posture"
                    else:
                        message = 'bad posture'
                   
                    # 자세 정보 업데이트
                    display_text = f'Pose: {message}'
                else:
                    # 가시성이 낮을 때는 대기 메시지 표시
                    display_text = "Waiting..."
                   
                processed_image_path = "./media/processed_image.png"
                cv2.imwrite(processed_image_path, frame)  # 이미지 저장
        return FileResponse(open(processed_image_path, 'rb'), content_type='image/png')
