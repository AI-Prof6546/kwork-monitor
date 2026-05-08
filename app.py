import streamlit as st
import pandas as pd
from datetime import date
import time

st.set_page_config(
    page_title="Kwork Монитор ИИ-заказов",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== ПРЕМИУМ ТЁМНАЯ ТЕМА ====================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0c14 0%, #0e1117 100%); }
    .main-header { 
        background: linear-gradient(90deg, #1a1f2e 0%, #252b3d 100%); 
        padding: 24px 32px; border-radius: 20px; margin-bottom: 24px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid #2a3142; 
    }
    .metric-card { 
        background: #1a1f2e; border-radius: 16px; padding: 20px 24px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.35); border: 1px solid #2a3142; 
    }
    .stDataFrame { 
        border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.45); 
        border: 1px solid #2a3142; 
    }
    .stTabs [data-baseweb="tab"] { 
        background: #252b3d; border-radius: 12px; padding: 14px 24px; 
        font-weight: 600; 
    }
    .stTabs [aria-selected="true"] { 
        background: linear-gradient(90deg, #00ff9d 0%, #00cc7a 100%); 
        color: #0a0c14 !important; font-weight: 700; 
    }
</style>
""", unsafe_allow_html=True)

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

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStd09qZjRsRPMB_mN0HgEB6dDL2UPAELc59_IxnFroSvWgR984VUcvzm3zn8dyhsP7Q5hk1iq9WXDS/pub?output=csv"

@st.cache_data(ttl=2, show_spinner=False)
def load_data():
    try:
        df = pd.read_csv(CSV_URL, on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        
        # === УМНАЯ АВТОМАТИЧЕСКАЯ КОРРЕКТИРОВКА КОЛОНОК ===
        col_map = {}
        for col in df.columns:
            c = col.lower()
            if 'дата' in c or 'время' in c or 'time' in c:
                col_map[col] = 'Дата'
            elif 'приоритет' in c or 'priority' in c:
                col_map[col] = 'Приоритет'
            elif 'категория' in c or 'category' in c:
                col_map[col] = 'Категория'
            elif 'заголовок' in c or 'title' in c:
                col_map[col] = 'Заголовок'
            elif 'бюджет' in c or 'budget' in c:
                col_map[col] = 'Бюджет'
            elif 'предложен' in c or 'proposal' in c:
                col_map[col] = 'Предложений'
            elif 'описан' in c or 'description' in c:
                col_map[col] = 'Описание'
            elif 'ссылк' in c or 'url' in c or 'link' in c:
                col_map[col] = 'Ссылка'
        
        df = df.rename(columns=col_map)
        
        # Если колонок меньше 8 — добавляем недостающие
        required = ['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка']
        for col in required:
            if col not in df.columns:
                df[col] = ""
        
        df = df[required]  # оставляем только нужные колонки в правильном порядке
        df = df.dropna(subset=['Заголовок'])
        df = df[df['Заголовок'].astype(str).str.strip() != ""]
        
        # Преобразуем дату
        df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
        df = df.sort_values(by='Дата', ascending=False).reset_index(drop=True)
        
        return df
    except Exception:
        return pd.DataFrame(columns=['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка'])

df = load_data()

# ==================== МЕТРИКИ ====================
def safe_count(column, pattern):
    if df.empty or column not in df.columns:
        return 0
    try:
        return int(df[column].astype(str).str.contains(pattern, case=False, na=False).sum())
    except:
        return 0

total = len(df)
high_priority = safe_count("Приоритет", "💎|ВЫСОКИЙ")
today_count = safe_count("Дата", str(date.today()))

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("📦 Всего заказов", total)
with col2: st.metric("💎 Высокий приоритет", high_priority)
with col3: st.metric("📅 Сегодня", today_count)
with col4: st.metric("📥 Загружено строк", total)

st.divider()

# ==================== ГЛАВНАЯ ТАБЛИЦА ====================
st.subheader("📋 Все заказы (новые сверху)")

if df.empty:
    st.info("📭 Пока нет заказов. Первые данные появятся в течение 1–2 минут.")
else:
    st.dataframe(
        df,
        use_container_width=True,
        height=520,
        column_config={
            "Дата": st.column_config.DatetimeColumn("Дата", format="DD.MM.YY HH:mm"),
            "Заголовок": st.column_config.TextColumn(width=420),
            "Описание": st.column_config.TextColumn(width=580),
            "Ссылка": st.column_config.LinkColumn("Действие", display_text="🔗 Открыть заказ", width=140),
        },
        hide_index=True
    )

st.divider()

# ==================== ВКЛАДКИ (максимально стабильная фильтрация) ====================
st.subheader("📂 Заказы по направлениям")

tab_names = [
    "🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop/Видео монтаж",
    "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие заказы"
]

tabs = st.tabs(tab_names)

def show_tab(tab_index, keywords):
    with tabs[tab_index]:
        if df.empty or "Категория" not in df.columns:
            st.info("📭 Нет данных")
            return
        
        # === УМНАЯ ФИЛЬТРАЦИЯ (ловит все вариации) ===
        if tab_index == 6:  # Другие заказы
            mask = ~df['Категория'].astype(str).str.contains(
                "Figma|Фото|Видео|Photoshop|Excel|WB|OZON|Grok", case=False, na=False
            )
        else:
            # Для Grok 4.3 ловим и "Grok 4.3", и "Grok", и "Grok4.3"
            mask = df['Категория'].astype(str).str.contains(keywords, case=False, na=False, regex=True)
        
        filtered = df[mask]
        
        if filtered.empty:
            st.info(f"📭 Пока нет заказов в этой категории")
        else:
            st.dataframe(
                filtered,
                use_container_width=True,
                height=320,
                column_config={
                    "Дата": st.column_config.DatetimeColumn("Дата", format="DD.MM HH:mm"),
                    "Заголовок": st.column_config.TextColumn(width=400),
                    "Описание": st.column_config.TextColumn(width=520),
                    "Ссылка": st.column_config.LinkColumn("Действие", display_text="🔗 Открыть", width=120),
                },
                hide_index=True
            )

# Привязка вкладок
show_tab(0, "Figma")
show_tab(1, "Фото|Видео ИИ")
show_tab(2, "Photoshop|Видео монтаж")
show_tab(3, "Excel|PDF")
show_tab(4, "WB|OZON")
show_tab(5, "Grok")          # ← ловит "Grok 4.3", "Grok", "Grok4.3" и т.д.
show_tab(6, "")              # Другие заказы

# ==================== АВТООБНОВЛЕНИЕ ====================
time.sleep(0.8)
st.rerun()
