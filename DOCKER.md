# 🐳 Docker Инструкция

Запуск сервиса с помощью Docker для изолированной и портативной среды.

## Преимущества Docker

✅ Не нужно устанавливать Python и зависимости  
✅ Изолированная среда  
✅ Легкое развертывание  
✅ Одинаковая работа на всех платформах  

## Установка Docker

### Windows
1. Скачайте [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Установите и запустите
3. Убедитесь, что Docker работает: `docker --version`

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

### macOS
1. Установите [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Запустите приложение

## Запуск с Docker

### Вариант 1: Docker Compose (рекомендуется)

```bash
# Сборка и запуск одной командой
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d
```

Откройте браузер: `http://localhost:8000`

### Вариант 2: Docker напрямую

```bash
# Сборка образа
docker build -t screenplay-analyzer .

# Запуск контейнера
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  --name screenplay-analyzer \
  screenplay-analyzer
```

## Управление контейнером

### Просмотр логов
```bash
docker-compose logs -f
# или
docker logs -f screenplay-analyzer
```

### Остановка
```bash
docker-compose down
# или
docker stop screenplay-analyzer
```

### Перезапуск
```bash
docker-compose restart
# или
docker restart screenplay-analyzer
```

### Удаление
```bash
docker-compose down -v
# или
docker rm -f screenplay-analyzer
```

## Обновление

```bash
# Пересборка образа после изменений
docker-compose up --build

# Или для Docker:
docker build -t screenplay-analyzer .
docker stop screenplay-analyzer
docker rm screenplay-analyzer
docker run -d -p 8000:8000 --name screenplay-analyzer screenplay-analyzer
```

## Настройка volumes

Volumes позволяют сохранять данные между перезапусками:

```yaml
# docker-compose.yml
volumes:
  - ./uploads:/app/uploads     # Загруженные файлы
  - ./outputs:/app/outputs     # Результаты обработки
  - ./models:/app/models       # Кэш моделей
```

## Переменные окружения

Добавьте в `docker-compose.yml`:

```yaml
environment:
  - MAX_FILE_SIZE_MB=50
  - MAX_PAGES=120
  - PORT=8000
```

## Изменение порта

Если порт 8000 занят:

```yaml
# docker-compose.yml
ports:
  - "8080:8000"  # Внешний:Внутренний
```

Или для Docker:
```bash
docker run -d -p 8080:8000 screenplay-analyzer
```

## Мониторинг ресурсов

```bash
# Просмотр использования ресурсов
docker stats screenplay-analyzer

# Информация о контейнере
docker inspect screenplay-analyzer
```

## Ограничение ресурсов

```yaml
# docker-compose.yml
services:
  screenplay-analyzer:
    # ... другие настройки
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          memory: 2G
```

## Отладка

### Войти в контейнер
```bash
docker exec -it screenplay-analyzer bash
```

### Просмотр логов ошибок
```bash
docker logs screenplay-analyzer --tail 50
```

### Проверка работы сервиса
```bash
curl http://localhost:8000/health
```

## Production развертывание

### Docker Swarm
```bash
docker swarm init
docker stack deploy -c docker-compose.yml screenplay
```

### Kubernetes
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: screenplay-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: screenplay-analyzer
  template:
    metadata:
      labels:
        app: screenplay-analyzer
    spec:
      containers:
      - name: screenplay-analyzer
        image: screenplay-analyzer:latest
        ports:
        - containerPort: 8000
```

## Резервное копирование

### Бэкап данных
```bash
# Создать архив outputs
docker run --rm \
  -v $(pwd)/outputs:/outputs \
  -v $(pwd):/backup \
  alpine tar czf /backup/outputs-backup.tar.gz -C / outputs

# Бэкап всего контейнера
docker commit screenplay-analyzer screenplay-analyzer-backup
docker save screenplay-analyzer-backup > screenplay-backup.tar
```

### Восстановление
```bash
# Восстановить образ
docker load < screenplay-backup.tar

# Восстановить данные
tar xzf outputs-backup.tar.gz
```

## Решение проблем

### Проблема: Контейнер не запускается
```bash
# Проверьте логи
docker logs screenplay-analyzer

# Проверьте, не занят ли порт
netstat -tulpn | grep 8000
```

### Проблема: Модели не загружаются
```bash
# Увеличьте память для Docker
# Docker Desktop → Settings → Resources → Memory: 8GB
```

### Проблема: Медленная работа
```bash
# Выделите больше CPU
# docker-compose.yml → cpus: '4.0'
```

## Полезные команды

```bash
# Список запущенных контейнеров
docker ps

# Все контейнеры (включая остановленные)
docker ps -a

# Список образов
docker images

# Удалить неиспользуемые образы
docker image prune

# Очистить всё
docker system prune -a
```

## Сетевые настройки

### Использование в локальной сети

```bash
# Запуск с доступом из локальной сети
docker run -d -p 0.0.0.0:8000:8000 screenplay-analyzer
```

### Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name screenplay.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## CI/CD

### GitHub Actions
```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t screenplay-analyzer .
      - name: Run tests
        run: docker run screenplay-analyzer pytest
```

## Безопасность

```bash
# Запуск от не-root пользователя
# Добавьте в Dockerfile:
RUN useradd -m appuser
USER appuser
```

## Заключение

Docker упрощает развертывание и масштабирование сервиса. 

Для production рекомендуется:
- Использовать orchestration (Kubernetes/Swarm)
- Настроить мониторинг (Prometheus/Grafana)
- Добавить health checks
- Настроить автоматическое резервное копирование

---

**Документация:** [README.md](README.md)  
**Быстрый старт:** [QUICKSTART.md](QUICKSTART.md)

