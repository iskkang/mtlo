import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

# 페이지 설정
st.set_page_config(layout="wide")

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# CSS 스타일링 추가
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    /* DASHBOARD PADDING */
    div.block-container.css-z5fcl4.egzxvld4 {
        width: 100%;
        min-width: auto;
        max-width: initial;
        padding-left: 5rem;
        padding-right: 5rem;
        padding-top: 15px;
        padding-bottom: 40px;
    }

    /* GLOBAL FONT CHANGE */
    html, body, [class*="css"] {
        font-family: 'Space Grotesk'; 
    }

    .st-ae {
        font-family: 'Space Grotesk';
    }

    /* CONTAINER CSS */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border: 1px groove #52546a;
        border-radius: 10px;
        padding-left: 25px;
        padding-top: 10px;
        padding-bottom: 10px;
        box-shadow: -6px 8px 20px 1px #00000052;
    }

    /* CUSTOM MARKDOWN CLASSES */
    .dashboard_title {
        font-size: 35px; 
        font-family: 'Space Grotesk';
        font-weight: 700;
        line-height: 1.2;
        text-align: left;
        padding-bottom: 35px;
    }

    .price_details {
        font-size: 30px; 
        font-family: 'Space Grotesk';
        color: #f6f6f6;
        font-weight: 900;
        text-align: left;
        line-height: 1;
        padding-bottom: 10px;
    }

    .btc_text {
        font-size: 14px; 
        font-family: 'Space Grotesk';
        color: #f7931a;
        font-weight: bold;
        text-align: left;
        line-height: 0.2;
        padding-top: 10px;
    }

    .eth_text {
        font-size: 14px; 
        font-family: 'Space Grotesk';
        color: #a1a1a1;
        font-weight: bold;
        text-align: left;
        line-height: 0.2;
        padding-top: 10px;
    }

    .xmr_text {
        font-size: 14px; 
        font-family: 'Space Grotesk';
        color: #ff6b08;
        font-weight: bold;
        text-align: left;
        line-height: 0.2;
        padding-top: 10px;
    }

    .sol_text {
        font-size: 14px; 
        font-family: 'Space Grotesk';
        color: #807af4;
        font-weight: bold;
        text-align: left;
        line-height: 0.2;
        padding-top: 10px;
    }

    .xrp_text {
        font-size: 14px; 
        font-family: 'Space Grotesk';
        color: #01acf1;
        font-weight: bold;
        text-align: left;
        line-height: 0.2;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 뉴스 기능
def fetch_news(keyword):
    url = f"https://news.google.com/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')

    news = []
    for article in articles:
        source = article.find('div', class_='vr1PYe').text if article.find('div', class_='vr1PYe') else 'No Source'
        title_tag = article.find('a', class_='JtKRv')
        title = title_tag.text if title_tag else 'No Title'
        link = 'https://news.google.com' + title_tag['href'][1:] if title_tag else 'No Link'
        thumbnail_tag = article.find('img', class_='Quavad')
        if thumbnail_tag:
            thumbnail = thumbnail_tag['src']
            if thumbnail.startswith('/'):
                thumbnail = 'https://news.google.com' + thumbnail
        else:
            thumbnail = None
        date_tag = article.find('time', class_='hvbAAd')
        date = date_tag['datetime'] if date_tag else None
        news.append({
            'source': source,
            'title': title,
            'link': link,
            'thumbnail': thumbnail,
            'date': date
        })

    return news

# 데이터 불러오기 및 전처리 함수들
def fetch_and_plot_ports():
    url = "https://www.econdb.com/widgets/top-port-comparison/data/"
    response = requests.get(url)
    logging.debug(f"Port comparison API response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'plots' in data and len(data['plots']) > 0:
            series_data = data['plots'][0]['data']
            df = pd.DataFrame(series_data)
            logging.debug(f"Port comparison data: {df.head()}")
            st.write("Port comparison data:")
            st.write(df.head())
            if 'name' in df.columns and 'value' in df.columns:
                fig = px.bar(df, x='name', y='value', title="Top Port Comparison (June 24 vs June 23)", labels={'value': 'Thousand TEU', 'name': 'Port'})
                return fig
            else:
                logging.error("Expected columns 'name' and 'value' not found in the data")
                st.write("Expected columns 'name' and 'value' not found in the data")
                return None
        else:
            logging.error("Port comparison API response does not contain 'plots' key or it is empty")
            st.write("Port comparison API response does not contain 'plots' key or it is empty")
            return None
    else:
        logging.error(f"Failed to retrieve data from {url}: {response.status_code}, {response.text}")
        st.write(f"Failed to retrieve data from {url}: {response.status_code}, {response.text}")
        return None

def fetch_and_plot_scfi():
    url = "https://www.econdb.com/widgets/shanghai-containerized-index/data/"
    response = requests.get(url)
    logging.debug(f"SCFI API response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'plots' in data and len(data['plots']) > 0:
            series_data = data['plots'][0]['data']
            df = pd.DataFrame(series_data)
            df['Date'] = pd.to_datetime(df['Date'])
            fig = go.Figure()
            for column in df.columns:
                if column != 'Date':
                    fig.add_trace(go.Scatter(x=df['Date'], y=df[column], mode='lines+markers', name=column))
            fig.update_layout(title="Shanghai Containerized Freight Index (SCFI)", xaxis_title='Date', yaxis_title='SCFI Value')
            return fig
        else:
            logging.error("SCFI API response does not contain 'plots' key or it is empty")
            return None
    else:
        logging.error(f"Failed to retrieve data from {url}: {response.status_code}, {response.text}")
        return None

def fetch_and_plot_global_trade():
    url = "https://www.econdb.com/widgets/global-trade/data/?type=export&net=0&transform=0"
    response = requests.get(url)
    logging.debug(f"Global trade API response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'plots' in data and len(data['plots']) > 0:
            series_data = data['plots'][0]['data']
            df = pd.DataFrame(series_data)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            fig = px.bar(df, x=df.index, y=df.columns, title="Global exports (TEU by week)", labels={'x': 'Year', 'value': 'TEU'}, barmode='stack')
            fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=52))
            return fig
        else:
            logging.error("Global trade API response does not contain 'plots' key or it is empty")
            return None
    else:
        logging.error(f"Failed to retrieve data from {url}: {response.status_code}, {response.text}")
        return None

# Streamlit 앱 구성
st.title("MTL Dashboard")

# 첫 번째 행: 3개의 그래프 (SCFI, 포트 비교, 글로벌 무역)
st.header("Timeline Graphs")
col1, col2, col3 = st.columns(3)

with col1:
    fig_scfi = fetch_and_plot_scfi()
    if fig_scfi:
        st.plotly_chart(fig_scfi, use_container_width=True)
    else:
        st.write("SCFI 데이터를 가져오는 데 실패했습니다.")

with col2:
    fig_ports = fetch_and_plot_ports()
    if fig_ports:
        st.plotly_chart(fig_ports, use_container_width=True)
    else:
        st.write("포트 비교 데이터를 가져오는 데 실패했습니다.")

with col3:
    fig_global_trade = fetch_and_plot_global_trade()
    if fig_global_trade:
        st.plotly_chart(fig_global_trade, use_container_width=True)
    else:
        st.write("글로벌 무역 데이터를 가져오는 데 실패했습니다.")

# 두 번째 행: 뉴스 기사와 포트 현황
st.header("Latest News and Port Status")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("뉴스")
    categories = ["해상운임", "항공운임", "철도", "물류", "Shipping"]
    for category in categories:
        if st.button(category):
            keyword = category
            news = fetch_news(keyword)
            st.write(f"키워드 '{keyword}'에 대한 뉴스 기사")
            for article in news[:3]:  # 상위 3개 기사만 표시
                st.markdown(f"""
                <div class="card">
                    <img src="{article['thumbnail'] if article['thumbnail'] else 'https://via.placeholder.com/300x150?text=No+Image'}" alt="{article['title']}" style="width:100%">
                    <h4><b>{article['title']}</b></h4>
                    <p>출처: {article['source']}</p>
                    <p>날짜: {article['date']}</p>
                    <a href="{article['link']}" target="_blank">기사 읽기</a>
                </div>
                """, unsafe_allow_html=True)

with col2:
    st.subheader("포트 현황")
    fig_ports_status = fetch_and_plot_ports()
    if fig_ports_status:
        st.plotly_chart(fig_ports_status, use_container_width=True)
    else:
        st.write("포트 현황 데이터를 가져오는 데 실패했습니다.")
