# service/views.py

from django.shortcuts import render, redirect

from .models import PostureDetection
from django.http import JsonResponse
import cv2
import mediapipe as mp
import joblib
import numpy as np
import pandas as pd
from .preprocessing import calculate_angle, calculate_distance, selected_landmarks, landmark_description, stretching_selected_landmarks
import os
# import mlflow
from datetime import datetime, timedelta
import mlflow

from django.contrib.auth.decorators import login_required

# MLflow Tracking URI 설정
# mlflow.set_tracking_uri("C:\\Users\\user\\TEAM10\\team10\\team10\\service\\mlruns")
mlflow_path = os.path.join(os.getcwd(), 'service\mlruns')
mlflow_path = "file:\\"+mlflow_path
mlflow.set_tracking_uri(mlflow_path)

# # 포즈 run ID와 모델 이름 설정
# run_id_pose = "6b8c4018707341eca7bf4e57438cc697"
# model_name_pose = "model_pose_final"

# # 포즈 모델을 불러오는 코드
# model_uri_pose = f"runs:/{run_id_pose}/{model_name_pose}"
# pose_model = mlflow.sklearn.load_model(model_uri_pose)

# # 스트레칭 run ID와 모델 이름 설정
# run_id_stretch = "6b8c4018707341eca7bf4e57438cc697"
# model_name_stretch = "model_stretch_final"

# # 스트레칭 모델을 불러오는 코드
# model_uri_stretch = f"runs:/{run_id_stretch}/{model_name_stretch}"
# stretching_model = mlflow.sklearn.load_model(model_uri_stretch)
    
model_path = os.path.join(os.getcwd(), 'service\pose_classification_model.pkl')
pose_model = joblib.load(model_path) 

stretching_model_path = os.path.join(os.getcwd(), 'service\pose_classification_model_stretch_final.pkl')
stretching_model = joblib.load(stretching_model_path) 


def service(request):
    return render(request, 'service/service.html')

def game(request):
    return render(request, 'service/game.html')

        
@login_required(login_url='accounts:login')
def send_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('img_file')
        mp_holistic = mp.solutions.holistic
        display_text = "Waiting..."
 
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            if image_file:
                nparr = np.fromstring(image_file.read(), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)

                visibility = [landmark.visibility for landmark in results.pose_landmarks.landmark] if results.pose_landmarks else []
                avg_visibility = np.mean(visibility) if visibility else 0

                if avg_visibility > 0.4:  # 사람이 화면에 있을 경우
                    pose_landmarks = results.pose_landmarks.landmark
                    row = []
                    
                    # 1. landmark positions and visibility
                    for i in selected_landmarks:
                        landmark = pose_landmarks[i]
                        row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
                            
                    # 2. Calculate distances
                    distances = {}
                    for i, landmark_i in enumerate(selected_landmarks):
                        for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1):
                            distance = calculate_distance([pose_landmarks[landmark_i].x, pose_landmarks[landmark_i].y, pose_landmarks[landmark_i].z],
                                                        [pose_landmarks[landmark_j].x, pose_landmarks[landmark_j].y, pose_landmarks[landmark_j].z])
                            row.append(distance)
                            distances[(landmark_i, landmark_j)] = distance
                    
                    reference_distance = distances.get('distance_between_left_eye_and_right_eye', 1)

                    # 3. Calculate relative distances
                    relative_distances = [distance / reference_distance for distance in distances.values()]
                    row.extend(relative_distances)
                    
                    # 4. Calculate relative landmark position(z)
                    for i in selected_landmarks:
                        landmark = pose_landmarks[i]    
                        row.append(landmark.z * reference_distance)
                    
                    # 5. Calculate angles
                    for i, landmark_i in enumerate(selected_landmarks):
                        for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1):
                            for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1):
                                angle = calculate_angle([pose_landmarks[landmark_i].x, pose_landmarks[landmark_i].y, pose_landmarks[landmark_i].z],
                                                        [pose_landmarks[landmark_j].x, pose_landmarks[landmark_j].y, pose_landmarks[landmark_j].z],
                                                        [pose_landmarks[landmark_k].x, pose_landmarks[landmark_k].y, pose_landmarks[landmark_k].z])
                                row.append(angle)                        

                    # 컬럼명 생성
                    csv_columns = [f'{landmark_description[i]}_{dim}' for i in selected_landmarks for dim in ['x', 'y', 'z', 'visibility']]
                    csv_columns += [f'distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
                    csv_columns += [f'relative_distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
                    csv_columns += [f'relative_{landmark_description[i]}_z' for i in selected_landmarks]
                    csv_columns += [f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1) for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1)]
                    
                    row_df = pd.DataFrame([row], columns=csv_columns) 
 
                    # 자세 예측
                    prediction = pose_model.predict(row_df)
                    class_name = prediction[0] # 여기를 DB로 넘김
                    print("클래스 : ", class_name)
                
                    now_ymd = datetime.now().strftime('%Y.%m.%d')
                    now_hms = datetime.now().strftime('%H:%M:%S')
                    print("오늘 날짜 : ", now_ymd)
                    print("현재 시간 : ", now_hms)
                    PostureDetection.objects.create(user=request.user, timeymd=now_ymd, timehms=now_hms, posturetype=class_name)

                else:
                    # 가시성이 낮을 때는 대기 메시지 표시
                    class_name = -1
                    now_ymd = datetime.now().strftime('%Y.%m.%d')
                    now_hms = datetime.now().strftime('%H:%M:%S')
                    PostureDetection.objects.create(user=request.user, timeymd=now_ymd, timehms=now_hms, posturetype=class_name)

                context = {'class_name':str(class_name)}
        return JsonResponse(context)
    
@login_required(login_url='accounts:login')
def send_image_game(request):
    if request.method == 'POST':
        image_file = request.FILES.get('img_file')
        mp_holistic = mp.solutions.holistic
        display_text = "Waiting..."
 
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            if image_file:
                nparr = np.fromstring(image_file.read(), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)

                visibility = [landmark.visibility for landmark in results.pose_landmarks.landmark] if results.pose_landmarks else []
                avg_visibility = np.mean(visibility) if visibility else 0

                if avg_visibility > 0.4:  # 사람이 화면에 있을 경우
                    pose_landmarks = results.pose_landmarks.landmark
                    row = []
                    
                    # 1. landmark positions and visibility
                    for i in stretching_selected_landmarks:
                        landmark = pose_landmarks[i]
                        row.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
                            
                    # 2. Calculate distances
                    distances = {}
                    for i, landmark_i in enumerate(stretching_selected_landmarks):
                        for j, landmark_j in enumerate(stretching_selected_landmarks[i+1:], start=i+1):
                            distance = calculate_distance([pose_landmarks[landmark_i].x, pose_landmarks[landmark_i].y, pose_landmarks[landmark_i].z],
                                                        [pose_landmarks[landmark_j].x, pose_landmarks[landmark_j].y, pose_landmarks[landmark_j].z])
                            row.append(distance)
                            distances[(landmark_i, landmark_j)] = distance
                    
                    reference_distance = distances.get('distance_between_left_eye_and_right_eye', 1)

                    # 3. Calculate relative distances
                    relative_distances = [distance / reference_distance for distance in distances.values()]
                    row.extend(relative_distances)
                    
                    # 4. Calculate relative landmark position(z)
                    for i in stretching_selected_landmarks:
                        landmark = pose_landmarks[i]    
                        row.append(landmark.z * reference_distance)
                    
                    # 5. Calculate angles
                    for i, landmark_i in enumerate(stretching_selected_landmarks):
                        for j, landmark_j in enumerate(stretching_selected_landmarks[i+1:], start=i+1):
                            for k, landmark_k in enumerate(stretching_selected_landmarks[j+1:], start=j+1):
                                angle = calculate_angle([pose_landmarks[landmark_i].x, pose_landmarks[landmark_i].y, pose_landmarks[landmark_i].z],
                                                        [pose_landmarks[landmark_j].x, pose_landmarks[landmark_j].y, pose_landmarks[landmark_j].z],
                                                        [pose_landmarks[landmark_k].x, pose_landmarks[landmark_k].y, pose_landmarks[landmark_k].z])
                                row.append(angle)                        

                    # 컬럼명 생성
                    csv_columns = [f'{landmark_description[i]}_{dim}' for i in stretching_selected_landmarks for dim in ['x', 'y', 'z', 'visibility']]
                    csv_columns += [f'distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(stretching_selected_landmarks) for j, landmark_j in enumerate(stretching_selected_landmarks[i+1:], start=i+1)]
                    csv_columns += [f'relative_distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(stretching_selected_landmarks) for j, landmark_j in enumerate(stretching_selected_landmarks[i+1:], start=i+1)]
                    csv_columns += [f'relative_{landmark_description[i]}_z' for i in stretching_selected_landmarks]
                    csv_columns += [f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}' for i, landmark_i in enumerate(stretching_selected_landmarks) for j, landmark_j in enumerate(stretching_selected_landmarks[i+1:], start=i+1) for k, landmark_k in enumerate(stretching_selected_landmarks[j+1:], start=j+1)]
                    
                    row_df = pd.DataFrame([row], columns=csv_columns) 
 
                    # 자세 예측
                    prediction = stretching_model.predict(row_df)
                    class_name = prediction[0]
                
                    now_ymd = datetime.now().strftime('%Y.%m.%d')
                    now_hms = datetime.now().strftime('%H:%M:%S')

                else:
                    # 가시성이 낮을 때는 대기 메시지 표시
                    class_name = -1
                    now_ymd = datetime.now().strftime('%Y.%m.%d')
                    now_hms = datetime.now().strftime('%H:%M:%S')

                context = {'class_name':str(class_name)}
        return JsonResponse(context)



@login_required(login_url='accounts:login')
def statistics(request):
    print('statistics request user : ', request.user)
    # 해당 유저의 자세 데이터 전체
    userdata = PostureDetection.objects.filter(user_id=request.user)
    # 오늘 날짜
    today = datetime.now().strftime('%Y.%m.%d')
    # 오늘 날짜에 해당되는 데이터 전체
    todaysposes = userdata.filter(timeymd=today)
    todayposecnt = todaysposes.count()
    
    # 바른 자세 데이터 수
    correctposecnt = todaysposes.filter(posturetype=0).count()
    # 나쁜 자세 데이터 수
    badposecnt = todaysposes.exclude(posturetype=0).count()
    
    # 자리에 있었던 데이터 수
    inplacecnt = todaysposes.exclude(posturetype=-1).count()
    # 자리를 비운 데이터 수
    missedplacecnt = todaysposes.filter(posturetype=-1).count()
    # 여기서 todayposecnt가 0인 경우를 처리해야 합니다.
    if todayposecnt > 0:
        correct_posture_ratio = round((correctposecnt / todayposecnt), 2)
        incorrect_posture_ratio = round((badposecnt / todayposecnt), 2)
        person_in_place_ratio = round((inplacecnt / todayposecnt), 2)
        person_missed_place_ratio = round((missedplacecnt / todayposecnt), 2)
    else:
        # todayposecnt가 0인 경우, 모든 비율을 0으로 설정
        correct_posture_ratio = 0
        incorrect_posture_ratio = 0
        person_in_place_ratio = 0
        person_missed_place_ratio = 0
    
    # Count for each posture type
    posture1_cnt = todaysposes.filter(posturetype=1).count()
    posture2_cnt = todaysposes.filter(posturetype=2).count()
    posture3_cnt = todaysposes.filter(posturetype=3).count()
    posture4_cnt = todaysposes.filter(posturetype=4).count()
    
    
    # 오늘 기준 지난 일주일 데이터
    correctWeek, badWeek, weekDate = weekData(userdata)
    correctWeek = list(map(str, correctWeek))
    badWeek = list(map(str, badWeek))
    
    # 리스트 - 문자열 변환
    correctWeek = ','.join(correctWeek)
    badWeek = ','.join(badWeek)
    weekDate = ','.join(weekDate)
    
    # 오늘 총 이용 시간
    totalUsageTime = round((todayposecnt / 1200), 2)
    

    context = {
        # 'posture_type_num':posture_type_cnt,
        'correct_posture_ratio': correct_posture_ratio,
        'incorrect_posture_ratio': incorrect_posture_ratio,
        'today_posture_cnt': todayposecnt,
        'correct_posture_cnt': correctposecnt,
        'bad_posture_cnt': badposecnt,
        'person_in_place_ratio': person_in_place_ratio,
        'person_missed_place_ratio': person_missed_place_ratio,
        'posture1_cnt': posture1_cnt,
        'posture2_cnt': posture2_cnt,
        'posture3_cnt': posture3_cnt,
        'posture4_cnt': posture4_cnt,
        'correct_week' : correctWeek,
        'bad_week' : badWeek,
        'week_date' : weekDate,
        'today_usage_t' : totalUsageTime,
    }
    return render(request, 'service/statistics.html', context)

    
    
def test(request):
    return render(request, 'service/test.html')

def weekData(data):
    # today = datetime.now().strftime('%Y.%m.%d')
    today = datetime.now()
    badWeek = []
    correctWeek = []
    weekDate = []
    for i in range(0, 7):
        day = today - timedelta(days=i) # 1-7일 전
        day2 = day.strftime('%Y.%m.%d')
        posesData = data.filter(timeymd=day2) # 해당 날짜 데이터 전체
        
        # 해당 날짜 데이터 전체 개수
        posesDataCnt = posesData.count()
        # 바른 자세 데이터 수
        correctposecnt = posesData.filter(posturetype=0).count()
        # 나쁜 자세 데이터 수
        badposecnt = posesData.exclude(posturetype=0).count()
        
        if posesDataCnt > 0:
            correct_posture_ratio = round((correctposecnt / posesDataCnt), 2)
            incorrect_posture_ratio = round((badposecnt / posesDataCnt), 2)
        else:
            # todayposecnt가 0인 경우, 모든 비율을 0으로 설정
            correct_posture_ratio = 0
            incorrect_posture_ratio = 0
        
        # 리스트에 데이터 추가
        correctWeek.insert(0, correct_posture_ratio)
        badWeek.insert(0, incorrect_posture_ratio)
        weekDate.insert(0,day.strftime('%m/%d'))
        
    return correctWeek, badWeek, weekDate
