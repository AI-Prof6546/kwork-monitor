import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Kwork Монитор ИИ-заказов", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0c14 0%, #0e1117 100%); }
    .main-header { background: linear-gradient(90deg, #1a1f2e 0%, #252b3d 100%); padding: 24px 32px; border-radius: 20px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid #2a3142; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:42px; font-weight:800; color:white;">🤖 Kwork Монитор ИИ-заказов</h1>
    <p style="margin:8px 0 0 0; font-size:18px; color:#00ff9d; font-weight:600;">
        🔥 Реальное время • Обновление каждые 2 секунды
    </p>
</div>
""", unsafe_allow_html=True)

SPREADSHEET_ID = "1V5wkNF8lYvz7FbRDEotmrmHB1zYrV2jAjU3WIcdD2bQ"

@st.cache_resource
def get_gspread_client():
    creds_dict = dict(st.secrets["google_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def load_data():
    try:
        client = get_gspread_client()
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        data = sheet.get_all_values()

        if len(data) < 2:
            return pd.DataFrame()

        # Берём первую строку как заголовки
        headers = [str(h).strip() for h in data[0]]
        df = pd.DataFrame(data[1:], columns=headers)

        # Приводим названия колонок к нужному виду (если они отличаются)
        col_map = {
            'Дата': 'Дата',
            'Приоритет': 'Приоритет',
            'Категория': 'Категория',
            'Заголовок': 'Заголовок',
            'Бюджет': 'Бюджет',
            'Предложений': 'Предложений',
            'Описание': 'Описание',
            'Ссылка': 'Ссылка'
        }
        
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        # Оставляем только нужные колонки
        needed = ['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка']
        for col in needed:
            if col not in df.columns:
                df[col] = ""

        df = df[needed]
        df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
        df = df.dropna(subset=['Заголовок'])
        df = df[df['Заголовок'].astype(str).str.strip() != ""]
        df = df.sort_values('Дата', ascending=False).reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return pd.DataFrame()

@st.fragment(run_every=2)
def show_dashboard():
    df = load_data()
    
    if 'last_df' not in st.session_state or len(df) > len(st.session_state.get('last_df', [])):
        st.session_state.last_df = df
    df = st.session_state.last_df

    total = len(df)
    high = len(df[df['Приоритет'].astype(str).str.contains('ВЫСОКИЙ|💎', case=False, na=False)]) if not df.empty else 0
    today = len(df[df['Дата'].dt.date == datetime.now().date()]) if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Всего заказов", total)
    col2.metric("💎 Высокий приоритет", high)
    col3.metric("📅 Сегодня", today)
    col4.metric("📥 Загружено строк", total)

    st.caption(f"Последнее обновление: {datetime.now().strftime('%H:%M:%S')}")
    st.divider()

    st.subheader("📋 Все заказы (новые сверху)")
    if df.empty:
        st.info("📭 Данных пока нет. Проверь таблицу в Google Sheets.")
    else:
        st.dataframe(df, use_container_width=True, height=520, hide_index=True,
                     column_config={"Ссылка": st.column_config.LinkColumn("Действие", display_text="🔗 Открыть заказ")})

    st.divider()
    st.subheader("📂 Заказы по направлениям")
    tabs = st.tabs(["🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop", "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие"])

    def show_tab(i, kw):
        with tabs[i]:
            if df.empty:
                st.info("Нет данных")
                return
            if i == 6:
                mask = ~df['Категория'].astype(str).str.contains("Figma|Фото|Видео|Photoshop|Excel|WB|OZON|Grok", case=False, na=False)
            else:
                mask = df['Категория'].astype(str).str.contains(kw, case=False, na=False, regex=True)
            filtered = df[mask]
            if filtered.empty:
                st.info("Пока нет заказов")
            else:
                st.dataframe(filtered, use_container_width=True, height=320, hide_index=True)

    show_tab(0, "Figma")
    show_tab(1, "Фото|Видео")
    show_tab(2, "Photoshop")
    show_tab(3, "Excel|PDF")
    show_tab(4, "WB|OZON")
    show_tab(5, "Grok")
    show_tab(6, "")

show_dashboard()
