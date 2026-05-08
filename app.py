import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Kwork Монитор ИИ-заказов", layout="wide")

st.title("🤖 Kwork Монитор ИИ-заказов")
st.caption("🔥 Реальное время • Обновление каждые 2 секунды")

# ===================== ДАННЫЕ =====================
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

# ===================== МЕТРИКИ =====================
col1, col2, col3, col4 = st.columns(4)

total = len(df)
high = len(df[df.get("Приоритет", "").astype(str).str.contains("💎", na=False)])
today = len(df[df.get("Дата", "").astype(str).str.contains(str(datetime.now().date()), na=False)])

col1.metric("Всего заказов", total)
col2.metric("Высокий приоритет", high)
col3.metric("Сегодня", today)
col4.metric("Загружено строк из Google", len(df))

st.divider()

# ===================== ОБЩАЯ ТАБЛИЦА =====================
st.subheader("📋 Все заказы")
if df.empty:
    st.info("Пока нет заказов")
else:
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Ссылка": st.column_config.LinkColumn("Открыть", display_text="🔗 Открыть", width=120),
            "Заголовок": st.column_config.TextColumn(width=400),
            "Описание": st.column_config.TextColumn(width=500),
        },
        hide_index=True
    )

st.divider()

# ===================== ВКЛАДКИ =====================
st.subheader("Фильтры по направлениям")
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop/Видео монтаж",
    "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие заказы"
])

def show_filtered_tab(df, category_name):
    if df.empty:
        st.info("Нет заказов")
        return
    filtered = df[df.get("Категория", "").astype(str).str.contains(category_name, na=False)]
    if filtered.empty:
        st.info(f"Пока нет заказов в категории «{category_name}»")
    else:
        st.dataframe(
            filtered,
            use_container_width=True,
            column_config={
                "Ссылка": st.column_config.LinkColumn("Открыть", display_text="🔗 Открыть", width=120),
                "Заголовок": st.column_config.TextColumn(width=400),
                "Описание": st.column_config.TextColumn(width=500),
            },
            hide_index=True
        )

with tab1: show_filtered_tab(df, "Figma")
with tab2: show_filtered_tab(df, "Фото/Видео ИИ")
with tab3: show_filtered_tab(df, "Photoshop|Видео монтаж")
with tab4: show_filtered_tab(df, "Excel/PDF")
with tab5: show_filtered_tab(df, "WB/OZON")
with tab6: show_filtered_tab(df, "Grok 4.3")
with tab7: show_filtered_tab(df, "Другие заказы")

# Автообновление
time.sleep(0.5)
st.rerun()
