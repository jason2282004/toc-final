# utils.py
import re

def extract_video_id(url):
    """Safely extract YouTube video ID from a URL."""
    if not url: return None
    pattern = r'(?:v=|\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def render_sticky_note(user, content, color="#fff176"):
    """
    Render the HTML string for a sticky note UI component.
    """
    return f"""
    <div style="
        background-color: {color};
        padding: 15px;
        width: 100%;
        height: 100%;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
        transform: rotate({hash(user) % 6 - 3}deg);
        color: #333;
        border-radius: 2px;">
        <div style="font-weight: bold; margin-bottom: 5px; border-bottom: 1px dashed #555; padding-bottom: 3px;">
            📌 {user}
        </div>
        <div style="font-size: 0.95rem; line-height: 1.4;">
            {content}
        </div>
    </div>
    """