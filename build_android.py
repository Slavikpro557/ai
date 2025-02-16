import os
import subprocess
import sys
import shutil

def check_requirements():
    """Проверка наличия необходимых компонентов"""
    print("Проверка необходимых компонентов...")
    
    # Проверка Java
    try:
        subprocess.run(['java', '-version'], capture_output=True)
        print("✓ Java установлена")
    except FileNotFoundError:
        print("❌ Требуется установить Java JDK")
        return False
    
    # Проверка Buildozer
    try:
        subprocess.run(['buildozer', '--version'], capture_output=True)
        print("✓ Buildozer установлен")
    except FileNotFoundError:
        print("Установка Buildozer...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'buildozer'])
    
    return True

def prepare_templates():
    """Подготовка шаблонов карт и кнопок"""
    print("Подготовка ресурсов...")
    
    # Создаем директории для ресурсов
    os.makedirs('templates/cards', exist_ok=True)
    os.makedirs('templates/buttons', exist_ok=True)
    
    # Здесь можно добавить копирование шаблонов из другой директории
    print("✓ Директории для ресурсов созданы")

def build_apk():
    """Сборка APK"""
    print("Начало сборки APK...")
    
    # Очистка предыдущей сборки
    if os.path.exists('.buildozer'):
        shutil.rmtree('.buildozer')
    
    # Запуск сборки
    result = subprocess.run(['buildozer', 'android', 'debug'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ APK успешно собран")
        apk_path = 'bin/durakAI-0.1-debug.apk'
        if os.path.exists(apk_path):
            print(f"APK находится в: {os.path.abspath(apk_path)}")
    else:
        print("❌ Ошибка при сборке APK")
        print("Лог ошибок:")
        print(result.stderr)

def main():
    print("=== Сборка Durak AI APK ===")
    
    if not check_requirements():
        print("❌ Не все требования удовлетворены")
        return
    
    prepare_templates()
    
    print("\nНачало процесса сборки...")
    build_apk()

if __name__ == '__main__':
    main() 