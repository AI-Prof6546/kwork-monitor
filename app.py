import streamlit as st
import pandas as pd
from datetime import datetime, date
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
    .stApp { background: linear-gradient(135deg, #0a0c14 0%, #0e1117 100%); font-family: 'Inter', sans-serif; }
    .main-header { background: linear-gradient(90deg, #1a1f2e 0%, #252b3d 100%); padding: 24px 32px; border-radius: 20px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid #2a3142; }
    .metric-card { background: #1a1f2e; border-radius: 16px; padding: 20px 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.35); border: 1px solid #2a3142; }
    .stDataFrame { border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.45); border: 1px solid #2a3142; }
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

# ==================== ЗАГРУЗКА ДАННЫХ ====================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStd09qZjRsRPMB_mN0HgEB6dDL2UPAELc59_IxnFroSvWgR984VUcvzm3zn8dyhsP7Q5hk1iq9WXDS/pub?output=csv"

@st.cache_data(ttl=2, show_spinner=False)
def load_data():
    try:
        df = pd.read_csv(CSV_URL, on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Дата", "Приоритет", "Категория", "Заголовок", "Описание", "Предложений", "Ссылка"])

df = load_data()

# ==================== БЕЗОПАСНЫЕ МЕТРИКИ ====================
def safe_count(col, pattern):
    if df.empty or col not in df.columns:
        return 0
    try:
        return len(df[df[col].astype(str).str.contains(pattern, na=False)])
    except:
        return 0

total = len(df)
high_priority = safe_count("Приоритет", "💎")
today_count = safe_count("Дата", str(date.today()))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📦 Всего заказов", total)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💎 Высокий приоритет", high_priority)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📅 Сегодня", today_count)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📥 Загружено строк", total)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==================== ГЛАВНАЯ ТАБЛИЦА ====================
st.subheader("📋 Все заказы")
if df.empty:
    st.info("📭 Пока нет заказов. Первые данные появятся в течение 1–2 минут.")
else:
    st.dataframe(
        df,
        use_container_width=True,
        height=480,
        column_config={
            "Ссылка": st.column_config.LinkColumn("Открыть", display_text="🔗 Открыть", width=130),
            "Заголовок": st.column_config.TextColumn(width=400),
            "Описание": st.column_config.TextColumn(width=600),
        },
        hide_index=True
    )

st.divider()

# ==================== ВКЛАДКИ ====================
st.subheader("📂 Заказы по направлениям")
tabs = st.tabs(["🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop/Видео монтаж", "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие заказы"])

def show_tab(keyword):
    if df.empty:
        st.info("Нет данных")
        return
    filtered = df[df.get("Категория", "").astype(str).str.contains(keyword, na=False)]
    if filtered.empty:
        st.info(f"Пока нет заказов в категории «{keyword}»")
    else:
        st.dataframe(
            filtered,
            use_container_width=True,
            height=320,
            column_config={
                "Ссылка": st.column_config.LinkColumn("Открыть", display_text="🔗 Открыть", width=130),
                "Заголовок": st.column_config.TextColumn(width=400),
                "Описание": st.column_config.TextColumn(width=600),
            },
            hide_index=True
        )

with tabs[0]: show_tab("Figma")
with tabs[1]: show_tab("Фото/Видео ИИ")
with tabs[2]: show_tab("Photoshop|Видео монтаж")
with tabs[3]: show_tab("Excel/PDF")
with tabs[4]: show_tab("WB/OZON")
with tabs[5]: show_tab("Grok 4.3")
with tabs[6]: show_tab("Другие заказы")

# Автообновление
time.sleep(0.5)
st.rerun()
