import cv2
import mediapipe as mp
import joblib
import numpy as np
import pandas as pd
from AI.Posture_Classification.Data_Processing.preprocessing import calculate_angle, calculate_distance, selected_landmarks, landmark_description
from django.http import FileResponse

def send_image(request):
    if request.method == 'POST':
        image_file = request.FILES.get('img_file')
        mp_holistic = mp.solutions.holistic
        model = joblib.load('pose_classification_model.pkl')

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
                    csv_columns += [f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1) for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1)]
                    
                    row_df = pd.DataFrame([row], columns=csv_columns) 
                    row_df.to_csv('test.csv')

                    # RandomForest 모델을 사용하여 자세 예측
                    prediction = model.predict(row_df)
                    class_name = prediction[0]
                    
                    if class_name == 0:
                        message = "good posture"
                    else:
                        message = 'bad posture'
                    
                    display_text = f'Pose: {message}'
                else:
                    display_text = "Waiting..."
                    
                processed_image_path = "path/to/save/processed_image.png"
                cv2.imwrite(processed_image_path, frame) 
        return FileResponse(open(processed_image_path, 'rb'), content_type='image/png')
