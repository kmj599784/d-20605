import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# App Title and Description
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("""
박스오피스 상위권 영화 데이터를 바탕으로 **장르별 분포**, **관객수 변수 간의 관계**, **스크린 및 흥행 지표 간의 상관관계**를 다양하게 시각화하여 살펴보는 도감입니다.
""")

st.divider()

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 처리: 세로막대 '|' 기호로 연결되어 있는 경우 첫 번째 장르만 사용
    df['genre_clean'] = df['genre'].fillna('기타').astype(str).apply(lambda x: x.split('|')[0].strip())
    
    # openDt 날짜형으로 변환 (YYYYMMDD 포맷)
    df['openDt_parsed'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')
    
    return df

try:
    df = load_data()
    
    # Sidebar Filter Options
    st.sidebar.header("🔍 데이터 필터링")
    selected_genres = st.sidebar.multiselect(
        "장르 선택",
        options=sorted(df['genre_clean'].unique()),
        default=sorted(df['genre_clean'].unique())
    )
    
    filtered_df = df[df['genre_clean'].isin(selected_genres)]
    
    st.sidebar.markdown(f"**총 데이터 수:** `{len(filtered_df)}` / {len(df)} 편")

    st.header("1. 장르별 영화 편수 분포")
    
    genre_counts = filtered_df['genre_clean'].value_counts().reset_index()
    genre_counts.columns = ['장르', '영화편수']
    
    fig_donut = px.pie(
        genre_counts,
        values='영화편수',
        names='장르',
        hole=0.4,
        title="장르별 영화 편수 비율 (도넛 차트)",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # 마우스 호버 시 편수와 비율이 명확하게 나타나도록 설정
    fig_donut.update_traces(
        hoverinfo='label+value+percent',
        textinfo='label+percent',
        hovertemplate='<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}'
    )
    fig_donut.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # 그래프 분석 자릿수 구역
    st.info("💡 **이 그래프로 알 수 있는 것:** 특정 주요 장르(예: 드라마다, 액션 등)가 전체 상위권 영화 중 대다수의 비중을 차지하는 편중 현상을 한눈에 파악할 수 있습니다.")

    st.divider()

    st.header("2. 총 관객수 및 흥행 지표 분포")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = px.histogram(
            filtered_df,
            x='total_audi',
            nbins=30,
            title="총 관객수 분포 (히스토그램)",
            labels={'total_audi': '총 관객수 (명)'},
            color_discrete_sequence=['#4C72B0']
        )
        fig_hist.update_layout(yaxis_title="영화 수")
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with col2:
        fig_box = px.box(
            filtered_df,
            x='genre_clean',
            y='total_audi',
            title="장르별 총 관객수 분포 (박스플롯)",
            labels={'genre_clean': '장르', 'total_audi': '총 관객수 (명)'},
            color='genre_clean'
        )
        fig_box.update_layout(showlegend=False, xaxis_title="장르")
        st.plotly_chart(fig_box, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 대다수 영화의 관객수는 하위 구간에 모여 있으며, 일부 대형 아웃라이어(천만 관객 영화 등)가 전체 평균을 이끄는 오른쪽 꼬리가 긴 분포 형태를 띱니다.")

    st.divider()

    st.header("3. 개봉 첫 주 관객수와 총 관객수의 관계")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='first_week_audi',
        y='total_audi',
        size='first_scrn',
        color='genre_clean',
        hover_name='movieNm',
        title="개봉 첫 주 관객수 vs 총 관객수 (점 크기: 개봉일 스크린수)",
        labels={
            'first_week_audi': '개봉 첫 주 관객수',
            'total_audi': '총 관객수',
            'first_scrn': '개봉일 스크린수',
            'genre_clean': '장르'
        },
        trendline="ols"  # 선형 회귀 추세선
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주 관객수와 최종 총 관객수 간에는 매우 강한 양의 선형 관계가 존재하며, 초반 흥행 성공이 최종 성패를 크게 좌우합니다.")

    st.divider()

    st.header("4. 톱10 유지 기간과 총 관객수의 관계")
    
    fig_days = px.scatter(
        filtered_df,
        x='days_in_top10',
        y='total_audi',
        color='first_show',
        hover_name='movieNm',
        title="10위권 머문 날수 vs 총 관객수 (색상: 개봉일 상영횟수)",
        labels={
            'days_in_top10': '10위권 머문 날수 (일)',
            'total_audi': '총 관객수',
            'first_show': '개봉일 상영횟수'
        },
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_days, use_container_width=True)

    st.info("💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권(Top 10)에 오래 머물수록 총 관객수가 비례하여 증가하며, 초기 상영 횟수가 많았던 영화들이 더 길게 상위권을 유지하는 경향을 보입니다.")

    st.divider()

    with st.expander("📄 원본 데이터 일부 보기"):
        st.dataframe(filtered_df[['movieNm', 'genre_clean', 'openDt', 'first_scrn', 'first_week_audi', 'total_audi', 'days_in_top10']])

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
