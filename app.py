import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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

# 데이터를 불러와서 처리하는 함수들
def fetch_freight_data():
    url = "https://www.econdb.com/maritime/freight_rates/"
    response = requests.get(url)
    try:
        data = response.json()
        return pd.DataFrame(data)
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        logging.error(f"Response content: {response.content}")
        st.error("Error fetching freight data. Please check the logs for details.")
        return pd.DataFrame()

def fetch_port_comparison():
    url = "https://www.econdb.com/widgets/top-port-comparison/data/"
    response = requests.get(url)
    try:
        data = response.json()
        return pd.DataFrame(data['plots'][0]['data'])
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        logging.error(f"Response content: {response.content}")
        st.error("Error fetching port comparison data. Please check the logs for details.")
        return pd.DataFrame()

def fetch_scfi_data():
    url = "https://www.econdb.com/widgets/shanghai-containerized-index/data/"
    response = requests.get(url)
    try:
        data = response.json()
        return pd.DataFrame(data['plots'][0]['data'])
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        logging.error(f"Response content: {response.content}")
        st.error("Error fetching SCFI data. Please check the logs for details.")
        return pd.DataFrame()

def fetch_global_trade_data():
    url = "https://www.econdb.com/widgets/global-trade/data/?type=export&net=0&transform=0"
    response = requests.get(url)
    try:
        data = response.json()
        return pd.DataFrame(data['plots'][0]['data'])
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        logging.error(f"Response content: {response.content}")
        st.error("Error fetching global trade data. Please check the logs for details.")
        return pd.DataFrame()

# 데이터 불러오기
freight_data = fetch_freight_data()
port_comparison_data = fetch_port_comparison()
scfi_data = fetch_scfi_data()
global_trade_data = fetch_global_trade_data()

# Streamlit 레이아웃 구성
st.title("Basic Dashboard using Streamlit and Plotly")

# 첫 번째 행: 지표 카드
st.header("KPIs")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Accounts Receivable", value="$6,621,280")
    st.metric(label="Current Ratio", value="1.86%", delta="1.5%")

with kpi2:
    st.metric(label="Total Accounts Payable", value="$1,630,270")
    st.metric(label="DSI", value="10 Days", delta="2 Days")

with kpi3:
    st.metric(label="Equity Ratio", value="75.38%")
    st.metric(label="DSO", value="7 Days", delta="3 Days")

with kpi4:
    st.metric(label="Debt Equity", value="1.10%")
    st.metric(label="DPO", value="28 Days", delta="5 Days")

# 두 번째 행: 그래프
st.header("Graphs")
graph1, graph2 = st.columns(2)

# Net Working Capital vs Gross Working Capital 그래프
if not freight_data.empty:
    fig1 = px.line(freight_data, x="date", y="value", title="Net Working Capital vs Gross Working Capital")
    graph1.plotly_chart(fig1, use_container_width=True)

# Port Comparison 그래프
if not port_comparison_data.empty:
    fig2 = px.bar(port_comparison_data, x='name', y='value', title="Top Port Comparison (June 24 vs June 23)")
    graph2.plotly_chart(fig2, use_container_width=True)

# 세 번째 행: SCFI 그래프
if not scfi_data.empty:
    fig3 = go.Figure()
    for column in scfi_data.columns:
        if column != 'Date':
            fig3.add_trace(go.Scatter(x=scfi_data['Date'], y=scfi_data[column], mode='lines+markers', name=column))
    fig3.update_layout(title="Shanghai Containerized Freight Index (SCFI)", xaxis_title='Date', yaxis_title='SCFI Value')
    st.plotly_chart(fig3, use_container_width=True)

# 네 번째 행: 글로벌 무역 그래프
if not global_trade_data.empty:
    fig4 = px.bar(global_trade_data, x=global_trade_data.index, y=global_trade_data.columns, title="Global exports (TEU by week)", barmode='stack')
    st.plotly_chart(fig4, use_container_width=True)

# 뉴스 섹션
st.header("뉴스")
keyword = "해상운임"
news = fetch_news(keyword)
st.write(f"키워드 '{keyword}'에 대한 뉴스 기사")
for article in news[:3]:  # 상위 3개 기사만 표시
    st.image(article['thumbnail'] if article['thumbnail'] else 'https://via.placeholder.com/300x150?text=No+Image')
    st.subheader(article['title'])
    st.write(f"출처: {article['source']}")
    st.write(f"날짜: {article['date']}")
    st.markdown(f"[기사 읽기]({article['link']})")
