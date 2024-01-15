import os
import cv2
import albumentations as A

# 데이터 증강을 위한 함수
def augment_image(image):
    augmenter = A.Compose([
        A.HorizontalFlip(p=0.3),  # 30% 확률로 수평 뒤집기
        A.Rotate(limit=30, p=0.9),  # -30도에서 +30도 사이로 회전
        A.RandomBrightnessContrast(p=0.2),  # 밝기 및 대비 조절
    ])
    augmented = augmenter(image=image)['image']
    return augmented

# 폴더 생성 함수
def create_directory_structure(base_path, sub_folders):
    augmented_path = os.path.join(base_path, 'augmented_images')
    if not os.path.exists(augmented_path):
        os.makedirs(augmented_path)
    
    for folder in sub_folders:
        label_path = os.path.join(augmented_path, folder)
        if not os.path.exists(label_path):
            os.makedirs(label_path)

# 이미지를 증강하고 저장하는 함수
def augment_and_save_images(input_folder, output_folder):
    sub_folders = [f.name for f in os.scandir(input_folder) if f.is_dir()]
    
    create_directory_structure(output_folder, sub_folders)

    for folder in sub_folders:
        input_subfolder = os.path.join(input_folder, folder)
        output_subfolder = os.path.join(output_folder, 'augmented_images', folder)

        for file_name in os.listdir(input_subfolder):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(input_subfolder, file_name)
                image = cv2.imread(file_path)
                if image is not None:
                    augmented_image = augment_image(image)
                    cv2.imwrite(os.path.join(output_subfolder, file_name), augmented_image)

# video가 저장될 경로 지정
if __name__ == "__main__":
    base_path = "저장할 base_path를 입력"
    test_folder = os.path.join(base_path, "세부폴더 입력")

    augment_and_save_images(test_folder, base_path)
