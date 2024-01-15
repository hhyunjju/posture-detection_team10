import csv
import cv2
import numpy as np
import os
import mediapipe as mp
from AI.Posture_Classification.Data_Processing.preprocessing import calculate_distance, calculate_angle, process_images_from_folder, selected_landmarks, landmark_description


def data_acquisition():
    base_folder_path = "Base folder containing sub-folders"
    csv_file = "Path to save the CSV file" 

    # create CSV columns
    csv_columns = ['file_name', 'label']
    csv_columns += [f'{landmark_description[i]}_{dim}' for i in selected_landmarks for dim in ['x', 'y', 'z', 'visibility']]
    csv_columns += [f'distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
    csv_columns += [f'relative_distance_between_{landmark_description[landmark_i]}_and_{landmark_description[landmark_j]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1)]
    csv_columns += [f'relative_{landmark_description[i]}_z' for i in selected_landmarks]
    csv_columns += [f'angle_between_{landmark_description[landmark_i]}_{landmark_description[landmark_j]}_{landmark_description[landmark_k]}' for i, landmark_i in enumerate(selected_landmarks) for j, landmark_j in enumerate(selected_landmarks[i+1:], start=i+1) for k, landmark_k in enumerate(selected_landmarks[j+1:], start=j+1)]
    
    # make CSV file
    with open(csv_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns)
        writer.writeheader()

        sub_folders = [f.name for f in os.scandir(base_folder_path) if f.is_dir()]
        label_dict = {name: idx for idx, name in enumerate(sub_folders)}

        for sub_folder in sub_folders:
            full_folder_path = os.path.join(base_folder_path, sub_folder)
            process_images_from_folder(full_folder_path, writer, label_dict[sub_folder])

if __name__ == "__main__":
    data_acquisition()