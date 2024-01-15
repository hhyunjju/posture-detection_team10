from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
import pandas as pd
import joblib
import matplotlib.pyplot as plt

data = pd.read_csv("csv파일의 경로 입력") 

X = data.drop(columns=['file_name', 'label']) 
y = data['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Random Forest 모델
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# 모델 저장
joblib.dump(model, 'pose_classification_model.pkl')

accuracy = model.score(X_test, y_test)
print("Accuracy on Test Set: {:.2f}%".format(accuracy * 100))

# 특성 중요도 상위 20개 시각화
importances = model.feature_importances_
feature_names = X.columns
feature_importances = pd.DataFrame(zip(feature_names, importances), columns=['feature', 'importance']).sort_values('importance', ascending=False)

top_features = feature_importances.head(20)
plt.figure(figsize=(10, 6))
plt.title('Top 20 Feature Importances')
plt.barh(top_features['feature'], top_features['importance'], color='skyblue')
plt.xlabel('Importance')
plt.gca().invert_yaxis()  
plt.show()
print(top_features)

# Permutation Importance 계산
# perm_importance = permutation_importance(model, X_test, y_test, n_repeats=30, random_state=42)

# sorted_idx = perm_importance.importances_mean.argsort()[-10:]
# plt.figure(figsize=(10, 6))
# plt.barh(X.columns[sorted_idx], perm_importance.importances_mean[sorted_idx])
# plt.title("Top 20 Permutation Importance")
# plt.xlabel("Permutation Importance")
# plt.show()
# print(X.columns[sorted_idx])
# print(perm_importance.importances_mean[sorted_idx])
