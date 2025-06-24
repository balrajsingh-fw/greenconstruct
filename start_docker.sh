set -e  # stop if any command fails

echo "🔹 Building Docker image..."
docker build -t mydjangoapp .

echo "🔹 Running Docker container..."
docker run -d --name mydjango_container -p 3003:3003 mydjangoapp