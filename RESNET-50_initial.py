import os
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.layers import Dense, Flatten

# Define paths
base_path = r'C:\Users\Seanw\OneDrive\Desktop\Capstone_Project\data_for_model_1\data_for_model_1'
train_path = os.path.join(base_path, 'train')
test_path = os.path.join(base_path, 'test')

# Create train/test directories
os.makedirs(train_path, exist_ok=True)
os.makedirs(test_path, exist_ok=True)

# Define train/test split ratio
split_ratio = 0.8

# Loop through all images and split them into train/test directories
for file_name in os.listdir(base_path):
    if file_name.endswith('.jpg'):
        file_path = os.path.join(base_path, file_name)
        label = int(file_name.split('_PSA')[1].split('_')[0])  # extract PSA grade from file name
        dir_name = 'train' if random.random() < split_ratio else 'test'
        dir_path = os.path.join(base_path, dir_name, str(label))
        os.makedirs(dir_path, exist_ok=True)
        os.rename(file_path, os.path.join(dir_path, file_name))

# Define data generators for train/test sets
train_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_path,
    target_size=(400, 600),
    batch_size=32,
    class_mode='categorical')

test_generator = test_datagen.flow_from_directory(
    test_path,
    target_size=(400, 600),
    batch_size=32,
    class_mode='categorical')

# Load pre-trained RESNET-50 model
resnet50_model = ResNet50(weights='imagenet', include_top=False, input_shape=(400, 600, 3))

# Freeze all layers except the last convolutional block
for layer in resnet50_model.layers[:-20]:
    layer.trainable = False

# Add custom dense layer
x = resnet50_model.output
x = Flatten()(x)
x = Dense(1024, activation='relu')(x)
x = Dense(512, activation='relu')(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(10, activation='softmax')(x)

# Create final model
model = tf.keras.Model(inputs=resnet50_model.input, outputs=predictions)

# Compile model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train model
model.fit(train_generator, epochs=10, validation_data=test_generator)
