import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Kwork Монитор ИИ-заказов", layout="wide")

st.title("🤖 Kwork Монитор ИИ-заказов")
st.caption("🔥 Реальное время • Обновление каждые 2 секунды")

# ===================== НАСТРОЙКИ =====================
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStd09qZjRsRPMB_mN0HgEB6dDL2UPAELc59_IxnFroSvWgR984VUcvzm3zn8dyhsP7Q5hk1iq9WXDS/pub?output=csv"

@st.cache_data(ttl=2)
def load_orders():
    try:
        df = pd.read_csv(CSV_URL, on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame(columns=["Дата", "Приоритет", "Категория", "Заголовок", "Бюджет", "Предложений", "Описание", "Ссылка"])

df = load_orders()

# ===================== БЕЗОПАСНЫЕ МЕТРИКИ =====================
def safe_metric(column, pattern, default=0):
    if df.empty or column not in df.columns:
        return default
    try:
        return len(df[df[column].astype(str).str.contains(pattern, na=False)])
    except:
        return default

total = len(df)
high_priority = safe_metric("Приоритет", "💎")
today_str = str(datetime.now().date())
today = safe_metric("Дата", today_str)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Всего заказов", total)
col2.metric("Высокий приоритет", high_priority)
col3.metric("Сегодня", today)
col4.metric("Загружено строк из Google", len(df))

st.divider()

# ===================== ВКЛАДКИ =====================
tabs = st.tabs([
    "📋 Все заказы", "🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop/Видео монтаж",
    "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие заказы"
])

def show_table(filtered_df, title=""):
    if filtered_df.empty:
        st.info("Пока нет заказов в этой категории")
        return
    column_config = {
        "Ссылка": st.column_config.LinkColumn("Открыть заказ", display_text="🔗 Открыть", width=130),
        "Заголовок": st.column_config.TextColumn("Заголовок", width=400),
        "Описание": st.column_config.TextColumn("Описание", width=500),
    }
    st.dataframe(filtered_df, use_container_width=True, column_config=column_config, hide_index=True)

with tabs[0]:
    show_table(df)

with tabs[1]:
    show_table(df[df.get("Категория", "").str.contains("Figma", na=False)])

with tabs[2]:
    show_table(df[df.get("Категория", "").str.contains("Фото/Видео ИИ", na=False)])

with tabs[3]:
    show_table(df[df.get("Категория", "").str.contains("Photoshop|Видео монтаж", na=False, regex=True)])

with tabs[4]:
    show_table(df[df.get("Категория", "").str.contains("Excel/PDF", na=False)])

with tabs[5]:
    show_table(df[df.get("Категория", "").str.contains("WB/OZON", na=False)])

with tabs[6]:
    show_table(df[df.get("Категория", "").str.contains("Grok 4.3", na=False)])

with tabs[7]:
    show_table(df[df.get("Категория", "").str.contains("Другие заказы", na=False)])

# Автообновление
time.sleep(0.5)
st.rerun()
