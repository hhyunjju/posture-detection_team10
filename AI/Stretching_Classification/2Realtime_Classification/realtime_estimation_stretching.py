import cv2
import mediapipe as mp
import joblib
import numpy as np
import pandas as pd
import time
from AI.Posture_Classification.Data_Processing.preprocessing import calculate_angle, calculate_distance, selected_landmarks, landmark_description

mp_holistic = mp.solutions.holistic

model = joblib.load('pose_classification_model.pkl')

# 웹캠 설정
cap = cv2.VideoCapture(0)

desired_width = 1280
desired_height = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)


prev_time = 0
interval = 0.3  # 0.3초 간격

display_text = "Waiting..."

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue
        
        # frame = cv2.flip(frame, 1)
        current_time = time.time()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)

        visibility = [landmark.visibility for landmark in results.pose_landmarks.landmark] if results.pose_landmarks else []
        avg_visibility = np.mean(visibility) if visibility else 0

        # 0.3초 간격
        if (current_time - prev_time) > interval:
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

                # 3. Calculate relative distances
                reference_distance = distances.get('distance_between_left_eye_and_right_eye', 1) 

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

                # 컬럼명
                csv_columns = [f'{landmark_description[i]}_{dim}' for i in selected_landmarks for dim in ['x', 'y', 'z', 'visibility']]
                csv_columns += [f'distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
                csv_columns += [f'relative_distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
                csv_columns += [f'relative_{landmark_description[i]}_z' for i in selected_landmarks]
                csv_columns += [f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1) for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1)]
                
                row_df = pd.DataFrame([row], columns=csv_columns) 
                row_df.to_csv('test.csv')

                # 자세 예측
                prediction = model.predict(row_df)
                class_name = prediction[0]

                print(prediction[0])
                
                if class_name == 0:
                    message = "good posture"
                else:
                    message = 'bad posture'
                
                display_text = f'Pose: {message}'

                prev_time = current_time
            else:
                display_text = "Waiting..."  

        cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Pose Classification', frame)
        
        # ESC 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break 
        
cap.release()
cv2.destroyAllWindows()
