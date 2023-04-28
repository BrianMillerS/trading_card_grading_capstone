#!/bin/bash

# Specify the directory path
directory="/Users/brianmiller/Desktop/trading_card_data/verified_data"

# Step 1: Create new folders if they don't exist
mkdir -p "$directory"/psa{1..10}

# Step 2: Move files into the correct folders
for file in "$directory"/card*_PSA*; do
    b="${file#*_PSA}"
    mv "$file" "$directory/psa${b%.*}"
done
