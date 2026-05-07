import streamlit as st
import pandas as pd
from datetime import datetime
import time

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStd09qZjRsRPMB_mN0HgEB6dDL2UPAELc59_IxnFroSvWgR984VUcvzm3zn8dyhsP7Q5hk1iq9WXDS/pub?output=csv"

st.set_page_config(page_title="Kwork Монитор", page_icon="🤖", layout="wide")

st.title("🤖 Kwork Монитор ИИ-заказов")
st.caption("⚡ Реальное время • Обновление каждые 2 секунды")

@st.cache_data(ttl=2)
def load_orders():
    try:
        df = pd.read_csv(CSV_URL, on_bad_lines='skip')
        # Приводим названия столбцов к точным
        df.columns = df.columns.str.strip()
        if "Дата" in df.columns:
            df["Дата"] = pd.to_datetime(df["Дата"], errors='coerce')
        st.success(f"✅ Загружено строк из Google: {len(df)}")
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки CSV: {e}")
        return pd.DataFrame()

df = load_orders()

if df.empty:
    st.warning("Таблица пока пустая или не загрузилась. Подожди 10–20 секунд и обнови страницу.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего заказов", len(df))
    col2.metric("Высокий приоритет", len(df[df.get("Приоритет", "").str.contains("💎", na=False)]))
    col3.metric("Сегодня", len(df[df["Дата"].dt.date == datetime.now().date()]) if "Дата" in df.columns else 0)

    st.subheader("📋 Все заказы")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.success(f"⚡ Последнее обновление: {datetime.now().strftime('%H:%M:%S')}")

time.sleep(0.5)
st.rerun()
