#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from pathlib import Path

# АВТО-УСТАНОВКА ЗАВИСИМОСТЕЙ 

def check_and_install_dependencies():
    """Проверяет и устанавливает все зависимости"""
    print("🔧 Проверка зависимостей...")
    
    if sys.version_info < (3, 9):
        print("❌ Требуется Python 3.9+")
        sys.exit(1)
    
    # Проверяем yt-dlp
    try:
        import yt_dlp
        print("   ✅ yt-dlp")
    except ImportError:
        print("   ⏳ Установка yt-dlp...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '-q'])
        print("   ✅ yt-dlp установлен")
    
    # Проверяем и устанавливаем ffmpeg
    check_and_install_ffmpeg()
    
    print("✅ Все зависимости готовы!\n")

def check_and_install_ffmpeg():
    """Автоматически устанавливает ffmpeg"""
    print("   🔍 Проверка ffmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ ffmpeg найден")
            return
    except:
        pass
    
    print("   ⏳ ffmpeg не найден. Устанавливаю...")
    
    if os.name == 'nt':  # Windows
        install_ffmpeg_windows()
    elif os.name == 'posix':
        import platform
        if platform.system() == 'Darwin':
            install_ffmpeg_macos()
        else:
            install_ffmpeg_linux()
    else:
        print("   ⚠️ Установите вручную: https://ffmpeg.org/download.html")
        return
    
    # Проверяем установку
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ ffmpeg успешно установлен!")
        else:
            print("   ❌ Ошибка установки ffmpeg")
    except:
        print("   ❌ Не удалось проверить ffmpeg")

def install_ffmpeg_windows():
    """Устанавливает ffmpeg на Windows"""
    print("      🪟 Установка для Windows...")
    
    # Пробуем winget
    try:
        subprocess.run(['winget', 'install', 'ffmpeg'], capture_output=True, timeout=60)
        print("      ✅ ffmpeg установлен (winget)")
        return
    except:
        pass
    
    # Пробуем chocolatey
    try:
        subprocess.run(['choco', 'install', 'ffmpeg', '-y'], capture_output=True, timeout=120)
        print("      ✅ ffmpeg установлен (choco)")
        return
    except:
        pass
    
    # Ручная загрузка
    print("      → Ручная загрузка...")
    download_ffmpeg_manual()

def install_ffmpeg_linux():
    """Устанавливает ffmpeg на Linux"""
    print("      🐧 Установка для Linux...")
    try:
        subprocess.run(['sudo', 'apt', 'update'], capture_output=True, timeout=30)
        subprocess.run(['sudo', 'apt', 'install', 'ffmpeg', '-y'], capture_output=True, timeout=120)
        print("      ✅ ffmpeg установлен (apt)")
    except:
        try:
            subprocess.run(['sudo', 'dnf', 'install', 'ffmpeg', '-y'], capture_output=True, timeout=120)
            print("      ✅ ffmpeg установлен (dnf)")
        except:
            print("      ⚠️ Выполните: sudo apt install ffmpeg")

def install_ffmpeg_macos():
    """Устанавливает ffmpeg на macOS"""
    print("      🍎 Установка для macOS...")
    try:
        subprocess.run(['brew', 'install', 'ffmpeg'], capture_output=True, timeout=120)
        print("      ✅ ffmpeg установлен (brew)")
    except:
        print("      ⚠️ Выполните: brew install ffmpeg")

def download_ffmpeg_manual():
    """Ручная загрузка ffmpeg для Windows"""
    import urllib.request
    import zipfile
    import shutil
    
    print("      📥 Загрузка ffmpeg...")
    
    try:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        temp_dir = Path.home() / "Downloads" / "ffmpeg_temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        zip_path = temp_dir / "ffmpeg.zip"
        
        print("      ⏳ Скачивание (может занять несколько минут)...")
        urllib.request.urlretrieve(url, zip_path)
        
        print("      📦 Распаковка...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Находим папку bin
        for folder in temp_dir.iterdir():
            if folder.is_dir() and folder.name.startswith('ffmpeg'):
                bin_path = folder / "bin"
                if bin_path.exists():
                    current_path = os.environ.get('PATH', '')
                    os.environ['PATH'] = str(bin_path) + os.pathsep + current_path
                    print(f"      ✅ ffmpeg добавлен в PATH")
                    break
        
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"      ❌ Ошибка: {e}")

#  ИМПОРТ ПОСЛЕ УСТАНОВКИ 

check_and_install_dependencies()

import yt_dlp

#  ФУНКЦИИ 

def find_music(query):
    """Ищет музыку в доступных источниках (без YouTube)"""
    
    sources = [
        ('vksearch', 'VK (ВКонтакте)'),
        ('scsearch', 'SoundCloud'),
        ('rutube', 'RuTube'),
        ('bandcamp', 'Bandcamp'),
    ]
    
    for source_code, source_name in sources:
        try:
            print(f"   🔍 Ищу в {source_name}...")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'default_search': source_code,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{source_code}:{query}", download=False)
                
                if info and 'entries' in info:
                    entries = [e for e in info['entries'] if e is not None]
                    if entries:
                        track = entries[0]
                        return {
                            'success': True,
                            'title': track.get('title', query),
                            'url': track.get('url', ''),
                            'source': source_name,
                            'extractor': source_code,
                            'duration': track.get('duration', 0)
                        }
                elif info and 'url' in info:
                    return {
                        'success': True,
                        'title': info.get('title', query),
                        'url': info.get('webpage_url', info.get('url', '')),
                        'source': source_name,
                        'extractor': source_code,
                        'duration': info.get('duration', 0)
                    }
                    
        except Exception as e:
            continue
    
    return {'success': False, 'error': 'Не найдено ни в одном источнике'}

def download_mp4(url, title):
    """Скачивает видео в MP4"""
    os.makedirs('downloads', exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            for f in os.listdir('downloads'):
                if f.endswith('.mp4') and title.lower() in f.lower():
                    return {
                        'success': True,
                        'file': f,
                        'path': os.path.join('downloads', f),
                        'size': os.path.getsize(os.path.join('downloads', f)) // (1024 * 1024)
                    }
            
            mp4_files = [f for f in os.listdir('downloads') if f.endswith('.mp4')]
            if mp4_files:
                return {
                    'success': True,
                    'file': mp4_files[0],
                    'path': os.path.join('downloads', mp4_files[0]),
                    'size': os.path.getsize(os.path.join('downloads', mp4_files[0])) // (1024 * 1024)
                }
                
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'Не скачалось'}

def convert_mp4_to_mp3(mp4_path):
    """Конвертирует MP4 в MP3 через ffmpeg"""
    try:
        mp3_path = mp4_path.rsplit('.', 1)[0] + '.mp3'
        
        cmd = [
            'ffmpeg',
            '-i', mp4_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-y',
            mp3_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(mp3_path):
            # Удаляем временный MP4
            os.remove(mp4_path)
            
            return {
                'success': True,
                'file': os.path.basename(mp3_path),
                'path': mp3_path,
                'size': os.path.getsize(mp3_path) // 1024
            }
        
        return {'success': False, 'error': 'Конвертация не удалась'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def download_mp3_direct(url, title):
    """Скачивает сразу в MP3 (альтернативный метод)"""
    os.makedirs('downloads', exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            for f in os.listdir('downloads'):
                if f.endswith('.mp3') and title.lower() in f.lower():
                    return {
                        'success': True,
                        'file': f,
                        'path': os.path.join('downloads', f),
                        'size': os.path.getsize(os.path.join('downloads', f)) // 1024
                    }
            
            mp3_files = [f for f in os.listdir('downloads') if f.endswith('.mp3')]
            if mp3_files:
                return {
                    'success': True,
                    'file': mp3_files[0],
                    'path': os.path.join('downloads', mp3_files[0]),
                    'size': os.path.getsize(os.path.join('downloads', mp3_files[0])) // 1024
                }
                
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'Не скачалось'}

#  ОБРАБОТКА КОМАНД 

def process_command(command, args):
    """Обрабатывает команды пользователя"""
    
    if command in ['help', 'помощь', '?']:
        return """
🎵 Музыкальный ИИ-агент — команды:

/music [название]  — Найти и скачать в MP3
/video [название]  — Скачать видео (MP4)
/search [название] — Только поиск
/help              — Эта справка

Примеры:
  /music белый танец лсп
  /video экспонат ленинград
  /search грустная музыка
"""
    
    elif command in ['music', 'm', 'скачать']:
        if not args:
            return "❌ Введите название: /music [название песни]"
        
        print(f"\n🔍 Ищу: {args}...")
        found = find_music(args)
        
        if not found['success']:
            return f"❌ Не найдено: {args}\nПопробуй уточнить запрос."
        
        duration = found.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
        
        result = f"""✅ Найдено в {found['source']}:
🎵 {found['title']}
⏱ {duration_str}
📥 Скачиваю MP4..."""
        
        print(result)
        
        # Скачиваем MP4
        dl = download_mp4(found['url'], found['title'])
        
        if not dl['success']:
            # Пробуем прямое скачивание в MP3
            print("   ⚠️ MP4 не скачался, пробую MP3...")
            dl = download_mp3_direct(found['url'], found['title'])
            
            if dl['success']:
                return f"""✅ Готово!
📁 {dl['file']} ({dl['size']} KB)
🎧 Приятного прослушивания!"""
            else:
                return f"❌ Ошибка скачивания: {dl.get('error', 'Неизвестно')}"
        
        print(f"   ✅ MP4 скачан: {dl['file']} ({dl['size']} MB)")
        print("   🔄 Конвертирую в MP3...")
        
        # Конвертируем в MP3
        conv = convert_mp4_to_mp3(dl['path'])
        
        if conv['success']:
            return f"""✅ Готово!
📁 {conv['file']} ({conv['size']} KB)
🎧 Приятного прослушивания!"""
        else:
            return f"⚠️ Конвертация не удалась: {conv.get('error', 'Неизвестно')}\nMP4 сохранён: {dl['file']}"
    
    elif command in ['video', 'v', 'видео']:
        if not args:
            return "❌ Введите название: /video [название]"
        
        print(f"\n📹 Ищу видео: {args}...")
        found = find_music(args)
        
        if not found['success']:
            return f"❌ Не найдено: {args}"
        
        print("📥 Скачиваю MP4...")
        dl = download_mp4(found['url'], found['title'])
        
        if dl['success']:
            return f"""✅ Готово!
📁 {dl['file']} ({dl['size']} MB)
📹 Видео сохранено в downloads/"""
        else:
            return f"❌ Ошибка: {dl.get('error', 'Неизвестно')}"
    
    elif command in ['search', 's', 'поиск']:
        if not args:
            return "❌ Введите название: /search [название]"
        
        print(f"\n🔍 Ищу: {args}...")
        found = find_music(args)
        
        if not found['success']:
            return f"❌ Не найдено: {args}"
        
        duration = found.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
        
        return f"""✅ Найдено в {found['source']}:
🎵 {found['title']}
⏱ {duration_str}
🔗 {found['url']}

💡 Для скачивания: /music {args}"""
    
    else:
        return """🎵 Музыкальный ИИ-агент
Введите команду:
  /music [название] — скачать MP3
  /video [название] — скачать MP4
  /help — помощь"""

# ЗАПУСК 

def main():
    print("\n" + "="*60)
    print("🎵 МУЗЫКАЛЬНЫЙ ИИ-АГЕНТ")
    print("="*60)
    print("Источники: VK, SoundCloud, RuTube (БЕЗ VPN)")
    print("Процесс: MP4 → MP3 (авто-конвертация)")
    print("Команды: /music, /video, /search, /help\n")
    
    while True:
        user_input = input("➡️  ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit', 'выход', 'стоп']:
            print("\n👋 До свидания!")
            break
        
        # Парсим команду
        if user_input.startswith('/'):
            parts = user_input[1:].split(' ', 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''
        else:
            command = 'music'
            args = user_input
        
        response = process_command(command, args)
        print(f"\n{response}\n")

if __name__ == "__main__":
    main()
