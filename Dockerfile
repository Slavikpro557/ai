FROM kivy/buildozer

# Установка дополнительных зависимостей
RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3-virtualenv \
    libssl-dev \
    libffi-dev \
    libltdl-dev \
    libbz2-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    liblzma-dev \
    uuid-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY . /app/

# Сборка APK
CMD buildozer android debug 