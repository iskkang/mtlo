import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# News function
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

# Freight Cost function
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

# Port Comparison function
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
            if 'name' in df.columns and 'value' in df.columns:
                fig = px.bar(df, x='name', y='value', title="Top Port Comparison (June 24 vs June 23)", labels={'value': 'Thousand TEU', 'name': 'Port'})
                return fig
            else:
                logging.error("Expected columns 'name' and 'value' not found in the data")
                return None
        else:
            logging.error("Port comparison API response does not contain 'plots' key or it is empty")
            return None
    else:
        logging.error(f"Failed to retrieve data from {url}: {response.status_code}, {response.text}")
        return None

# SCFI function
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

# Global Trade function
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

# Streamlit app
st.set_page_config(layout="wide")

# Define tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["News", "Freight Cost", "Port Comparison", "SCFI", "Global Trade"])

# News Tab
with tab1:
    st.header("News")
    keyword = st.text_input("Enter keyword for news search:")
    if st.button("Fetch News"):
        news = fetch_news(keyword)
        for article in news:
            st.subheader(article['title'])
            st.write(article['source'])
            if article['thumbnail']:
                st.image(article['thumbnail'])
            st.write(article['date'])
            st.markdown(f"[Read more]({article['link']})")

# Freight Cost Tab
with tab2:
    st.header("Freight Cost")
    origin = st.text_input("Enter origin:")
    destination = st.text_input("Enter destination:")
    if st.button("Search Freight Cost"):
        url = "https://www.econdb.com/maritime/freight_rates/"
        df = fetch_data(url)
        result = search_rate(df, origin, destination)
        if isinstance(result, pd.DataFrame):
            st.write(result)
        else:
            st.write(result)

# Port Comparison Tab
with tab3:
    st.header("Port Comparison")
    if st.button("Fetch Port Comparison Data"):
        fig = fetch_and_plot_ports()
        if fig:
            st.plotly_chart(fig)
        else:
            st.write("Failed to retrieve port comparison data.")

# SCFI Tab
with tab4:
    st.header("Shanghai Containerized Freight Index (SCFI)")
    if st.button("Fetch SCFI Data"):
        fig = fetch_and_plot_scfi()
        if fig:
            st.plotly_chart(fig)
        else:
            st.write("Failed to retrieve SCFI data.")

# Global Trade Tab
with tab5:
    st.header("Global Trade")
    if st.button("Fetch Global Trade Data"):
        fig = fetch_and_plot_global_trade()
        if fig:
            st.plotly_chart(fig)
        else:
            st.write("Failed to retrieve global trade data.")
