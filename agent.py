#!/usr/bin/env python3
"""
🎵 Музыкальный помощник для OpenCode
Поиск информации о музыке
"""

import sys
import subprocess

# ========== ПРОВЕРКА ЗАВИСИМОСТЕЙ ==========

def check_dependencies():
    """Проверяет зависимости"""
    print("🔧 Проверка...")
    
    try:
        import yt_dlp
        print("   ✅ Библиотеки готовы")
    except ImportError:
        print("   ⏳ Установка...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '-q'])
        print("   ✅ Готово")
    
    print()

check_dependencies()

# ========== ПОИСК ==========

def find_track(query):
    """Ищет информацию о треке"""
    
    sources = [
        ('vksearch', 'VK'),
        ('scsearch', 'SoundCloud'),
        ('bandcamp', 'Bandcamp'),
    ]
    
    for source_code, source_name in sources:
        try:
            import yt_dlp
            
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
                        track = entries[0]
                        return {
                            'success': True,
                            'title': track.get('title', query),
                            'url': track.get('url', ''),
                            'source': source_name,
                            'duration': track.get('duration', 0)
                        }
                        
        except:
            continue
    
    return {'success': False, 'error': 'Не найдено'}

# ========== КОМАНДЫ ==========

def process_command(command, args):
    """Обрабатывает команды"""
    
    if command in ['help', 'помощь', '?']:
        return """
🎵 Музыкальный помощник — команды:

/music [название]  — найти информацию
/search [название] — поиск
/help              — справка

Пример: /music белый танец
"""
    
    elif command in ['music', 'm', 'search', 's']:
        if not args:
            return "❌ Введите название: /music [название]"
        
        print(f"\n🔍 Поиск: {args}...")
        found = find_track(args)
        
        if not found['success']:
            return f"❌ Не найдено: {args}\nПопробуй уточнить."
        
        duration = found.get('duration', 0)
        duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "?"
        
        return f"""✅ Найдено в {found['source']}:
🎵 {found['title']}
⏱ {duration_str}
🔗 {found['url']}

💡 Откройте ссылку для прослушивания"""
    
    else:
        return """🎵 Музыкальный помощник
Введите: /music [название]"""

# ========== ЗАПУСК ==========

def main():
    print("\n" + "="*60)
    print("🎵 МУЗЫКАЛЬНЫЙ ПОМОЩНИК")
    print("="*60)
    print("Поиск информации о музыке")
    print("Команды: /music, /search, /help\n")
    
    while True:
        user_input = input("➡️  ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit', 'выход', 'стоп']:
            print("\n👋 До свидания!")
            break
        
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
