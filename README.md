<p align="center">
    <img src="readme_photos/CNN_white.png" width="75%" height="75%">
</p>

<h1 align="center">Automated Grading of Baseball Trading Cards using Convolutional Neural Networks</h1>  

# Table of contents
- [Project Takeaway](#Project-Takeaway)
- [Description of the Data](#Description-of-the-Data)
- [Methods Overview](#methods-overview)
- [Project Summary](#project-summary)
- [Descriptions of Files in Repo](#Descriptions-of-Files-in-Repo)

# Project Takeaway
For my masters capstone I built a neural network to automate the manual card grading process done by companies such as [PSA](https://www.psacard.com/services/tradingcardgrading). Card holders now no longer need to ship their valuable cards off and pay top prices for a manual professional grade. This model allows users to get instanteneous card grades from just a snap of their phone camera.

 - The model performed well, assigning new cards a grade score with 76% accuracy, with a variance of +/- 1.2 grades.
 - The model was trained on 10k labeled images with professional scores from PSA, which underwent rigorous cleaning: image selection, image cropping, and image augmentation.
 - Neural network design was essential. Built on top of RESNET-50, many decisions were made: number of dense layers, pooling method, activation functions, freezing layers while training, batch size, learning rate, dropout rate.

![alt text](readme_photos/CNN_diagram.png)

Using this model, I founded **Card Grade AI, LLC** Our app allows users to get instant card grades, and host a virtual portfolio of thier collection. Tt is currently in progress. For this reason the training data and final ML model are not on this repo, and are considered proprietary.

# Description of the Data

All 10k cards were scraped from [Collectors.com](https://www.collectors.com/trading-cards/sport-baseball-cards/20003?lowgrade=1&highgrade=10&gradingservice=2&page=1) using beautiful soup

# Methods Overview


# Project Summary
- [Exploratory Data Analysis](#xploratory-Data-Analysis)
- [Data Collection](#Data-Collection)
- [Data Cleaning](#Data-Cleaning)
- [Data Standardization and Augmentation](#Data-Standardization-and-Augmentation)
- [Neural Network Model Building](#Neural-Network-Model-Building)
- [Model Evaluation](#Model-Evaluation)

## Exploratory Data Analysis

<img src="readme_photos/eda_new_cards_better_grade.png" width="810" height="518">
<img src="readme_photos/eda_card_age.png" width="703" height="550">
<img src="readme_photos/eda_card_price_age.png" width="712" height="457">

## Data Collection

<img src="readme_photos/eda_data_sources.png" width="704" height="508">
<img src="readme_photos/website_example.png" width="380" height="558">

## Data Cleaning

<img src="readme_photos/good_examples.png" width="133%" height="133%">
<img src="readme_photos/bad_examples.png" width="133%" height="133%">

## Data Standardization and Augmentation

<img src="readme_photos/image_cropping.png" width="702" height="453">
<img src="readme_photos/dataset_balancing.png" width="133%" height="133%">
<img src="readme_photos/pixel_distribution.png" width="133%" height="133%">
<img src="readme_photos/image_augmentation.png" width="133%" height="133%">

## Neural Network Model Building

- ResNet-50 feeds into three fully connected ReLU dense layers [1024, 512, 128]  
- The dense layers feed into a single softmax prediction layer  

Two rounds of training were done:
- First Round: 15 epochs, freeze first 20 layers of ResNet-50
- Second Round: 15 epochs, unfreeze all layers
  
<img src="readme_photos/CNN_diagram_complex.png" width="133%" height="133%">



## Model Evaluation

The condition of a trading card significantly influences its worth. However, the current methods to assess a card's condition are insufficient. Non-professionals often lack the accuracy required for card grading, and obtaining professional evaluations is too expensive and time-consuming.

This project aims to automate the card grading process using machine learning. Our neural network utilizes the pretained model ResNet-50 
combined with custom classification and output layers. 


# Descriptions of Files in Repo
![TREE](readme_photos/TREE.png)














