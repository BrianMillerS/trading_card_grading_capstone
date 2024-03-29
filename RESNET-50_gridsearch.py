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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script to train and evaluate a model.')
    parser.add_argument('-e', '--n_epochs', type=int, default=10,
                        help='Number of epochs per training cycles (positive integer)')
    parser.add_argument('-b', '--base_path', type=str, required=True,
                        help='The base path for the data folder containing both /train and /test folders')
    parser.add_argument('-d', '--droprate', type=float, default=0.012,
                        help='The droprate for the dropout layers (float between 0 and 1)')
    parser.add_argument('--lr_dense', type=float, default=0.0001,
                        help='Learning rate for dense layers')
    parser.add_argument('--batch_size', type=int, default=16,
                        help='Batch size for training and validation data')
    parser.add_argument('--dense1_units', type=int, default=1024,
                        help='Number of units in the first additional dense layer')
    parser.add_argument('--dense2_units', type=int, default=512,
                        help='Number of units in the second additional dense layer')
    parser.add_argument('--dense3_units', type=int, default=128,
                        help='Number of units in the third additional dense layer')
    parser.add_argument('--unfreeze_after', type=int, default=20,
                        help='After how many layers from the last of the ResNet50 should the layers be trainable')
    return parser.parse_args()

args = parse_arguments()
n_epochs = args.n_epochs
base_path = args.base_path
droprate = args.droprate
learning_rate_dense_layers = args.lr_dense
batch_size = args.batch_size
dense1_units = args.dense1_units
dense2_units = args.dense2_units
dense3_units = args.dense3_units
unfreeze_after = args.unfreeze_after

train_path = os.path.join(base_path, 'train')
test_path = os.path.join(base_path, 'test')

log_dir = os.path.join(os.getcwd(), 'logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
os.makedirs(log_dir, exist_ok=True)

os.makedirs(train_path, exist_ok=True)
os.makedirs(test_path, exist_ok=True)

split_ratio = 0.8

for file_name in os.listdir(base_path):
    if file_name.endswith('.jpg'):
        file_path = os.path.join(base_path, file_name)
        label = int(file_name.split('_PSA')[1].split('_')[0])
        dir_name = 'train' if random.random() < split_ratio else 'test'
        dir_path = os.path.join(base_path, dir_name, str(label))
        os.makedirs(dir_path, exist_ok=True)
        os.rename(file_path, os.path.join(dir_path, file_name))

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest')

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_path,
    target_size=(400, 600),
    batch_size=batch_size,
    class_mode='categorical')

test_generator = test_datagen.flow_from_directory(
    test_path,
    target_size=(400, 600),
    batch_size=batch_size,
    class_mode='categorical')

class CustomCSVLogger(tf.keras.callbacks.CSVLogger):
    def __init__(self, filename, learning_rate, dropout_rate, append=False, separator=','):
        super().__init__(filename, separator=separator, append=append)
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        logs['lr'] = self.learning_rate
        logs['drop_rate'] = self.dropout_rate
        self.keys = sorted(logs.keys())
        super().on_epoch_end(epoch, logs)

csv_logger = CustomCSVLogger(os.path.join(log_dir, 'log.csv'), learning_rate_dense_layers, droprate, append=True)

resnet50_model = ResNet50(weights='imagenet', include_top=False, input_shape=(400, 600, 3))

for layer in resnet50_model.layers[:-20]:
    layer.trainable = False

x = resnet50_model.output
x = Flatten()(x)
x = Dense(dense1_units, activation='relu')(x)
x = Dropout(droprate)(x)
x = Dense(dense2_units, activation='relu')(x)
x = Dropout(droprate)(x)
x = Dense(dense3_units, activation='relu')(x)

predictions = Dense(10, activation='softmax')(x)

model = tf.keras.Model(inputs=resnet50_model.input, outputs=predictions)

model.compile(optimizer=Adam(lr=learning_rate_dense_layers), loss='categorical_crossentropy', metrics=['accuracy', Precision(), Recall()])

model.fit(train_generator, epochs=n_epochs, validation_data=test_generator, callbacks=[csv_logger])

for layer in resnet50_model.layers[:-unfreeze_after]:
    layer.trainable = False

model.compile(optimizer=Adam(lr=learning_rate_dense_layers), loss='categorical_crossentropy', metrics=['accuracy', Precision(), Recall()])

history = model.fit(train_generator, epochs=n_epochs, validation_data=test_generator, callbacks=[csv_logger])

history_clean_keys = {re.sub(r'_\d+', '', key): value for key, value in history.history.items()}
final_train_accuracy = history_clean_keys['accuracy'][-1]
final_train_precision = history_clean_keys['precision'][-1]
final_train_recall = history_clean_keys['recall'][-1]
final_test_xval_accuracy = history_clean_keys['val_accuracy'][-1]
final_test_xval_precision = history_clean_keys['val_precision'][-1]
final_test_xval_recall = history_clean_keys['val_recall'][-1]

test_images, true_labels = next(test_generator)
predictions = model.predict(test_images)
predicted_labels = np.argmax(predictions, axis=1)
true_labels = np.argmax(true_labels, axis=1)

absolute_diffs = np.abs(predicted_labels - true_labels)
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
