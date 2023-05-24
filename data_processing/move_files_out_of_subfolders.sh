#!/bin/bash

for folder in psa{1..10}; do
    if [[ -d "$folder" ]]; then
        echo "Moving files from $folder to parent directory"
        mv "$folder"/* .
    fi
done
