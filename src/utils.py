from typing import Dict, Optional

def parse_time(s: str) -> Dict[str, int]:
    parts = s.split(':')
    hours = 0
    minutes = 0
    seconds_with_ms = "0"
    
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_with_ms = parts[2]
    elif len(parts) == 2:
        minutes = int(parts[0])
        seconds_with_ms = parts[1]
    else:
        seconds_with_ms = parts[0]
    
    if '.' in seconds_with_ms:
        sec_parts = seconds_with_ms.split('.')
        seconds = int(sec_parts[0])
        milliseconds = int(sec_parts[1].ljust(3, '0')[:3])
    else:
        seconds = int(seconds_with_ms)
        milliseconds = 0
    
    total_minutes = hours * 60 + minutes
    
    return {
        'minute': total_minutes,
        'second': seconds,
        'millisecond': milliseconds
    }

def get_category(players: str) -> Optional[str]:
    p = [x.strip() for x in players.split(',') if x.strip()]
    count = len(p)
    if count == 1:
        return "Solo"
    elif count == 2:
        return "Duo"
    elif count == 3:
        return "Trio"
    elif count == 4:
        return "Quartet"
    elif count >= 5:
        return "Squad"
    return None

def center_window(window):
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
    y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
    window.geometry(f"+{x}+{y}")

def validate_run(data: Dict, levels: Dict, vars: Dict) -> Optional[str]:
    players = data.get('players', '')
    map_name = data.get('map', '')
    time = data.get('time', '')
    var = data.get('variable', '')
    video = data.get('video', '')
    
    cat = get_category(players)
    if not cat:
        count = len([p for p in players.split(',') if p.strip()])
        return f"Invalid player count ({count})"
    
    if map_name not in levels:
        return f"Invalid map ({map_name})"
    
    if not any(c.isdigit() for c in time):
        return f"Invalid time format ({time})"
    
    if var not in vars['options']:
        return f"Invalid gear/gearless value ({var})"
    
    if not (video.startswith('http://') or video.startswith('https://')):
        return f"Invalid video URL ({video})"
    
    return None
