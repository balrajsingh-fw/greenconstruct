set -e  # stop if any command fails

echo "Remove existing docker container"
docker stop mydjango_container
docker rm mydjango_container

echo "🔹 Building Docker image..."
docker build -t mydjangoapp .

echo "🔹 Running Docker container..."
docker run -d --name mydjango_container -p 8041:8041 mydjangoapp