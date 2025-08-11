#!/bin/bash
# araqode-archive
# A curated, multi-modal dataset

# Pull and extract dataset from Docker image
# ------------------------------------------

# --- CONFIGURE THESE VARIABLES ---
IMAGE="araqode/araqode-archive:latest"
LOCAL_DIR="./dataset"

# --- SCRIPT STARTS HERE ---
set -e

# Pull the image
docker pull "$IMAGE"

# Create a temp container
CONTAINER_ID=$(docker create "$IMAGE")

# Copy dataset from container to local directory
mkdir -p "$LOCAL_DIR"
docker cp "${CONTAINER_ID}:/araqode-archive/." "$LOCAL_DIR"

# Clean up
docker rm "$CONTAINER_ID"

echo "Dataset extracted to $LOCAL_DIR"