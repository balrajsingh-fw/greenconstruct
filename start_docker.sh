set -e  # stop on any real error

echo "🔹 Remove existing Docker container if it exists..."
docker stop green_construct_container 2>/dev/null || true
docker rm green_construct_container 2>/dev/null || true

echo "🔹 Building Docker image..."
docker build -t greenconstructapp .

echo "🔹 Running Docker container..."
docker run -d \
  --name green_construct_container \
  --restart=always \
  -p 8041:8041 \
  greenconstructapp
