# -*- coding: utf-8 -*-
"""Copy of l05c03_exercise_flowers_with_data_augmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TJ0qS0ybR8iQ6VabsjkAUnDD52G0YTok

# Importing Packages
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import numpy as np
import glob
import shutil
import matplotlib.pyplot as plt

import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator

"""# Data Loading

After downloading the dataset, we need to extract its contents.
"""

_URL = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"

zip_file = tf.keras.utils.get_file(origin=_URL,
                                   fname="flower_photos.tgz",
                                   extract=True)

base_dir = os.path.join(os.path.dirname(zip_file), 'flower_photos')

"""The dataset we downloaded contains images of 5 types of flowers:

1. Rose
2. Daisy
3. Dandelion
4. Sunflowers
5. Tulips

So, let's create the labels for these 5 classes:
"""

classes = ['roses', 'daisy', 'dandelion', 'sunflowers', 'tulips']

for cl in classes:
  img_path = os.path.join(base_dir, cl)
  images = glob.glob(img_path + '/*.jpg')
  print("{}: {} Images".format(cl, len(images)))
  train, val = images[:round(len(images)*0.8)], images[round(len(images)*0.8):]

  for t in train:
    if not os.path.exists(os.path.join(base_dir, 'train', cl)):
      os.makedirs(os.path.join(base_dir, 'train', cl))
    shutil.move(t, os.path.join(base_dir, 'train', cl))

  for v in val:
    if not os.path.exists(os.path.join(base_dir, 'val', cl)):
      os.makedirs(os.path.join(base_dir, 'val', cl))
    shutil.move(v, os.path.join(base_dir, 'val', cl))

"""For convenience, let us set up the path for the training and validation sets"""

train_dir = os.path.join(base_dir, 'train')
val_dir = os.path.join(base_dir, 'val')

"""# Data Augmentation

### Set Batch and Image Size

In the cell below, create a `batch_size` of 100 images and set a value to `IMG_SHAPE` such that our training data consists of images with width of 150 pixels and height of 150 pixels.
"""

batch_size = 110
IMG_SHAPE = 252

image_gen = ImageDataGenerator(horizontal_flip=True,rescale=1/255)

train_data_gen = image_gen.flow_from_directory(train_dir,
                                              batch_size = batch_size,shuffle=True, target_size=(IMG_SHAPE, IMG_SHAPE),)

"""Let's take 1 sample image from our training examples and repeat it 5 times so that the augmentation can be applied to the same image 5 times over randomly, to see the augmentation in action."""

# This function will plot images in the form of a grid with 1 row and 5 columns where images are placed in each column.
def plotImages(images_arr):
    fig, axes = plt.subplots(1, 5, figsize=(20,20))
    axes = axes.flatten()
    for img, ax in zip( images_arr, axes):
        ax.imshow(img)
    plt.tight_layout()
    plt.show()


augmented_images = [train_data_gen[0][0][0] for i in range(5)]
plotImages(augmented_images)

image_gen_train = ImageDataGenerator(rotation_range=360,
                                     zoom_range=0.68, 
                                     horizontal_flip=True, 
                                     width_shift_range=0.15, 
                                     height_shift_range=0.15,
                                     rescale=1./255,
                                     fill_mode='reflect',
                                     featurewise_std_normalization=False,
                                     featurewise_center=False)

train_data_gen = image_gen_train.flow_from_directory(train_dir,
                                                    shuffle=True,
                                                    batch_size=batch_size,
                                                    target_size=(IMG_SHAPE,IMG_SHAPE), class_mode='sparse')

"""Let's visualize how a single image would look like 5 different times, when we pass these augmentations randomly to our dataset."""

augmented_images = [train_data_gen[0][0][0] for i in range(5)]
plotImages(augmented_images)

"""### Create a Data Generator for the Validation Set

Generally, we only apply data augmentation to our training examples. So, in the cell below, use ImageDataGenerator to create a transformation that only rescales the images by 255. Then use the `.flow_from_directory` method to apply the above transformation to the images in our validation set. Make sure you indicate the batch size, the path to the directory of the validation images, the target size for the images, and to set the class mode to `sparse`.
"""

image_gen_val = ImageDataGenerator(rescale=1/255)
val_data_gen = image_gen_val.flow_from_directory(val_dir,
                                                shuffle=True,
                                                batch_size=batch_size,
                                                target_size=(IMG_SHAPE,IMG_SHAPE), class_mode='sparse')

"""#  Create the CNN"""

model = tf.keras.Sequential([tf.keras.layers.Conv2D(32,(3,3), activation='relu', input_shape=(IMG_SHAPE,IMG_SHAPE, 3)),
                            tf.keras.layers.MaxPooling2D((2,2)),
                           tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
                           tf.keras.layers.MaxPooling2D((2,2)),
                           tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
                           tf.keras.layers.MaxPooling2D((2,2)),
                           tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
                           tf.keras.layers.MaxPooling2D((2,2)),
                           tf.keras.layers.Flatten(),
                           tf.keras.layers.Dropout(0.3),
                           tf.keras.layers.Dense(512, activation='relu'),
                           tf.keras.layers.Dropout(0.3),
                           tf.keras.layers.Dense(512, activation= 'relu'),
                           tf.keras.layers.Dropout(0.3),
                           tf.keras.layers.Dense(5, activation='softmax')])

"""# Compile the Model

In the cell below, compiling the model using the ADAM optimizer, the sparse cross entropy function as a loss function. We would also like to look at training and validation accuracy on each epoch as we train our network.
"""

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

"""# Train the Model

In the cell below, train the model using the **fit_generator** function instead of the usual **fit** function. We have to use the `fit_generator` function because we are using the **ImageDataGenerator** class to generate batches of training and validation data for the model.
"""

epochs = 70

history = model.fit_generator(train_data_gen, epochs=epochs, validation_data=val_data_gen, shuffle=True, steps_per_epoch=29, validation_steps=20)

"""# Plot Training and Validation Graphs.

In the cell below, plot the training and validation accuracy/loss graphs.
"""

acc = history.history['acc']
val_acc = history.history['val_acc']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()
