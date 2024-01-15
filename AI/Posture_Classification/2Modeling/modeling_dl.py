import tensorflow
from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, Activation, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
import matplotlib.pyplot as plt

data = pd.read_csv("csv파일 경로 입력") 

X = data.drop(columns=['file_name', 'label'])  
y = data['label']  

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

n_features = X_train.shape[1]  
n_classes = 7    

# 모델
model = Sequential([
    Dense(128, input_shape=(n_features,)),
    BatchNormalization(),  
    Activation('relu'), 
    Dropout(0.3),  
    Dense(256),
    BatchNormalization(),
    Activation('relu'),
    Dropout(0.3),
    Dense(n_classes, activation='softmax')  
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

early_stopping = EarlyStopping(monitor='val_loss', patience=5)
model_checkpoint = ModelCheckpoint('best_model.h5', save_best_only=True)

model.summary()

model.fit(X_train, y_train, validation_split = 0.2, epochs=100, callbacks=[early_stopping, model_checkpoint])
