
docker stop n8n
docker rm n8n

docker pull docker.n8n.io/n8nio/n8n


docker run -d  --name n8n  -p 5678:5678  -e GENERIC_TIMEZONE="America/New_York"  -e TZ="America/New_York"  -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true  -e N8N_RUNNERS_ENABLED=true  -e N8N_SECURE_COOKIE=false  -v n8n_data:/home/node/.n8n  --restart unless-stopped  docker.n8n.io/n8nio/n8n
