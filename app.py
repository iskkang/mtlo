import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

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

# 운임 비용 기능
def fetch_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        raise ValueError("Expected a list of data")
    return df

def search_rate(df, origin, destination):
    origin = origin.lower()
    destination = destination.lower()
    df['name_o'] = df['name_o'].str.lower()
    df['name_d'] = df['name_d'].str.lower()
    filtered_df = df[df['name_o'].str.contains(origin) & df['name_d'].str.contains(destination)]
    if not filtered_df.empty:
        return filtered_df[['name_o', 'name_d', 'dv20rate']]
    else:
        return "No data found for the given origin and destination."

# 포트 비교 기능
def fetch_and_plot_ports():
    url = "https://www.econdb.com/widgets/top-port-comparison/data/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'plots' in data and len(data['plots']) > 0:
            series_data = data['plots'][0]['data']
            df = pd.DataFrame(series_data)
            fig = px.bar(df, x='name', y='value', title="Top Port Comparison (June 24 vs June 23)", labels={'value': 'Thousand TEU', 'name': 'Port'})
            return fig
        else:
            return None
    else:
        return None

# SCFI 기능
def fetch_and_plot_scfi():
    url = "https://www.econdb.com/widgets/shanghai-containerized-index/data/"
    response = requests.get(url)
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
            return None
    else:
        return None

# 글로벌 무역 기능
def fetch_and_plot_global_trade():
    url = "https://www.econdb.com/widgets/global-trade/data/?type=export&net=0&transform=0"
    response = requests.get(url)
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
            return None
    else:
        return None

# Streamlit 앱 구성
st.title("엠티엘 뉴스")

# 뉴스 섹션
st.header("뉴스")
keyword = st.text_input("뉴스 검색 키워드 입력", "해상운임")
if st.button("뉴스 검색"):
    news = fetch_news(keyword)
    st.write(f"키워드 '{keyword}'에 대한 뉴스 기사")
    for article in news[:3]:  # 상위 3개 기사만 표시
        st.image(article['thumbnail'] if article['thumbnail'] else 'https://via.placeholder.com/300x150?text=No+Image')
        st.subheader(article['title'])
        st.write(f"출처: {article['source']}")
        st.write(f"날짜: {article['date']}")
        st.markdown(f"[기사 읽기]({article['link']})")

# 운임 비용 섹션
st.header("운임 비용")
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("출발지 입력")
with col2:
    destination = st.text_input("목적지 입력")
if st.button("운임 비용 검색"):
    url = "https://www.econdb.com/maritime/freight_rates/"
    df = fetch_data(url)
    result = search_rate(df, origin, destination)
    if isinstance(result, pd.DataFrame):
        st.write(result)
    else:
        st.write(result)

# 그래프 섹션
st.header("그래프")

# 포트 비교 그래프
st.subheader("포트 비교")
if st.button("포트 비교 데이터 가져오기"):
    fig = fetch_and_plot_ports()
    if fig:
        st.plotly_chart(fig)
    else:
        st.write("포트 비교 데이터를 가져오는 데 실패했습니다.")

# SCFI 그래프
st.subheader("SCFI")
if st.button("SCFI 데이터 가져오기"):
    fig = fetch_and_plot_scfi()
    if fig:
        st.plotly_chart(fig)
    else:
        st.write("SCFI 데이터를 가져오는 데 실패했습니다.")

# 글로벌 무역 그래프
st.subheader("글로벌 무역")
if st.button("글로벌 무역 데이터 가져오기"):
    fig = fetch_and_plot_global_trade()
    if fig:
        st.plotly_chart(fig)
    else:
        st.write("글로벌 무역 데이터를 가져오는 데 실패했습니다.")
