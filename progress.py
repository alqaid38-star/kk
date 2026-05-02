import math

def get_progress_bar(current_seconds, total_seconds):
    if total_seconds == 0:
        return "00:00 ──○────── 00:00"
    
    percentage = (current_seconds / total_seconds) * 100
    percentage = min(max(percentage, 0), 100)
    
    # Create the visual bar
    bar_length = 10
    filled_length = int(round(bar_length * percentage / 100))
    
    bar = "━" * filled_length + "○" + "─" * (bar_length - filled_length)
    
    # Format times
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    return f"{format_time(current_seconds)} {bar} {format_time(total_seconds)}"
