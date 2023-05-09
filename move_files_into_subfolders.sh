#!/bin/bash

# Specify the directory path
directory="/Users/brianmiller/Desktop/trading_card_data/verified_data/cropped_data"

# Step 1: Create new folders if they don't exist
mkdir -p "$directory"/psa{1..10}

# Step 2: Move files into the correct folders
for file in "$directory"/card*_PSA*_cropped.jpg; do
    b=$(basename "$file" | sed -n 's/.*_PSA\([0-9]*\)_cropped.jpg/\1/p')
    mv "$file" "$directory/psa${b}"
done
