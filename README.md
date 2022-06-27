# PORGhub 😂

Jak nasadit:

```bash
docker build -t porghub .

docker run -d -v $(pwd)/attachments:/app/attachments -v $(pwd)/data:/app/data -p $PORT:80 --name porghub porghub
```