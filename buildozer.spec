[app]
title = Durak AI
package.name = durak_ai
package.domain = org.durak
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1

requirements = python3,kivy,numpy,opencv-python,pillow,psutil,pyautogui,mss

# Ориентация и настройки экрана
orientation = portrait
fullscreen = 0
android.presplash_color = #000000
android.window = 800x600

# Разрешения Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,SYSTEM_ALERT_WINDOW

# Настройки сборки
android.arch = arm64-v8a
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.allow_backup = True

# Включаем поддержку OpenCV
android.enable_opencv = True

# Добавляем нативные зависимости
android.enable_natives = True

# Настройки для работы с окнами
android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 1

# Дополнительные настройки для сборки
android.release_artifact = apk
p4a.branch = master
p4a.bootstrap = sdl2 