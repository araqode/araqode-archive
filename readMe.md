# araqode-archive
A curated, multi-modal dataset

## Dockerized version
You can download and extract the dataset using the public Docker image.
This method does not require cloning the repository or running any Python code.

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) must be installed on your system.

### Steps
1. **Pull the Docker image:**
	```bash
	docker pull araqode/araqode-archive:latest
	```

2. **Extract the dataset from the image:**
	```bash
	CONTAINER_ID=$(docker create araqode/araqode-archive:latest)
	mkdir -p dataset
	docker cp ${CONTAINER_ID}:/araqode-archive/. ./dataset
	docker rm ${CONTAINER_ID}
	```
	This will copy the dataset to the `dataset` directory in your current folder.
