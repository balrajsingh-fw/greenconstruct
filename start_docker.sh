set -e  # stop if any command fails

echo "Remove existing docker container"
docker stop green_construct_container
docker rm green_construct_container

echo "🔹 Building Docker image..."
docker build -t greenconstructapp .

echo "🔹 Running Docker container..."
docker run -d --name green_construct_container -p 8041:8041 mydjangoapp