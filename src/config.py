# config.py
import streamlit as st
from datetime import datetime

# --- Load Configuration ---
try:
    API_URL = st.secrets["API_URL"]
    API_KEY = st.secrets["API_KEY"]
    MODEL = "gemma3:4b"
except KeyError:
    st.error("❌ Secrets not found! Please ensure API_KEY and API_URL are set in .streamlit/secrets.toml")
    st.stop()

# --- Constants Setup ---
TODAY = datetime.now().strftime("%Y-%m-%d")

# Visa and entry rules database
ENTRY_DB = {
    "日本": "🇯🇵 **簽證**：免簽證（觀光 90 天）。\n\n**規定**：需填寫 Visit Japan Web。",
    "韓國": "🇰🇷 **簽證**：免簽證（觀光 90 天）。\n\n**規定**：建議申請 K-ETA。",
    "泰國": "🇹🇭 **簽證**：對台免簽證優惠中。\n\n**規定**：備妥回程機票供抽查。",
    "美國": "🇺🇸 **簽證**：需申請 ESTA (21 USD)。\n\n**規定**：建議出發前 72 小時完成申請。",
    "新加坡": "🇸🇬 **簽證**：免簽證（30 天）。\n\n**規定**：填寫 SG Arrival Card。"
}

# Popular cities mapping (Display Name -> Search Query)
POPULAR_CITIES = {
    "東京 🍣": "東京", "大阪 🐙": "大阪", "首爾 🇰🇷": "首爾", "曼谷 🥭": "曼谷", 
    "倫敦 🎡": "倫敦", "巴黎 🗼": "巴黎", "紐約 🗽": "紐約", "新加坡 🦁": "新加坡", 
    "雪梨 🐨": "雪梨", "冰島 ❄️": "冰島", "溫哥華 🍁": "溫哥華", "羅馬 🍕": "羅馬", 
    "布拉格 🏰": "布拉格", "清邁 🐘": "清邁", "福岡 🍜": "福岡", "墨爾本 ☕": "墨爾本", 
    "阿姆斯特丹 🌷": "阿姆斯特丹", "維也納 🎵": "維也納", "巴塞隆納 ⚽": "巴塞隆納", "瑞士 🧀": "瑞士"
}