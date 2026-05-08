import streamlit as st
import pandas as pd
from datetime import datetime, date
import time

# ==================== КОНФИГУРАЦИЯ ====================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStd09qZjRsRPMB_mN0HgEB6dDL2UPAELc59_IxnFroSvWgR984VUcvzm3zn8dyhsP7Q5hk1iq9WXDS/pub?output=csv"

st.set_page_config(
    page_title="Kwork Монитор ИИ-заказов",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== ПРЕМИУМ ТЁМНАЯ ТЕМА ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Space+Grotesk:wght@500;600&amp;display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0c14 0%, #0e1117 100%);
        font-family: 'Inter', system_ui, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1a1f2e 0%, #252b3d 100%);
        padding: 24px 32px;
        border-radius: 20px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 1px solid #2a3142;
    }
    
    .metric-card {
        background: #1a1f2e;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        border: 1px solid #2a3142;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 255, 157, 0.15);
    }
    
    .stMetric {
        background: transparent !important;
    }
    
    .stMetric label {
        font-size: 13px !important;
        color: #8b92a8 !important;
        font-weight: 500 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    .stDataFrame {
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        border: 1px solid #2a3142;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #1a1f2e;
        padding: 8px;
        border-radius: 16px;
        margin-bottom: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #252b3d;
        border-radius: 12px;
        padding: 14px 26px;
        font-size: 15px;
        font-weight: 600;
        color: #c5cad8;
        transition: all 0.2s ease;
        border: 1px solid #2a3142;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #2f3548;
        color: #00ff9d;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00ff9d 0%, #00cc7a 100%);
        color: #0a0c14 !important;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(0, 255, 157, 0.3);
    }
    
    .section-title {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
        margin: 24px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .premium-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #2a3142, transparent);
        margin: 20px 0;
    }
    
    .stTextInput > div > div > input {
        background: #1a1f2e;
        border: 1px solid #2a3142;
        border-radius: 12px;
        color: white;
        font-size: 15px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ff9d;
        box-shadow: 0 0 0 3px rgba(0, 255, 157, 0.15);
    }
    
    .footer {
        text-align: center;
        color: #5a6278;
        font-size: 12px;
        margin-top: 40px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ЗАГОЛОВОК ====================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:42px; font-weight:800; background: linear-gradient(90deg, #ffffff, #c5cad8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🤖 Kwork Монитор ИИ-заказов
    </h1>
    <p style="margin:8px 0 0 0; font-size:18px; color:#00ff9d; font-weight:600;">
        🔥 Реальное время • Обновление каждые 2 секунды
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== ЗАГРУЗКА ДАННЫХ (максимально защищённая) ====================
@st.cache_data(ttl=2, show_spinner=False)
def load_data():
    try:
        df = pd.read_csv(CSV_URL, on_bad_lines='skip', encoding='utf-8')
        df = df.dropna(how='all')
        
        # Приводим названия колонок к единому виду (на случай разных версий)
        column_mapping = {
            'time': 'Время', 'timestamp': 'Время', 'date': 'Время',
            'category': 'Категория', 'cat': 'Категория',
            'priority': 'Приоритет', 'prio': 'Приоритет', 'color': 'Приоритет',
            'title': 'Заголовок', 'name': 'Заголовок',
            'description': 'Описание', 'desc': 'Описание',
            'url': 'Ссылка', 'link': 'Ссылка', 'href': 'Ссылка',
            'proposals': 'Предложений', 'offers': 'Предложений', 'count': 'Предложений'
        }
        
        for old, new in column_mapping.items():
            if old in df.columns and new not in df.columns:
                df = df.rename(columns={old: new})
        
        # Создаём отсутствующие колонки
        required = ['Время', 'Категория', 'Приоритет', 'Заголовок', 'Описание', 'Ссылка', 'Предложений']
        for col in required:
            if col not in df.columns:
                df[col] = ""
        
        # Очистка
        df['Время'] = pd.to_datetime(df['Время'], errors='coerce')
        df['Предложений'] = pd.to_numeric(df['Предложений'], errors='coerce').fillna(0).astype(int)
        df = df.fillna("")
        
        return df
    except Exception:
        return pd.DataFrame(columns=['Время', 'Категория', 'Приоритет', 'Заголовок', 'Описание', 'Ссылка', 'Предложений'])

# ==================== ОСНОВНОЙ ФРАГМЕНТ (обновление без мерцания) ====================
@st.fragment(run_every=2)
def show_dashboard():
    df = load_data()
    
    if df.empty or len(df) == 0:
        st.warning("📭 Таблица пока пуста. Первые заказы появятся в течение минуты.", icon="⏳")
        st.info("🔄 Страница автоматически обновляется каждые 2 секунды")
        return
    
    # ==================== 4 МЕТРИКИ ====================
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    total = len(df)
    high_priority = len(df[df['Приоритет'].astype(str).str.contains('💎|ВЫСОКИЙ|high', case=False, na=False)])
    
    today = date.today()
    df['Время'] = pd.to_datetime(df['Время'], errors='coerce')
    today_count = int((df['Время'].dt.date == today).sum()) if not df['Время'].isna().all() else 0
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 Всего заказов", f"{total:,}", delta=f"+{total - 5}" if total > 5 else None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💎 Высокий приоритет", high_priority, delta_color="normal")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📅 Сегодня", today_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📥 Загружено строк", f"{total:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
    
    # ==================== ПОИСК ====================
    search_query = st.text_input(
        "🔍 Поиск по всем заказам",
        placeholder="Введите часть заголовка, описания или категории...",
        key="global_search",
        label_visibility="collapsed"
    )
    
    if search_query:
        mask = (
            df['Заголовок'].astype(str).str.contains(search_query, case=False, na=False) |
            df['Описание'].astype(str).str.contains(search_query, case=False, na=False) |
            df['Категория'].astype(str).str.contains(search_query, case=False, na=False)
        )
        filtered_df = df[mask].copy()
    else:
        filtered_df = df.copy()
    
    # ==================== ГЛАВНАЯ ТАБЛИЦА ====================
    st.markdown('<div class="section-title">📋 Все заказы <span style="font-size:14px; color:#5a6278;">(всегда видна • занимает почти весь экран)</span></div>', unsafe_allow_html=True)
    
    display_df = filtered_df[['Время', 'Категория', 'Приоритет', 'Заголовок', 'Описание', 'Предложений', 'Ссылка']].copy()
    
    # Красивый формат времени
    display_df['Время'] = display_df['Время'].dt.strftime('%d.%m.%Y %H:%M')
    
    column_config = {
        "Время": st.column_config.DatetimeColumn(
            "Время",
            format="DD.MM.YY HH:mm",
            width="small"
        ),
        "Категория": st.column_config.TextColumn("Категория", width="small"),
        "Приоритет": st.column_config.TextColumn("Приоритет", width="small"),
        "Заголовок": st.column_config.TextColumn("Заголовок", width="large"),
        "Описание": st.column_config.TextColumn("Описание", width="large"),
        "Предложений": st.column_config.NumberColumn("Предложений", format="%d", width="small"),
        "Ссылка": st.column_config.LinkColumn(
            "Действие",
            help="Открыть заказ на Kwork.ru",
            display_text="🔗 Открыть заказ",
            width="small"
        )
    }
    
    # Подсветка высокого приоритета (зелёный фон)
    def highlight_high_priority(row):
        if '💎' in str(row.get('Приоритет', '')) or 'ВЫСОКИЙ' in str(row.get('Приоритет', '')).upper():
            return pd.Series(['background-color: #0d3b2e; color: #00ff9d; font-weight: 500'] * len(row), index=row.index)
        return pd.Series([''] * len(row), index=row.index)
    
    try:
        styled_df = display_df.style.apply(highlight_high_priority, axis=1)
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=520,
            column_config=column_config,
            hide_index=True
        )
    except:
        st.dataframe(
            display_df,
            use_container_width=True,
            height=520,
            column_config=column_config,
            hide_index=True
        )
    
    # ==================== ВКЛАДКИ ПО НАПРАВЛЕНИЯМ ====================
    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📂 Заказы по направлениям</div>', unsafe_allow_html=True)
    
    tab_names = [
        "🎨 Figma",
        "🖼️ Фото/Видео ИИ",
        "📸 Photoshop/Видео монтаж",
        "📊 Excel/PDF",
        "🛒 WB/OZON",
        "🤖 Grok 4.3",
        "📦 Другие заказы"
    ]
    
    tabs = st.tabs(tab_names)
    
    for i, tab in enumerate(tabs):
        with tab:
            cat_name = tab_names[i].split(" ", 1)[1]
            
            # Гибкий поиск категории
            if "Другие" in cat_name:
                mask = ~df['Категория'].astype(str).str.contains(
                    "Figma|Фото|Видео|Photoshop|Excel|WB|OZON|Grok", case=False, na=False
                )
            else:
                keywords = cat_name.split("/")
                mask = df['Категория'].astype(str).str.contains(keywords[0], case=False, na=False)
            
            tab_df = df[mask].copy()
            
            if tab_df.empty:
                st.info(f"📭 В категории «{cat_name}» пока нет заказов", icon="😴")
            else:
                tab_display = tab_df[['Время', 'Категория', 'Приоритет', 'Заголовок', 'Описание', 'Предложений', 'Ссылка']].copy()
                tab_display['Время'] = tab_display['Время'].dt.strftime('%d.%m %H:%M')
                
                st.dataframe(
                    tab_display,
                    use_container_width=True,
                    height=280,
                    column_config=column_config,
                    hide_index=True
                )
                st.caption(f"Всего в категории: **{len(tab_df)}** заказов • Высокий приоритет: **{len(tab_df[tab_df['Приоритет'].astype(str).str.contains('💎', na=False)])}**")

# ==================== ЗАПУСК ====================
show_dashboard()

# ==================== ФУТЕР ====================
st.markdown("""
<div class="footer">
    🤖 Kwork Monitor v64 • Streamlit 2026 • Данные обновляются автоматически из Google Sheets<br>
    <span style="font-size:10px;">Защита от ошибок: включена • Кликабельные ссылки • Тёмная премиум-тема</span>
</div>
""", unsafe_allow_html=True)
