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

# CSS 파일 읽어오기
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
            return
