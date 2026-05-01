#!/usr/bin/env python3
"""
🎵 Музыкальный ИИ-помощник с диалогом + СКАЧИВАНИЕ
Спрашивает про настроение, жанр, предпочтения + скачивает в MP3
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# ========== АВТО-УСТАНОВКА ЗАВИСИМОСТЕЙ ==========

def check_and_install_dependencies():
    """Проверяет и устанавливает зависимости"""
    print("🔧 Проверка зависимостей...")
    
    # Проверяем yt-dlp
    try:
        import yt_dlp
        print("   ✅ yt-dlp")
    except ImportError:
        print("   ⏳ Установка yt-dlp...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '-q'])
        print("   ✅ yt-dlp установлен")
    
    # Проверяем ffmpeg
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
    except:
        print("   ❌ Не удалось проверить ffmpeg")

def install_ffmpeg_windows():
    """Устанавливает ffmpeg на Windows"""
    print("      🪟 Установка для Windows...")
    try:
        subprocess.run(['winget', 'install', 'ffmpeg'], capture_output=True, timeout=60)
        print("      ✅ ffmpeg установлен (winget)")
        return
    except:
        pass
    try:
        subprocess.run(['choco', 'install', 'ffmpeg', '-y'], capture_output=True, timeout=120)
        print("      ✅ ffmpeg установлен (choco)")
        return
    except:
        pass
    print("      ⚠️ Установите вручную или скачайте с: https://ffmpeg.org/download.html")

def install_ffmpeg_linux():
    """Устанавливает ffmpeg на Linux"""
    print("      🐧 Установка для Linux...")
    try:
        subprocess.run(['sudo', 'apt', 'update'], capture_output=True, timeout=30)
        subprocess.run(['sudo', 'apt', 'install', 'ffmpeg', '-y'], capture_output=True, timeout=120)
        print("      ✅ ffmpeg установлен (apt)")
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

# Запускаем установку
check_and_install_dependencies()

import yt_dlp

# ========== СОСТОЯНИЯ ДИАЛОГА ==========

class DialogState:
    def __init__(self):
        self.stage = 'greeting'
        self.mood = ''
        self.genre = ''
        self.artist = ''
        self.found_tracks = []
        self.last_search_result = None

# ========== ПОИСК ТРЕКОВ ==========

def find_track(query):
    """Ищет музыку в доступных источниках (без YouTube)"""
    
    sources = [
        ('vksearch', 'VK'),
        ('scsearch', 'SoundCloud'),
        ('bandcamp', 'Bandcamp'),
    ]
    
    for source_code, source_name in sources:
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': source_code,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{source_code}:{query}", download=False)
                
                if info and 'entries' in info:
                    entries = [e for e in info['entries'] if e is not None]
                    if entries:
                        tracks = []
                        for track in entries[:4]:
                            if track:
                                tracks.append({
                                    'title': track.get('title', ''),
                                    'url': track.get('url', ''),
                                    'id': track.get('id', ''),
                                    'duration': track.get('duration', 0),
                                    'artist': track.get('channel', ''),
                                    'source': source_name
                                })
                        return {'success': True, 'tracks': tracks, 'source': source_name}
                        
        except Exception as e:
            continue
    
    return {'success': False, 'error': 'Не найдено'}

# ========== СКАЧИВАНИЕ В MP3 ==========

def download_mp3(url, title, video_id=''):
    """Скачивает трек и конвертирует в MP3"""
    
    # Создаём папку для загрузок
    download_dir = Path('downloads')
    download_dir.mkdir(exist_ok=True)
    
    # Безопасное имя файла
    safe_title = "".join(c if c.isalnum() or c in ' -_.' else '_' for c in title)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': str(download_dir / f'{safe_title}.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    
    try:
        print(f"   📥 Скачиваю: {title}...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Ищем скачанный файл
        for f in download_dir.iterdir():
            if f.suffix == '.mp3' and safe_title.lower() in f.stem.lower():
                file_size = f.stat().st_size // 1024  # KB
                print(f"   ✅ Скачано: {f.name} ({file_size} KB)")
                
                return {
                    'success': True,
                    'file_path': str(f),
                    'file_name': f.name,
                    'file_size': file_size
                }
        
        # Если не нашли по имени — берём первый MP3
        mp3_files = list(download_dir.glob('*.mp3'))
        if mp3_files:
            f = mp3_files[0]
            file_size = f.stat().st_size // 1024
            return {
                'success': True,
                'file_path': str(f),
                'file_name': f.name,
                'file_size': file_size
            }
        
        return {'success': False, 'error': 'Файл не найден после скачивания'}
        
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Превышено время ожидания'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# ========== ОПРЕДЕЛЕНИЕ НАСТРОЕНИЯ И ЖАНРА ==========

def get_mood_keywords(user_input):
    """Определяет настроение по ключевым словам"""
    moods = {
        'грустное': ['груст', 'печаль', 'меланхол', 'sad', 'депресс'],
        'весёлое': ['весел', 'радост', 'happy', 'позитив', 'бодр'],
        'спокойное': ['спокой', 'расслаб', 'chill', 'тих', 'умиротвор'],
        'энергичное': ['энергич', 'бодр', 'active', 'спорт', 'трениров'],
        'романтичное': ['романтик', 'любов', 'love', 'неж', 'свидан'],
    }
    
    user_input = user_input.lower()
    for mood, keywords in moods.items():
        for keyword in keywords:
            if keyword in user_input:
                return mood
    return ''

def get_genre_keywords(user_input):
    """Определяет жанр по ключевым словам"""
    genres = {
        'поп': ['поп', 'pop', 'танцеваль', 'dance'],
        'рок': ['рок', 'rock', 'метал', 'metal', 'гитар'],
        'хип-хоп': ['хип', 'хоп', 'hip', 'rap', 'рэп'],
        'лоу-фай': ['лоу', 'фай', 'lofi', 'lo-fi', 'study'],
        'электроника': ['электрон', 'electro', 'edm', 'techno', 'house'],
    }
    
    user_input = user_input.lower()
    for genre, keywords in genres.items():
        for keyword in keywords:
            if keyword in user_input:
                return genre
    return ''

# ========== ОБРАБОТКА ДИАЛОГА ==========

def process_dialog(user_input, state):
    """Обрабатывает диалог с пользователем"""
    
    user_input = user_input.strip().lower()
    
    # Команды выхода
    if user_input in ['стоп', 'stop', 'выход', 'exit', 'пока', 'quit']:
        return "👋 До свидания! Возвращайся за музыкой! 🎵", False, state
    
    # Команда назад
    if user_input in ['назад', 'back', 'заново', 'начать сначала']:
        state = DialogState()
        return "🎵 Начинаем заново! Какую музыку хочешь?", True, state
    
    # Команда скачать
    if user_input in ['скачать', 'download', 'сохранить']:
        if state.last_search_result and state.stage == 'suggesting':
            # Скачиваем последний найденный трек
            track = state.found_tracks[0] if state.found_tracks else None
            if track:
                print(f"\n📥 Скачиваю: {track['title']}...")
                dl = download_mp3(track['url'], track['title'], track.get('id', ''))
                
                if dl['success']:
                    state.stage = 'downloaded'
                    return f"""✅ Скачано!
🎵 {track['title']}
📁 {dl['file_name']} ({dl['file_size']} KB)
💾 Папка: downloads/
🎧 Приятного прослушивания!

Хочешь ещё музыку? Напиши 'заново' 🎵""", True, state
                else:
                    return f"❌ Ошибка скачивания: {dl['error']}\nПопробуем другой трек?", True, state
        return "🤔 Сначала найди трек, потом я скачаю! Введи название песни 🎵", True, state
    
    # Этап 1: Приветствие и сбор предпочтений
    if state.stage == 'greeting':
        mood = get_mood_keywords(user_input)
        genre = get_genre_keywords(user_input)
        
        if mood or genre or ' - ' in user_input or len(user_input) > 20:
            state.mood = mood or state.mood
            state.genre = genre or state.genre
            state.artist = user_input if ' - ' in user_input else state.artist
            state.stage = 'searching'
        else:
            return """🎵 Понял! Чтобы подобрать идеальную музыку, расскажи:

• Какое настроение? (грустное, весёлое, спокойное, энергичное)
• Какой жанр? (поп, рок, хип-хоп, лоу-фай, электроника)
• Есть любимые исполнители?
• Для чего музыка? (работа, спорт, отдых, дорога)

Можешь ответить на любой вопрос или просто опиши, что хочешь 🎧""", True, state
    
    # Этап 2: Поиск треков
    if state.stage == 'searching':
        search_parts = []
        if state.artist:
            search_parts.append(state.artist)
        if state.genre:
            search_parts.append(state.genre)
        if state.mood:
            search_parts.append(state.mood + " музыка")
        
        search_query = ' '.join(search_parts) if search_parts else user_input
        
        print(f"\n🔍 Ищу: {search_query}...")
        result = find_track(search_query)
        
        if not result['success']:
            return f"""❌ Не удалось найти треки.

Попробуем:
• Указать конкретного исполнителя?
• Изменить жанр или настроение?
• Или напиши название песни 🎵""", True, state
        
        state.found_tracks = result['tracks']
        state.last_search_result = result
        state.stage = 'suggesting'
        
        # Формируем список треков
        tracks_text = ""
        for i, track in enumerate(state.found_tracks, 1):
            duration = track.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
            tracks_text += f"{i}. {track.get('artist', '')} — {track.get('title', '')} ⏱ {duration_str}\n"
        
        return f"""🎧 На основе твоих предпочтений я подобрал:

{tracks_text}
💡 Введи номер (1-4) чтобы выбрать, или напиши 'скачать' для первого трека 🎵""", True, state
    
    # Этап 3: Пользователь выбирает трек
    if state.stage == 'suggesting':
        # Выбор по номеру
        if user_input.isdigit() and 1 <= int(user_input) <= len(state.found_tracks):
            selected = state.found_tracks[int(user_input) - 1]
        else:
            # Выбор по названию
            selected = None
            for track in state.found_tracks:
                if track.get('title', '').lower() in user_input or track.get('artist', '').lower() in user_input:
                    selected = track
                    break
        
        if selected:
            # Показываем информацию + опцию скачать
            duration = selected.get('duration', 0)
            duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
            
            return f"""✅ Найдено в {selected['source']}:
🎵 {selected.get('title', '')}
👤 {selected.get('artist', '')}
⏱ {duration_str}
🔗 {selected.get('url', '')}

📥 Напиши 'скачать' чтобы сохранить в MP3
💡 Или выбери другой трек номером (1-4)""", True, state
        else:
            return "🤔 Не понял выбор. Введи номер трека (1-4) или 'скачать' 🎵", True, state
    
    # Этап 4: После скачивания
    if state.stage == 'downloaded':
        if any(w in user_input for w in ['ещё', 'другое', 'подбери', 'заново']):
            state = DialogState()
            return "🎵 Отлично! Какую музыку ещё хочешь?", True, state
        return "🎧 Рад, что помог! Напиши 'заново' для нового подбора 🎵", True, state
    
    # По умолчанию
    return """🎵 Я здесь, чтобы помочь с музыкой!

Просто опиши, что хочешь услышать:
• "грустная музыка для вечера"
• "рок для тренировки"
• "лоу-фай для работы"
• или название песни 🎧""", True, state

# ========== ЗАПУСК ==========

def main():
    state = DialogState()
    
    print("\n" + "="*60)
    print("🎵 МУЗЫКАЛЬНЫЙ ИИ-ПОМОЩНИК + СКАЧИВАНИЕ")
    print("="*60)
    print("• Подбор по настроению и жанру")
    print("• Скачивание в MP3 (192 kbps)")
    print("• Источники: VK, SoundCloud, Bandcamp (без VPN)")
    print("Команды: 'скачать', 'назад', 'стоп'\n")
    
    # Приветствие
    print("🎵 Привет! Какую музыку хочешь?")
    print("• Грустную или весёлую?")
    print("• Рок, поп, хип-хоп, лоу-фай?")
    print("• Есть любимые исполнители?\n")
    
    running = True
    while running:
        user_input = input("➡️  ").strip()
        
        if not user_input:
            continue
        
        response, running, state = process_dialog(user_input, state)
        print(f"\n{response}\n")

if __name__ == "__main__":
    main()
