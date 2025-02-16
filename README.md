# DurakAI - Умный ассистент для игры в Дурака

## Как скачать проект

### Шаг 1: Настройка Git
```bash
git config --global user.name "Slavikpro557"
git config --global user.email "slavikpro557@gmail.com"
```

### Шаг 2: Клонирование репозитория
```bash
# Для Windows
git clone https://github.com/Slavikpro557/ai.git

# Для Linux
mkdir ai_project
cd ai_project
git clone https://github.com/Slavikpro557/ai.git
```

Если Git запрашивает пароль, используйте токен доступа, который вы можете получить у владельца репозитория.

## Особенности

- 🧠 Самообучающийся ИИ
- 📱 Работает с любым приложением для игры в дурака
- 🎮 Два режима работы: советы и автоматическая игра
- 📊 Анализ игровой ситуации в реальном времени
- 📈 Статистика и улучшение стратегии
- 🔄 Адаптация под конкретное приложение

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Использование

1. Запустите приложение:
```bash
python main.py
```

2. Выполните калибровку, указав область игрового поля
3. Включите нужный режим (советы/автоигра)
4. Начните анализ

## Требования

- Python 3.8+
- OpenCV
- NumPy
- Доступ к экрану для анализа

## Конфигурация

- `templates/` - шаблоны карт и кнопок
- `ai_data/` - данные обучения ИИ
- `config.json` - настройки приложения

## Лицензия

MIT License 
