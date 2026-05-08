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

# ===================== ЗАЩИЩЁННЫЕ МЕТРИКИ =====================
def safe_count_contains(col_name, pattern):
    if df.empty or col_name not in df.columns:
        return 0
    col = df[col_name].astype(str)
    return len(col[col.str.contains(pattern, na=False)])

total = len(df)
high_priority = safe_count_contains("Приоритет", "💎")
today = len(df[df.get("Дата", pd.Series()).astype(str).str.contains(str(datetime.now().date()), na=False)]) if not df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Всего заказов", total)
col2.metric("Высокий приоритет", high_priority)
col3.metric("Сегодня", today)
col4.metric("Загружено строк из Google", len(df))

st.divider()

# ===================== ВКЛАДКИ =====================
tab_all, tab_figma, tab_ai, tab_photo, tab_excel, tab_wb, tab_grok, tab_other = st.tabs([
    "📋 Все заказы", "🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop/Видео монтаж",
    "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие заказы"
])

def show_table(filtered_df):
    if filtered_df.empty:
        st.info("Пока нет заказов в этой категории")
        return
    
    column_config = {
        "Ссылка": st.column_config.LinkColumn("Открыть заказ", display_text="🔗 Открыть", width=130),
        "Заголовок": st.column_config.TextColumn("Заголовок", width=400),
        "Описание": st.column_config.TextColumn("Описание", width=500),
    }
    
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config=column_config,
        hide_index=True
    )

with tab_all:
    show_table(df)

with tab_figma:
    show_table(df[df.get("Категория", "").str.contains("Figma", na=False)])

with tab_ai:
    show_table(df[df.get("Категория", "").str.contains("Фото/Видео ИИ", na=False)])

with tab_photo:
    show_table(df[df.get("Категория", "").str.contains("Photoshop|Видео монтаж", na=False, regex=True)])

with tab_excel:
    show_table(df[df.get("Категория", "").str.contains("Excel/PDF", na=False)])

with tab_wb:
    show_table(df[df.get("Категория", "").str.contains("WB/OZON", na=False)])

with tab_grok:
    show_table(df[df.get("Категория", "").str.contains("Grok 4.3", na=False)])

with tab_other:
    show_table(df[df.get("Категория", "").str.contains("Другие заказы", na=False)])

# Автообновление
time.sleep(0.5)
st.rerun()
