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
    .main-header { background: linear-gradient(90deg, #1a1f2e 0%, #252b3d 100%); padding: 24px 32px; border-radius: 20px; margin-bottom: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid #2a3142; }
    .metric-card { background: #1a1f2e; border-radius: 16px; padding: 20px 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.35); border: 1px solid #2a3142; }
    .stDataFrame { border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.45); border: 1px solid #2a3142; }
    .stTabs [data-baseweb="tab"] { background: #252b3d; border-radius: 12px; padding: 14px 24px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: linear-gradient(90deg, #00ff9d 0%, #00cc7a 100%); color: #0a0c14 !important; font-weight: 700; }
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
        df = pd.read_csv(CSV_URL, on_bad_lines='skip', header=None)
        
        if df.empty:
            return pd.DataFrame(columns=['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка'])
        
        # Принудительно назначаем колонки по позиции (самый надёжный способ)
        if len(df.columns) >= 8:
            df.columns = ['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка']
        else:
            while len(df.columns) < 8:
                df[len(df.columns)] = ""
            df.columns = ['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка'][:len(df.columns)]
        
        # Убираем строку заголовков, если она попала
        if str(df.iloc[0, 0]).lower() in ['дата', 'date', 'время']:
            df = df.iloc[1:].reset_index(drop=True)
        
        df['Дата'] = pd.to_datetime(df['Дата'], errors='coerce')
        df = df.dropna(subset=['Заголовок'])
        df = df[df['Заголовок'].astype(str).str.strip() != ""]
        df = df.sort_values('Дата', ascending=False).reset_index(drop=True)
        
        return df
    except Exception:
        return pd.DataFrame(columns=['Дата', 'Приоритет', 'Категория', 'Заголовок', 'Бюджет', 'Предложений', 'Описание', 'Ссылка'])

# ==================== ОСНОВНОЙ ФРАГМЕНТ (БЕЗ st.rerun — ТОЛЬКО fragment) ====================
@st.fragment(run_every=2)
def show_dashboard():
    df = load_data()
    
    # Метрики
    total = len(df)
    high_priority = len(df[df['Приоритет'].astype(str).str.contains('💎|ВЫСОКИЙ', case=False, na=False)]) if not df.empty else 0
    today_count = len(df[df['Дата'].dt.date == date.today()]) if not df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Всего заказов", total)
    col2.metric("💎 Высокий приоритет", high_priority)
    col3.metric("📅 Сегодня", today_count)
    col4.metric("📥 Загружено строк", total)
    
    st.divider()
    
    # Главная таблица
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
    
    # Вкладки
    st.subheader("📂 Заказы по направлениям")
    
    tab_names = ["🎨 Figma", "🖼️ Фото/Видео ИИ", "📸 Photoshop/Видео монтаж", "📊 Excel/PDF", "🛒 WB/OZON", "🤖 Grok 4.3", "📦 Другие заказы"]
    tabs = st.tabs(tab_names)
    
    def show_tab(tab_index, keywords):
        with tabs[tab_index]:
            if df.empty or "Категория" not in df.columns:
                st.info("📭 Нет данных")
                return
            
            if tab_index == 6:  # Другие
                mask = ~df['Категория'].astype(str).str.contains("Figma|Фото|Видео|Photoshop|Excel|WB|OZON|Grok", case=False, na=False)
            else:
                mask = df['Категория'].astype(str).str.contains(keywords, case=False, na=False, regex=True)
            
            filtered = df[mask]
            
            if filtered.empty:
                st.info("📭 Пока нет заказов в этой категории")
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
    
    show_tab(0, "Figma")
    show_tab(1, "Фото|Видео")
    show_tab(2, "Photoshop|Видео монтаж")
    show_tab(3, "Excel|PDF")
    show_tab(4, "WB|OZON")
    show_tab(5, "Grok")           # ловит Grok 4.3 и все вариации
    show_tab(6, "")

# ==================== ЗАПУСК ====================
show_dashboard()
