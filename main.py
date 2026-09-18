import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

# 제목 설정
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 전처리: '|' 기호로 연결된 여러 장르 중 첫 번째 장르만 추출
    df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0] if x != 'nan' else x)
    
    return df

df = load_data()

# 1. 장르별 영화 편수 (도넛 그래프)
st.subheader("1. 장르별 영화 편수")

# 장르별 편수 집계
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

# Plotly 도넛 그래프 생성
fig_genre = px.pie(
    genre_counts,
    values='count',
    names='genre',
    hole=0.4,
    title="장르별 영화 편수 분포"
)

# 호버 툴팁 설정 (편수 및 비율 표시)
fig_genre.update_traces(
    hovertemplate="<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}"
)

# 그래프 출력
st.plotly_chart(fig_genre, use_container_width=True)

# 구분선 및 알 수 있는 점 안내 구역
st.divider()
st.markdown("**이 그래프로 알 수 있는 것:** 특정 기간 박스오피스 상위권에 가장 많이 진입한 주요 장르의 비중과 분포를 한눈에 확인할 수 있습니다.")
