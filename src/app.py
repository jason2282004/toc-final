# app.py
import streamlit as st
import pandas as pd
import time
import random
import concurrent.futures
from datetime import datetime

# Import custom modules
import config as config
import services
from utils import render_sticky_note, extract_video_id

# --- Page Configuration ---
st.set_page_config(page_title="靈魂旅伴 —— 最懂你的 MBTI 旅遊導航員", layout="wide")

# --- UI Container Initialization ---
main_container = st.empty()

# --- State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 'INPUT'

# STEP 1: INPUT PAGE
if st.session_state.step == 'INPUT':
    st.title("靈魂旅伴 —— 最懂你的 MBTI 旅遊導航員")
    
    city_names = list(config.POPULAR_CITIES.keys())

    st.markdown("### 🎲 不知道去哪？讓 AI 幫你選個好地方！")
    wheel_placeholder = st.empty()
    
    tick_sound = "https://www.soundjay.com/buttons/button-27.mp3" # Ticking sound
    win_sound = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" # Winning sound

    if st.button("我抽一個"):
        # Animation loop for the wheel
        for i in range(20):
            random_display = random.choice(city_names)
            
            wheel_placeholder.markdown(f"""
                <div style="text-align:center; padding:30px; background-color:#ffffff; border-radius:15px; border:3px solid #ff4b4b; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                    <h1 style="color:#ff4b4b; margin:0; font-size: 3rem;">🌀 {random_display}</h1>
                </div>
                <audio autoplay>
                    <source src="{tick_sound}" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)
            
            time.sleep(0.05 + (i * 0.01))
        
        final_display = random.choice(city_names)
        final_city_pure = config.POPULAR_CITIES[final_display]
        
        wheel_placeholder.markdown(f"""
            <div style="text-align:center; padding:30px; background-color:#ff4b4b; border-radius:15px; box-shadow: 0 4px 15px rgba(255,75,75,0.4);">
                <h1 style="color:white; margin:0; font-size: 3.5rem;">🎯 {final_display}</h1>
            </div>
            <audio autoplay>
                <source src="{win_sound}" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)
        
        st.session_state.city_input = final_city_pure
        time.sleep(1.2) 
        st.rerun()

    st.divider()

    if 'city_input' not in st.session_state:
        st.session_state.city_input = "Tokyo"

    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("📍 目的地城市", key="city_input")
    with col2:
        today = datetime.now().date()
        travel_dates = st.date_input("📅 預計旅行日期", [today, today + pd.Timedelta(days=6)])

    user_context = st.text_area("✍️ 簡單說一下您的旅行個性", placeholder="例如：想睡到自然醒、受夠J人朋友咄咄逼人叫我排行程")

    if st.button("開始規劃嚕 →"):
        if len(travel_dates) < 2:
            st.warning("請選擇完整日期。")
        else:
            with st.spinner("正在規劃中，請您別急..."):
                st.session_state.location_en = services.translate_to_english(location)
                st.session_state.location = location
                st.session_state.start_date = travel_dates[0]
                st.session_state.end_date = travel_dates[1]
                st.session_state.user_context = user_context
                st.session_state.step = 'DASHBOARD'
                st.rerun()

# STEP 2: DASHBOARD PAGE
elif st.session_state.step == 'DASHBOARD':
    st.title(f"🌍 {st.session_state.location} 完整的旅遊規劃")
    current_city_en = st.session_state.get('location_en', 'Tokyo')
    current_city_cn = st.session_state.get('location', '東京')

    flight_url = f"https://www.google.com/travel/flights?q=Flights+to+{current_city_en}"
    booking_url = f"https://www.booking.com/searchresults.html?ss={current_city_en}"
    klook_url = f"https://www.klook.com/zh-TW/search?query={current_city_cn}"

    # Custom CSS for Floating Navigation
    st.markdown(f"""
        <style>
        .floating-nav {{
            position: fixed;
            top: 70px;
            right: 30px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        .nav-icon {{
            background-color: white;
            border: 3px solid #f0f2f6;
            border-radius: 50%;
            width: 65px;
            height: 65px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 35px;
            text-decoration: none;
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        .nav-icon:hover {{
            transform: scale(1.15) rotate(5deg);
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            border-color: #4285F4; /* Google Blue */
            background-color: #fffafa;
        }}
        /* Tooltip text */
        .nav-icon::before {{
            content: attr(data-title);
            position: absolute;
            right: 80px;
            font-size: 14px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px 12px;
            border-radius: 8px;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }}
        .nav-icon:hover::before {{
            opacity: 1;
        }}
        </style>
        
        <div class="floating-nav">
            <a href="{flight_url}" target="_blank" class="nav-icon" data-title="Google 機票比價">✈️</a>
            <a href="{booking_url}" target="_blank" class="nav-icon" data-title="Booking.com 訂房">🏠</a>
            <a href="{klook_url}" target="_blank" class="nav-icon" data-title="Klook 找行程">🎫</a>
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("正在抓取全球資料庫資訊，請您不要急..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Parallel execution of API calls
            future_geo = executor.submit(services.get_location_data, st.session_state.location_en, st.session_state.start_date, st.session_state.end_date)
            future_wiki = executor.submit(services.get_wikipedia_summary, st.session_state.location_en)
            future_music = executor.submit(services.search_media, f"{st.session_state.location} ambient music", mode='video')
            future_map_img = executor.submit(services.search_media, f"{st.session_state.location} metro map", mode='image')

            lat, lon, country, w_dates, w_temps = future_geo.result()
            wiki_summary,wiki_img = future_wiki.result()
            music_url = future_music.result()
            transport_map_url = future_map_img.result()

    # --- Sidebar ---
    with st.sidebar:
        st.header("📊 小工具")
        
        st.write("💱 **匯率查詢**")
        
        search_query = f"TWD to {country} exchange rate"
        google_finance_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        st.link_button(f"💹 查看台幣對 {country} currency的即時匯率", google_finance_url)
        st.caption("💡 點一下我就幫你估狗查詢最即時的匯率資訊ㄡ")

        st.divider()
        if music_url:
            vid = extract_video_id(music_url)
            st.components.v1.html(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{vid}?autoplay=1" allow="autoplay"></iframe>', height=170)
        st.button("← 返回", on_click=lambda: st.session_state.update({"step": "INPUT"}))

    tabs = st.tabs([
        "城市簡介",
        "氣象數據",
        "交通、景點住宿規劃",
        "出入境規定",
        "來看看別人怎麼玩的",
        "mbti個人化行程規劃"
    ])
    
    # --- Tab 1: City Introduction ---
    with tabs[0]:
        display_img = wiki_img if wiki_img else f"https://loremflickr.com/1200/400/city,{st.session_state.location_en}"
        st.markdown(f"""
            <div style="position: relative; width: 100%; height: 350px; border-radius: 20px; 
                        background-image: linear-gradient(to bottom, rgba(0,0,0,0) 30%, rgba(0,0,0,0.8) 100%), url('{display_img}');
                        background-size: cover; background-position: center; display: flex; align-items: flex-end; padding: 30px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <h1 style="color: white; font-size: 4rem; text-shadow: 2px 2px 15px rgba(0,0,0,0.8); margin: 0; font-family: 'Arial Black', sans-serif;">
                    {st.session_state.location.upper()}
                </h1>
            </div>
        """, unsafe_allow_html=True)
        st.write("") 

        # Fact caching logic
        if 'facts_cache' not in st.session_state or st.session_state.get('facts_city') != st.session_state.location:
            with st.spinner("🚀 正在執行城市資訊，請您稍後..."):
                fact_prompt = f"請提供 {st.session_state.location} 的 1.官方語言 2.時區 3.必吃的代表性食物。請用極簡字詞回答，格式：語言|時區|食物"
                facts_raw = services.call_llm(fact_prompt, sys_msg="旅遊顧問")
                if facts_raw and "|" in facts_raw:
                    st.session_state.facts_cache = facts_raw.split("|")
                    st.session_state.facts_city = st.session_state.location

        if 'facts_cache' in st.session_state:
            lang, tz, food = st.session_state.facts_cache
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("#### 🗣️ 語言")
                st.info(lang.strip())
            with c2:
                st.markdown("#### ⏰ 時區")
                st.info(tz.strip())
            with c3:
                st.markdown("#### 🍛 必吃")
                st.info(food.strip())

        st.divider()

        st.markdown(f"### 關於 {st.session_state.location} 的介紹")
        
        # Introduction generation logic
        if 'intro_cache' not in st.session_state or st.session_state.get('intro_city') != st.session_state.location:
            with st.status("✍️ 正在為您量身打造城市介紹，請稍後...", expanded=True) as status:
                intro_prompt = f"""
                你是一位資深旅遊文學作家。請為：{st.session_state.location} 撰寫一段迷人的城市深度簡介（約 400 字）。
                用戶背景：{st.session_state.user_context}
                請包含：城市的氛圍感、歷史痕跡、以及為什麼適合該用戶。語氣要優雅且感性。
                """
                ai_intro = services.call_llm(intro_prompt, sys_msg="你是一位捕捉城市溫度的作家。")
                if ai_intro:
                    st.session_state.intro_cache = ai_intro.replace('\n', '<br>')
                    st.session_state.intro_city = st.session_state.location
                    status.update(label="請看請看！", state="complete")

        if 'intro_cache' in st.session_state:
            st.markdown(f"""
                <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; border: 1px solid #e1e4e8;
                            line-height: 1.8; color: #24292e; font-size: 1.1rem; text-align: justify; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    {st.session_state.intro_cache}
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📍 地理位置")
        mini_map = f"https://maps.google.com/maps?q={st.session_state.location_en}&hl=zh-TW&z=10&output=embed"
        st.components.v1.html(f'<iframe src="{mini_map}" width="100%" height="300" style="border-radius:15px; border:none; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"></iframe>', height=310)
    
    # --- Tab 2: Weather Data ---
    with tabs[1]:
        st.subheader(f"🌦️ 動態氣象圖 ({st.session_state.start_date} 至 {st.session_state.end_date})")
        
        windy_src = f"https://embed.windy.com/embed2.html?lat={lat}&lon={lon}&zoom=8&level=surface&overlay=wind&menu=&message=&marker=&type=map&location={st.session_state.location_en}&metricTemp=c"
        st.components.v1.html(f'<iframe src="{windy_src}" width="100%" height="400" frameborder="0"></iframe>', height=410)

        st.divider()
        
        if w_temps:
            current_weather_id = f"{st.session_state.location}_{st.session_state.start_date}_{st.session_state.end_date}"
            
            # Weather analysis caching logic
            if 'weather_cache' not in st.session_state or st.session_state.get('weather_id') != current_weather_id:
                avg_temp = sum(w_temps) / len(w_temps)
                max_temp = max(w_temps)
                min_temp = min(w_temps)
                trend = "上升" if w_temps[-1] > w_temps[0] else "下降"
                
                with st.spinner("🌡️ AI 正在分析氣象數據..."):
                    prompt = f"""
                    您是一位專業旅遊氣象分析師。目的地：{st.session_state.location}
                    旅行區間：{st.session_state.start_date} 到 {st.session_state.end_date}
                    數據：平均 {avg_temp:.1f}°C, 最高 {max_temp}°C, 最低 {min_temp}°C。
                    用戶背景：{st.session_state.user_context}
                    請提供簡短趨勢總結與穿著建議（200字內）。
                    """
                    st.session_state.weather_cache = services.call_llm(prompt)
                    st.session_state.weather_id = current_weather_id
                    st.session_state.weather_metrics = {"avg": avg_temp, "max": max_temp, "trend": trend, "count": len(w_temps)}

            m = st.session_state.weather_metrics
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.metric("平均溫度", f"{m['avg']:.1f}°C", m['trend'])
                st.metric("預測最高溫", f"{m['max']}°C")
            with col_b:
                st.markdown("### 🎙️ AI 為您打造的專屬氣象報告")
                st.info(st.session_state.weather_cache)
    
    # --- Tab 3: Transport & Attractions ---
    with tabs[2]:
        st.subheader(f"🚆 {st.session_state.location} 大眾運輸與交通建議")
        
        if 'transport_overview' not in st.session_state:
            st.session_state.transport_overview = ""

        if st.button("🧠 產生 AI 專屬交通分析"):
            with st.spinner(f"正在為您提供 {st.session_state.location} 的交通建議..."):
                transport_prompt = f"""
                你是一位資深的全球旅遊交通顧問。
                目的地：{st.session_state.location}
                用戶旅行個性與需求：{st.session_state.user_context}

                請針對該城市提供一份精簡的交通建議（約 300 字）：
                1. 主要移動方式推薦（例如：地鐵、巴士或步行）。
                2. 針對「該用戶個性」的交通避坑指南。
                3. 交通卡建議（例如：Suica, Oyster Card 等）。
                
                請使用繁體中文，並用條列式呈現，語氣專業且實用。
                """
                st.session_state.transport_overview = services.call_llm(transport_prompt, sys_msg="你是一位專業的交通導航專家。")

        if st.session_state.transport_overview:
            html_transport = st.session_state.transport_overview.replace('\n', '<br>')
            
            st.markdown(f"""
                <div style="background-color: #e3f2fd; padding: 20px; border-radius: 12px; border-left: 5px solid #2196f3; margin-bottom: 25px;">
                    <h4 style="margin-top:0; color:#1565c0;">🎙️ AI 為您打造的專屬氣象報告</h4>
                    <div style="color: #0d47a1; line-height: 1.6;">
                        {html_transport}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.divider()
        city = st.session_state.location_en
        st.markdown("#### 🚇 城市交通圖 (by Google Transit)")
        google_transit_url = f"https://maps.google.com/maps?q={city}&hl=zh-TW&z=14&t=m&layer=t&output=embed"
        
        st.components.v1.html(f"""
            <div style="border: 2px solid #10ac84; border-radius: 15px; overflow: hidden;">
                <iframe width="100%" height="450" frameborder="0" src="{google_transit_url}"></iframe>
            </div>
        """, height=470)

        st.markdown("---")

        st.markdown("#### 📂 交通平面圖 ")
        st.info("💡 平面圖不能顯示真實地理座標，但最適合旅程中的轉乘，請至下列連結看看")
        
        search_query = f"{city} metro map schematic official filetype:pdf"
        google_search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        st.link_button(f"🔍 在 Google 搜尋 {city} 官方路線圖", google_search_url)

        st.markdown("---")

        with st.expander("📍 其他資訊 (景點與住宿)"):
            st.markdown("### 🏛️ 主要景點")
            st.components.v1.iframe(f"https://www.google.com/maps?q={city}+attractions&output=embed", height=400)
            
            st.divider()
            
            st.markdown("### 🏨 熱門住宿")
            st.components.v1.iframe(f"https://www.google.com/maps?q={city}+hotels&output=embed", height=400)
    
    # --- Tab 4: Entry Rules ---
    with tabs[3]:
        st.subheader("🛫 出入境與簽證規定")

        links = services.search_entry_rules(country)

        if links:
            st.markdown("### 🔗 參考連結")
            for l in links:
                st.markdown(f"- {l}")
        
        st.markdown("---")
        if st.button("🧠 按一下將由 AI 幫您生成懶人包"):
            source_text = chr(10).join(links) if links else "一般公開旅遊規定"
            
            with st.spinner(f"正在整理 {country} 的出入境規定..."):
                prompt = f"""
                請根據目前的公開規定，整理台灣護照前往 {country} 的：

                1. 是否免簽
                2. 最長停留天數
                3. 是否需線上申請 (如：電子簽、申報卡)
                4. 特別注意事項
                
                並給我大約 300 字左右的內容，條列式呈現。
                來源參考：{source_text}
                """
                
                summary = services.call_llm(prompt, sys_msg="你是嚴謹的移民與簽證資訊整理助理。")
                
                if summary:
                    st.success(summary)
                else:
                    st.error("暫時無法生成懶人包，請稍後再試。")

    # --- Tab 5: Vlog & Sticky Notes ---
    with tabs[4]:
        st.subheader(f"🎬 {st.session_state.location} 精選Vlog與旅人留聲機")
        
        v_url = services.search_media(f"{st.session_state.location} travel guide 2025")
        if v_url:
            st.video(v_url)
        
        st.divider()

        # Sticky Notes logic
        if 'last_city_notes' not in st.session_state or st.session_state.last_city_notes != st.session_state.location:
            st.session_state.last_city_notes = st.session_state.location
            st.session_state.user_notes = []
            
            with st.spinner("正在釘上其他旅人的便利貼..."):
                ai_prompt = f"請模擬 4 位剛從 {st.session_state.location} 回來的台灣旅人，每人寫下一句15字內的私藏心得。格式：用戶名|內容"
                ai_notes_raw = services.call_llm(ai_prompt, sys_msg="你是一個幽默的旅遊論壇小編。")
                
                fixed_ai_list = []
                if ai_notes_raw:
                    for entry in ai_notes_raw.strip().split("\n"):
                        if "|" in entry:
                            u, c = entry.split("|", 1)
                            fixed_ai_list.append({
                                "user": u.strip().replace("- ", "").replace("1. ", ""),
                                "content": c.strip(),
                                "color": "#fff176" 
                            })
                st.session_state.fixed_ai_notes = fixed_ai_list

        st.markdown("### ✍️ 我也要留言 (貼上便利貼)")
        with st.expander("📝 點此撰寫您的私藏心得"):
            col_u1, col_u2 = st.columns([1, 3])
            with col_u1:
                u_name = st.text_input("您的暱稱", placeholder="匿名旅人", key="note_name")
            with col_u2:
                u_comment = st.text_input("留言內容 (限 25 字)", placeholder="打不贏袋鼠，不推薦來這裡旅遊...", key="note_content")
            
            if st.button("📌 貼上便利貼"):
                if u_comment:
                    new_note = {
                        "user": u_name if u_name else "匿名旅人",
                        "content": u_comment,
                        "color": random.choice(["#ffadad", "#ffd6a5", "#fdffb6", "#caffbf", "#9bf6ff", "#a0c4ff", "#bdb2ff", "#ffc6ff"])
                    }
                    st.session_state.user_notes.insert(0, new_note)
                    st.rerun() 

        st.divider()

        st.markdown("### 📍 旅人留言牆")
        
        display_notes = st.session_state.user_notes + st.session_state.fixed_ai_notes

        col_wall1, col_wall2 = st.columns(2)
        for i, note in enumerate(display_notes):
            target_col = col_wall1 if i % 2 == 0 else col_wall2
            with target_col:
                st.components.v1.html(
                    render_sticky_note(note['user'], note['content'], color=note['color']), 
                    height=180
                )
    
    # --- Tab 6: MBTI Planning ---
    with tabs[5]:
        st.subheader("🧠 MBTI 行程規劃")
        st.write("輸入您的人格特質，讓 AI 為您的靈魂量身打造專屬旅程。")
        
        if 'j_itinerary' not in st.session_state:
            st.session_state.j_itinerary = ""
        if 'mbti_chat_history' not in st.session_state:
            st.session_state.mbti_chat_history = []
        if 'current_mbti' not in st.session_state:
            st.session_state.current_mbti = ""

        mbti_input = st.text_input("請輸入您的 4 碼 MBTI (例如: INFJ, ENFP):", value=st.session_state.current_mbti).upper().strip()

        if st.button("🔮 開始人格分析規劃"):
            if not mbti_input or len(mbti_input) != 4:
                st.warning("⚠️ 請輸入正確的 4 碼 MBTI 代碼！")
            elif mbti_input.endswith('P'):
                st.session_state.j_itinerary = ""
                st.session_state.current_mbti = mbti_input
                st.markdown("---")
                st.error("🚫 **P 人不可以規畫行程！**")
                st.info(f"親愛的 {mbti_input} 黃豆，請自離並邊旅遊邊隨機應變，這才是p人所該做的唷<3！")
                st.components.v1.html("""
                    <div style="text-align:center; padding:20px;">
                        <h2 style="color:#ff4b4b; animation: shake 0.5s infinite;">🏃‍♂️ 嘿嘿</h2>
                    </div>
                    <style>@keyframes shake {0%{transform:translate(1px,1px)}20%{transform:translate(-3px,0px)}40%{transform:translate(1px,-1px)}100%{transform:translate(1px,-2px)}}</style>
                """, height=100)
            elif mbti_input.endswith('J'):
                st.session_state.current_mbti = mbti_input
                with st.status("🏗️ 正在為會做事的的 J 人打造專屬的行程...", expanded=True) as status:
                    st.write("🔍 分析mbti中...")
                    time.sleep(1)
                    prompt = f"目的地：{st.session_state.location}，日期：{st.session_state.start_date}到{st.session_state.end_date}，MBTI：{mbti_input}，請幫這位追求完美的 J 人規劃精確到分鐘的行程，並給予專業提醒。"
                    itinerary = services.call_llm(prompt, sys_msg="你是一位服務 J 型人格的精密規劃師。")
                    if itinerary:
                        st.session_state.j_itinerary = itinerary
                        st.session_state.mbti_chat_history = [] 
                        status.update(label="✅ 行程已生成完畢，請您查收！", state="complete", expanded=True)
            else:
                st.error("最後一碼必須是 J 或 P 喔！")

        if st.session_state.j_itinerary:
            st.divider()
            st.markdown("### 📋 J 人專屬：個人化導航行程")
            with st.container():
                st.markdown(st.session_state.j_itinerary)
            
            st.divider()
            
            st.markdown("### 💬 針對行程進一步調整？")
            
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.mbti_chat_history:
                    with st.chat_message(chat["role"]):
                        st.write(chat["content"])

            if user_query := st.chat_input("對行程有任何細節想微調嗎？請告訴我..."):
                st.session_state.mbti_chat_history.append({"role": "user", "content": user_query})
                with chat_container:
                    with st.chat_message("user"):
                        st.write(user_query)
                
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("正在根據您的需求調整計畫..."):
                            follow_up_prompt = f"原始行程：{st.session_state.j_itinerary}\n用戶問題：{user_query}"
                            answer = services.call_llm(follow_up_prompt, sys_msg="你是一位精益求精的旅遊助手。")
                            st.write(answer)
                            st.session_state.mbti_chat_history.append({"role": "assistant", "content": answer})