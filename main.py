import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# App Title and Description
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("""
박스오피스 상위권 영화 데이터를 바탕으로 **장르별 분포**, **총 관객수 비중 및 관계**, **흥행 지표 간의 상관관계**를 다양한 시각화 차트로 살펴보는 도감입니다.
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
    
    fig_donut.update_traces(
        hoverinfo='label+value+percent',
        textinfo='label+percent',
        hovertemplate='<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}'
    )
    fig_donut.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    
    st.plotly_chart(fig_donut, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 특정 주요 장르(예: 드라마, 액션 등)가 전체 상위권 영화 중 대다수의 비중을 차지하는 편중 현상을 한눈에 파악할 수 있습니다.")

    st.divider()

    st.header("2. 장르 및 영화별 총 관객수 분포 (트리맵)")
    
    # 계층구조(장르 -> 영화명) 트리맵 작성
    fig_treemap = px.treemap(
        filtered_df,
        path=[px.Constant("전체 영화"), 'genre_clean', 'movieNm'],
        values='total_audi',
        color='genre_clean',
        title="장르 및 영화별 총 관객수 (칸 크기: 총 관객수)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # 호버 툴팁 설정: 영화명 및 총 관객수 명시
    fig_treemap.update_traces(
        hovertemplate='<b>%{label}</b><br>총 관객수: %{value:,.0f}명<br>비율: %{percentParent:.1%}',
        textinfo='label+value'
    )
    fig_treemap.update_layout(margin=dict(t=50, l=10, r=10, b=10))
    
    st.plotly_chart(fig_treemap, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 각 장르가 차지하는 전체 관객 비중과 해당 장르 내에서 흥행을 견인한 대표 영화들의 관객수 규모를 한눈에 직관적으로 비교할 수 있습니다.")

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
        trendline="ols"
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
