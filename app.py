import streamlit as st
import pandas as pd
from datetime import datetime
import time

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStd09qZjRsRPMB_mN0HgEB6dDL2UPAELc59_IxnFroSvWgR984VUcvzm3zn8dyhsP7Q5hk1iq9WXDS/pub?output=csv"

st.set_page_config(page_title="Kwork Монитор", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .main {background-color: #0a0a0a;}
    h1 {color: #ffd700 !important;}
    .stTabs [data-baseweb="tab"] {color: #ffffff; font-weight: 600;}
    .stTabs [data-baseweb="tab-highlight"] {background-color: #ffd700 !important;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Kwork Монитор ИИ-заказов")
st.caption("⚡ Реальное время • Обновление каждые 2 секунды")

@st.cache_data(ttl=2)
def load_orders():
    try:
        df = pd.read_csv(CSV_URL)
        df["Дата"] = pd.to_datetime(df["Дата"], errors='coerce')
        return df.sort_values("Дата", ascending=False)
    except:
        return pd.DataFrame(columns=["Дата", "Приоритет", "Категория", "Заголовок", "Бюджет", "Предложений", "Описание", "Ссылка"])

df = load_orders()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Всего заказов", len(df))
col2.metric("Высокий приоритет", len(df[df["Приоритет"].str.contains("💎", na=False)]))
col3.metric("Сегодня", len(df[df["Дата"].dt.date == datetime.now().date()]) if not df.empty else 0)

budget_nums = pd.to_numeric(df['Бюджет'].str.extract('(\d+)', expand=False), errors='coerce')
col4.metric("Средний бюджет", f"{budget_nums.mean():.0f} ₽" if not budget_nums.empty else "— ₽")

st.subheader("📋 Все заказы")

search = st.text_input("🔍 Поиск", "")
priority_filter = st.selectbox("Приоритет", ["Все", "💎 Высокий", "📌 Обычный"])

filtered = df.copy()
if search:
    filtered = filtered[filtered["Заголовок"].str.contains(search, case=False, na=False) | 
                        filtered["Описание"].str.contains(search, case=False, na=False)]
if priority_filter != "Все":
    filtered = filtered[filtered["Приоритет"].str.contains(priority_filter[0], na=False)]

st.dataframe(
    filtered.style.apply(lambda row: ['background-color: #1a3c2e' if '💎' in str(row.get("Приоритет","")) else 'background-color: #1a2a3c'] * len(row), axis=1),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Дата": st.column_config.DatetimeColumn(format="DD.MM HH:mm", width=110),
        "Приоритет": st.column_config.TextColumn(width=140),
        "Категория": st.column_config.TextColumn(width=160),
        "Заголовок": st.column_config.TextColumn(width=320),
        "Бюджет": st.column_config.TextColumn(width=110),
        "Предложений": st.column_config.NumberColumn(width=100),
        "Описание": st.column_config.TextColumn(width=500),
        "Ссылка": st.column_config.LinkColumn("Открыть", display_text="🔗 Открыть", width=110),
    }
)

st.success(f"⚡ Обновлено: {datetime.now().strftime('%H:%M:%S')}")

# Вкладки
st.subheader("📂 Заказы по направлениям")
tabs = st.tabs(["Figma", "Фото/Видео ИИ", "Photoshop/Видео монтаж", "Excel/PDF", "WB/OZON", "Grok 4.3", "Другие заказы"])

for tab, cat in zip(tabs, ["Figma", "Фото/Видео ИИ", "Photoshop/Видео монтаж", "Excel/PDF", "WB/OZON", "Grok 4.3", "Другие заказы"]):
    with tab:
        df_cat = df[df["Категория"] == cat].copy()
        if df_cat.empty:
            st.info(f"Пока нет заказов в категории «{cat}»")
        else:
            st.dataframe(
                df_cat.style.apply(lambda row: ['background-color: #1a3c2e' if '💎' in str(row.get("Приоритет","")) else 'background-color: #1a2a3c'] * len(row), axis=1),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Дата": st.column_config.DatetimeColumn(format="DD.MM HH:mm", width=110),
                    "Приоритет": st.column_config.TextColumn(width=140),
                    "Заголовок": st.column_config.TextColumn(width=320),
                    "Бюджет": st.column_config.TextColumn(width=110),
                    "Предложений": st.column_config.NumberColumn(width=100),
                    "Описание": st.column_config.TextColumn(width=500),
                    "Ссылка": st.column_config.LinkColumn("Открыть", display_text="🔗 Открыть", width=110),
                }
            )

time.sleep(0.5)
st.rerun()
