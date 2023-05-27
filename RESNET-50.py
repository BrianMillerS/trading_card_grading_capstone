import os
import re
import random
import numpy as np
import datetime
import argparse
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Precision, Recall
from tensorflow.keras import mixed_precision


#### USAGE ####
# python RESNET-50.py --n_epochs 50 --droprate 0.025 --base_path /home/data/data_for_model_3


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to train and evaluate a model.')
    parser.add_argument('-e', '--n_epochs', type=int, default=10,
                        help='Number of epochs per training cycles (positive integer)')
    parser.add_argument('-b', '--base_path', type=str, required=True,
                        help='The base path for the data folder containing both /train and /test folders')
    parser.add_argument('-d', '--droprate', type=float, default=0.012,
                        help='The droprate for the dropout layers (float between 0 and 1)')
    return parser.parse_args()

# get the droprate
args = parse_arguments()
n_epochs = args.n_epochs
base_path = args.base_path
droprate = args.droprate

# Enable mixed precision for performance improvement
# mixed_precision.set_global_policy('mixed_float16')

# Define the distribution strategy
# strategy = tf.distribute.MirroredStrategy()
# print("Number of GPUs: {}".format(strategy.num_replicas_in_sync))

#### USER INPUTS ####
learning_rate_dense_layers = 0.0001
#####################

# define the paths for the files
train_path = os.path.join(base_path, 'train')
test_path = os.path.join(base_path, 'test')

# Paths for Logging
log_dir = os.path.join(os.getcwd(), 'logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
os.makedirs(log_dir, exist_ok=True)

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
    batch_size=16,
    class_mode='categorical')

test_generator = test_datagen.flow_from_directory(
    test_path,
    target_size=(400, 600),
    batch_size=16,
    class_mode='categorical')

class CustomCSVLogger(tf.keras.callbacks.CSVLogger):
    def __init__(self, filename, learning_rate, dropout_rate, append=False, separator=','):
        super().__init__(filename, separator=separator, append=append)
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}

        # Add custom learning rate and dropout rate logs
        logs['lr'] = self.learning_rate
        logs['drop_rate'] = self.dropout_rate

        # Update the self.keys list to include the keys in the logs dictionary
        self.keys = sorted(logs.keys())

        super().on_epoch_end(epoch, logs)


# define a log
csv_logger = CustomCSVLogger(os.path.join(log_dir, 'log.csv'), learning_rate_dense_layers, droprate, append=True)

# Load pre-trained RESNET-50 model
resnet50_model = ResNet50(weights='imagenet', include_top=False, input_shape=(400, 600, 3))

# Freeze all layers except the last convolutional block
for layer in resnet50_model.layers[:-20]:
    layer.trainable = False

# Add custom dense layer
x = resnet50_model.output
x = Flatten()(x)
x = Dense(1024, activation='relu')(x)

# Add dropout layer with the current droprate after the 1024-node layer
x = Dropout(droprate)(x)  # get the original model to make changes to
x = Dense(512, activation='relu')(x)

# Add dropout layer with the current droprate after the 512-node layer
x = Dropout(droprate)(x)
x = Dense(128, activation='relu')(x)

# Add a prediction layer
predictions = Dense(10, activation='softmax')(x)

# Create final model
model = tf.keras.Model(inputs=resnet50_model.input, outputs=predictions)

# Compile model
model.compile(optimizer=Adam(lr=learning_rate_dense_layers), loss='categorical_crossentropy', metrics=['accuracy', Precision(), Recall()])

# Train model for the first round (freezing ResNet50 layers)
model.fit(train_generator, epochs=n_epochs, validation_data=test_generator, callbacks=[csv_logger])

# Unfreeze ResNet50 for the second round
for layer in resnet50_model.layers[:-50]:
    layer.trainable = False

# Recompile model with lower learning rate
model.compile(optimizer=Adam(lr=learning_rate_dense_layers), loss='categorical_crossentropy', metrics=['accuracy', Precision(), Recall()])

# Train model for the second round (unfreezing some ResNet50 layers)
history = model.fit(train_generator, epochs=n_epochs, validation_data=test_generator, callbacks=[csv_logger])

##  print final accuracy and precison metrics for each fully trained model (20 epochs total) ##
history_clean_keys = {re.sub(r'_\d+', '', key): value for key, value in history.history.items()}

# get accuracy metrics
final_train_accuracy = history_clean_keys['accuracy'][-1]
final_train_precision = history_clean_keys['precision'][-1]
final_train_recall = history_clean_keys['recall'][-1]
final_test_xval_accuracy = history_clean_keys['val_accuracy'][-1]
final_test_xval_precision = history_clean_keys['val_precision'][-1]
final_test_xval_recall = history_clean_keys['val_recall'][-1]
    
# get precision metrics

# Get a batch of test images and their true labels
test_images, true_labels = next(test_generator)

# Make predictions for the test images
predictions = model.predict(test_images)

# Get the class with the highest probability for each prediction
predicted_labels = np.argmax(predictions, axis=1)

# Convert true_labels from one-hot encoded to class indices
true_labels = np.argmax(true_labels, axis=1)

# Calculate the absolute differences between the predicted and true labels
absolute_diffs = np.abs(predicted_labels - true_labels)

# Calculate the mean and median absolute differences
mean_diff = np.mean(absolute_diffs)
median_diff = np.median(absolute_diffs)

print("Model Summary: [ lr = {} ,droprate = {} ]".format(learning_rate_dense_layers, droprate))
print("Train Accuracy:  {}".format(final_train_accuracy))
print("Train Precision: {}".format(final_train_precision))
print("Train Recall:    {}".format(final_train_recall))
print("Test Accuracy (Xval):  {}".format(final_test_xval_accuracy))
print("Test Precision (Xval): {}".format(final_test_xval_precision))
print("Test Recall (Xval):    {}".format(final_test_xval_recall))
print("Grade Differential (mean):   {}".format(mean_diff))
print("Grade Differential (median): {}\n".format(median_diff))
