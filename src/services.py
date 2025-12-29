# services.py
import streamlit as st
import requests
import re
import random
import time
from duckduckgo_search import DDGS
from config import API_URL, API_KEY, MODEL

def call_llm(prompt, sys_msg="你是一個具備經驗的旅遊分析師。"):
    """Call the LLM API for analysis."""
    headers = {"Authorization": f"Bearer {API_KEY.strip()}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}], "stream": False}
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        data = resp.json()
        return data['message']['content'] if 'message' in data else data['choices'][0]['message']['content']
    except: return None

def translate_to_english(city_name):
    """Translate location name to official English name using LLM, removing punctuation."""
    if re.match(r'^[A-Za-z\s,-]+$', city_name):
        return city_name.strip()
    
    prompt = f"請將這個城市地名翻譯成其官方英文名稱：'{city_name}'。請只輸出英文名稱，禁止輸出任何標點符號、括號或多餘文字。"
    english_name = call_llm(prompt, sys_msg="你是一個精準且不廢話的地理名稱翻譯器。")
    clean_name = re.sub(r'[^a-zA-Z\s]', '', english_name) if english_name else city_name
    return clean_name.strip()

@st.cache_data(ttl=3600)
def get_wikipedia_summary(location):
    """Fetch Wikipedia summary and main image."""
    headers = {"User-Agent": "Mozilla/5.0"}
    for lang in ["zh", "en"]:
        try:
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{location}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                extract = data.get("extract", "")
                img_url = data.get("originalimage", {}).get("source", "")
                return extract, img_url
        except: continue
    return "無法取得 Wikipedia 介紹", ""

@st.cache_data(ttl=1800)
def search_entry_rules(country):
    """Search for entry requirements via DuckDuckGo."""
    queries = [
        f"site:gov {country} entry requirements Taiwan passport",
        f"site:mofa {country} visa Taiwan",
        f"Taiwan passport {country} entry requirements official"
    ]
    links = []
    try:
        with DDGS() as ddgs:
            for q in queries:
                results = list(ddgs.text(q, max_results=5))
                for r in results:
                    href = r.get("href", "")
                    if href and href not in links:
                        links.append(href)
    except:
        pass
    return links[:5] if links else None

@st.cache_data(ttl=3600)
def get_exchange_rate(target_currency="JPY"):
    """[Non-LLM] Get real-time exchange rate (Base: TWD)."""
    try:
        url = "https://open.er-api.com/v6/latest/TWD"
        data = requests.get(url).json()
        return data['rates'].get(target_currency, "N/A")
    except: return "N/A"

@st.cache_data(ttl=3600)
def get_location_data(location, start_date, end_date):
    """Fetch Geolocation and Weather data."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&format=json"
        res = requests.get(geo_url).json()
        if res.get('results'):
            r = res['results'][0]
            lat, lon = r['latitude'], r['longitude']
            country = r.get('country', location)

            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&start_date={start_str}&end_date={end_str}&timezone=auto"
            
            w_res = requests.get(w_url).json()
            # Fallback if date range causes error
            if "error" in w_res:
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&timezone=auto"
                w_res = requests.get(w_url).json()
            
            return lat, lon, country, w_res['daily']['time'], w_res['daily']['temperature_2m_max']
    except: pass
    return 23.0, 120.2, "Unknown", [], []

@st.cache_data(ttl=3600)
def search_media(query, mode='video'):
    """Fixed search function: uses specific methods for video or image search."""
    try:
        with DDGS() as ddgs:
            if mode == 'video':
                res = list(ddgs.videos(query, max_results=3))
                if res:
                    return res[0].get('content')
            elif mode == 'image':
                res = list(ddgs.images(f"{query} official transit metro map high resolution", max_results=3))
                return res[0]["image"] if res else None
    except Exception as e:
        st.error(f"搜尋出錯: {e}")
    return None

@st.cache_data(ttl=24 * 3600)
def search_metro_map(city, retries=3):
    """Search for metro map using DuckDuckGo with retry logic."""
    query = f"{city} metro map site:wikipedia.org OR site:official"
    for attempt in range(retries):
        try:
            time.sleep(random.uniform(1.5, 3.0))
            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=1))
                if results:
                    return results[0].get("image")
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(random.uniform(2.0, 4.0))
    return None