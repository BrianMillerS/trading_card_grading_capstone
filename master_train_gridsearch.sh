#!/bin/bash

# Path to the data
base_path="/home/data/data_for_model_3"

# Number of epochs
n_epochs_list=(35 50)

# Drop rates
droprates=(0 0.012 0.025 0.05 0.1 0.2)

# Learning rates for dense layers
lr_denses=(0.0001 0.0005 0.001)

# Batch sizes
batch_sizes=(16)

# Units in the dense layers
dense1_units_list=(512 1024 2048)
dense2_units_list=(256 512 1024)
dense3_units_list=(64 128 256)

# After how many layers from the last of the ResNet50 should the layers be trainable
unfreeze_after_list=(10 20 30)

# Export variables to be used by parallel
export base_path

# Define the function that will be run in parallel
run_experiment() {
  n_epochs=$1
  droprate=$2
  lr_dense=$3
  batch_size=$4
  dense1_units=$5
  dense2_units=$6
  dense3_units=$7
  unfreeze_after=$8

  # Run the Python script with the current combination of parameters
  python RESNET-50.py \
    --n_epochs $n_epochs \
    --base_path $base_path \
    --droprate $droprate \
    --lr_dense $lr_dense \
    --batch_size $batch_size \
    --dense1_units $dense1_units \
    --dense2_units $dense2_units \
    --dense3_units $dense3_units \
    --unfreeze_after $unfreeze_after
}

# Export the function so it can be used by parallel
export -f run_experiment

# Use GNU parallel to run the experiments in parallel
parallel -j 6 run_experiment ::: "${n_epochs_list[@]}" ::: "${droprates[@]}" ::: "${lr_denses[@]}" ::: "${batch_sizes[@]}" ::: "${dense1_units_list[@]}" ::: "${dense2_units_list[@]}" ::: "${dense3_units_list[@]}" ::: "${unfreeze_after_list[@]}"