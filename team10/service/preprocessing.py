import csv
import cv2
import numpy as np
import os
import mediapipe as mp


selected_landmarks = [0, 2, 5, 7, 8, 11, 12, 15, 16]

landmark_description = [
"nose", "left_eye_inner", "left_eye", "left_eye_outer", 
"right_eye_inner", "right_eye", "right_eye_outer", "left_ear", 
"right_ear", "mouth_left", "mouth_right", "left_shoulder", 
"right_shoulder", "left_elbow", "right_elbow", "left_wrist", 
"right_wrist", "left_pinky", "right_pinky", "left_index", 
"right_index", "left_thumb", "right_thumb", 
"left_hip", 
"right_hip", "left_knee", "right_knee", "left_ankle", 
"right_ankle", "left_heel", "right_heel", "left_foot_index", 
"right_foot_index"
]

# Function to calculate the Euclidean distance between two points.
def calculate_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a-b)

# Function to calculate the angle between three points.
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

def process_images_from_folder(folder_path, writer, label):
    # MediaPipe Holistic 객체를 한 번만 생성하여 사용
    mp_holistic = mp.solutions.holistic.Holistic(static_image_mode=True, model_complexity=2,
                                                enable_segmentation=True, refine_face_landmarks=True)
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files.
            image = cv2.imread(file_path)
            if image is None:
                print(f"Failed to read image {file_name}. Skipping...")
                continue  # Skip this file if the image cannot be read.

            try:
                results = mp_holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    row_data = {'file_name': file_name, 'label': label}
                    
                    # Record selected landmark positions and visibility with descriptive names
                    for i in selected_landmarks:
                        landmark = landmarks[i]
                        row_data[f'{landmark_description[i]}_x'] = landmark.x
                        row_data[f'{landmark_description[i]}_y'] = landmark.y
                        row_data[f'{landmark_description[i]}_z'] = landmark.z
                        row_data[f'{landmark_description[i]}_visibility'] = landmark.visibility

                    # Calculate and record distances between each pair of selected landmarks
                    distance_values = {}
                    for i, landmark_i in enumerate(selected_landmarks):
                        for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1):
                            distance = calculate_distance([landmarks[landmark_i].x, landmarks[landmark_i].y, landmarks[landmark_i].z],
                                                        [landmarks[landmark_j].x, landmarks[landmark_j].y, landmarks[landmark_j].z])
                            distance_key = f'distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}'
                            row_data[distance_key] = distance
                            distance_values[distance_key] = distance

                    # 상대적인 길이 값 계산을 위한 기준 설정
                    reference_distance = distance_values.get('distance_between_left_eye_and_right_eye', 1)  # 기준 거리를 nose와 right_ear 사이의 거리로 설정합니다.

                    # 상대적인 길이 값 계산 및 CSV에 추가
                    for distance_key, distance_value in distance_values.items():
                        relative_distance_key = f'relative_{distance_key}'
                        row_data[relative_distance_key] = distance_value / reference_distance  # 상대적인 길이 값을 계산하여 추가
                        
                        
                    # Calculate and record angles among triplets of selected landmarks
                    for i, landmark_i in enumerate(selected_landmarks):
                        for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1):
                            for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1):
                                angle = calculate_angle([landmarks[landmark_i].x, landmarks[landmark_i].y, landmarks[landmark_i].z],
                                                        [landmarks[landmark_j].x, landmarks[landmark_j].y, landmarks[landmark_j].z],
                                                        [landmarks[landmark_k].x, landmarks[landmark_k].y, landmarks[landmark_k].z])
                                row_data[f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}'] = angle

                    writer.writerow(row_data)  # Write the row data for this image
            except Exception as e:
                print(f"Error processing image {file_name}: {e}")