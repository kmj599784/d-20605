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

# ---------------------------------------------------------
# 1. 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------
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

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 장르 및 영화별 총 관객수 (트리맵)
# ---------------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객수 분포")

# Plotly 트리맵 생성 (계층 구조: genre -> movieNm, 칸 크기: total_audi)
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), 'genre', 'movieNm'],
    values='total_audi',
    title="장르별·영화별 총 관객수 (트리맵)",
    hover_data={'total_audi': ':,d'}
)

# 호버 툴팁 설정 (영화명과 총 관객수 표시)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig_treemap, use_container_width=True)

# 구분선 및 알 수 있는 점 안내 구역
st.divider()
st.markdown("**이 그래프로 알 수 있는 것:** 장르별 전체 관객수 규모와 함께 각 장르 내에서 어떤 영화가 흥행을 주도했는지 상대적 크기로 한눈에 비교할 수 있습니다.")

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 총 관객수 분포 (히스토그램)
# ---------------------------------------------------------
st.subheader("3. 총 관객수 분포")

# Plotly 히스토그램 생성
fig_hist = px.histogram(
    df,
    x='total_audi',
    nbins=20,
    title="총 관객수 히스토그램",
    labels={'total_audi': '총 관객수', 'count': '영화 수'}
)

fig_hist.update_traces(
    hovertemplate="<b>관객수 구간:</b> %{x}<br><b>영화 수:</b> %{y}편<extra></extra>"
)

# 그래프 출력
st.plotly_chart(fig_hist, use_container_width=True)

# 최다 관객 영화 정보 데이터 동적 추출
top_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie['movieNm']
top_movie_audi = top_movie['total_audi']

# 구분선 및 알 수 있는 점 안내 구역
st.divider()
st.markdown(
    f"**이 그래프로 알 수 있는 것:** 대부분의 영화가 **하위 관객수 구간(200만 명 미만)**에 모여 있는 오른쪽으로 긴 꼬리를 찌그러진 분포를 보입니다. "
    f"반면 가장 관객 수가 많은 영화는 **'{top_movie_name}'**(총 {top_movie_audi:,}명)으로 흥행 대작과 일반 영화 간의 양극화 현상을 확인할 수 있습니다."
)
