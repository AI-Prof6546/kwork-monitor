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
        df = pd.read_csv(CSV_URL, on_bad_lines='skip')
        df.columns = df.columns.str.strip()           # убираем лишние пробелы
        if "Дата" in df.columns:
            df["Дата"] = pd.to_datetime(df["Дата"], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return pd.DataFrame()

df = load_orders()

st.success(f"✅ Загружено строк из Google: {len(df)}")

# Метрики с защитой
col1, col2, col3, col4 = st.columns(4)
col1.metric("Всего заказов", len(df))

high_count = len(df[df["Приоритет"].str.contains("💎", na=False)]) if "Приоритет" in df.columns else 0
col2.metric("Высокий приоритет", high_count)

today_count = len(df[df["Дата"].dt.date == datetime.now().date()]) if "Дата" in df.columns and not df.empty else 0
col3.metric("Сегодня", today_count)

budget_nums = pd.to_numeric(df['Бюджет'].str.extract('(\d+)', expand=False), errors='coerce') if "Бюджет" in df.columns else pd.Series()
col4.metric("Средний бюджет", f"{budget_nums.mean():.0f} ₽" if not budget_nums.empty else "— ₽")

st.subheader("📋 Все заказы")

search = st.text_input("🔍 Поиск по заголовку или описанию", "")
priority_filter = st.selectbox("Приоритет", ["Все", "💎 Высокий", "📌 Обычный"])

filtered = df.copy()
if search and not filtered.empty:
    filtered = filtered[filtered["Заголовок"].str.contains(search, case=False, na=False) | 
                        filtered["Описание"].str.contains(search, case=False, na=False)]
if priority_filter != "Все" and not filtered.empty and "Приоритет" in filtered.columns:
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
        df_cat = df[df["Категория"] == cat].copy() if "Категория" in df.columns else pd.DataFrame()
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
