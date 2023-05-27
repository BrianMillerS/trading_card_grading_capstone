# Automated Grading of Baseball Trading Cards using Convolutional Neural Networks

**Authors:**  
- Brian Miller (brian.s.miller@du.edu)
- Sean Wendlandt (sean.wendlandt@du.edu)

## Project Overview

## Description of Files
.  
├── RESNET-50.py                         # main CNN training script.  
├── terminal_output_copy_model3.txt      # copy of latest modeling attempt.  
├── eda.ipynb                            # exploratory data analysis notebook.  
├── make_balanced_dataset.ipynb          # selects balanced dataset after manual QC.  
├── make_metadata_file.ipynb             # selects 30k photos from scraped data.  
├── data_processing                       
│&nbsp;&nbsp;&nbsp;├── image_cropping.py                # removed PSA label from photo.   
│&#32;&#32;&#32;├── image_augmentation_flip.py       # makes flipped copy of photo for training data.   
└── web_scraping                         
&#32;&#32;&#32;&#32;├── master_collectors_scrape.sh      # bash script to call scrape_collections.py   
&#32;&#32;&#32;&#32;└── scrape_collections.py            # main web scraping script.  


This is some text<span style="white-space: pre;">                    </span>with 20 spaces.
