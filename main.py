import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("""
박스오피스 상위권 영화 데이터를 바탕으로 **장르별 분포**, **제작국가별 구도**, **총 관객수 비중 및 관계**, **개봉일 스크린수, 첫 주 관객수와 최종 관객수의 상관관계**를 살펴보는 종합 시각화 도감입니다.
""")

st.divider()

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # genre 열 처리: 세로막대 '|' 기호로 연결되어 있는 경우 첫 번째 장르만 사용
    df['genre_clean'] = df['genre'].fillna('기타').astype(str).apply(lambda x: x.split('|')[0].strip())
    
    # nation 열 결측치 처리
    df['nation_clean'] = df['nation'].fillna('기타').astype(str).apply(lambda x: x.strip())
    
    # openDt 날짜형 변환
    df['openDt_parsed'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')
    
    return df

try:
    df = load_data()
    
    st.sidebar.header("🔍 데이터 필터링")
    selected_genres = st.sidebar.multiselect(
        "장르 선택",
        options=sorted(df['genre_clean'].unique()),
        default=sorted(df['genre_clean'].unique())
    )
    
    filtered_df = df[df['genre_clean'].isin(selected_genres)].copy()
    
    st.sidebar.markdown(f"**총 데이터 수:** `{len(filtered_df)}` / {len(df)} 편")

    # 상단 요약 지표
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 분석 영화 수", f"{len(filtered_df):,} 편")
    with col2:
        st.metric("총 누적 관객수", f"{filtered_df['total_audi'].sum():,} 명")
    with col3:
        st.metric("평균 개봉일 스크린수", f"{int(filtered_df['first_scrn'].mean()):,} 개")
    with col4:
        st.metric("평균 Top10 유지일수", f"{filtered_df['days_in_top10'].mean():.1f} 일")

    st.divider()

    # 1. 도넛 차트
    st.header("1. 장르별 영화 편수 분포 (도넛 차트)")
    
    genre_counts = filtered_df['genre_clean'].value_counts().reset_index()
    genre_counts.columns = ['장르', '영화편수']
    
    fig_donut = px.pie(
        genre_counts,
        values='영화편수',
        names='장르',
        hole=0.4,
        title="장르별 영화 편수 비율",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_donut.update_traces(
        hoverinfo='label+value+percent',
        textinfo='label+percent',
        hovertemplate='<b>장르:</b> %{label}<br><b>영화편수:</b> %{value:,}편<br><b>비율:</b> %{percent}'
    )
    fig_donut.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    
    st.plotly_chart(fig_donut, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 특정 주요 장르(예: 드라마, 액션 등)가 전체 상위권 영화 중 대다수의 비중을 차지하는 편중 현상을 한눈에 파악할 수 있습니다.")

    st.divider()

    # 2. 트리맵
    st.header("2. 장르 및 영화별 총 관객수 분포 (트리맵)")
    
    fig_treemap = px.treemap(
        filtered_df,
        path=[px.Constant("전체 영화"), 'genre_clean', 'movieNm'],
        values='total_audi',
        color='genre_clean',
        title="장르 및 영화별 총 관객수 (칸 크기: 총 관객수)",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig_treemap.update_traces(
        hovertemplate='<b>%{label}</b><br>총 관객수: %{value:,.0f}명<br>상위 대비 비율: %{percentParent:.1%}',
        textinfo='label+value'
    )
    fig_treemap.update_layout(margin=dict(t=50, l=10, r=10, b=10))
    
    st.plotly_chart(fig_treemap, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 각 장르가 차지하는 전체 관객 비중과 해당 장르 내에서 흥행을 견인한 대표 영화들의 관객수 규모를 한눈에 직관적으로 비교할 수 있습니다.")

    st.divider()

    # 3. 박스 플롯 (Top 10 유지일수)
    st.header("3. 장르별 톱10 유지 기간 분포 (박스 플롯)")
    
    fig_box = px.box(
        filtered_df,
        x='genre_clean',
        y='days_in_top10',
        color='genre_clean',
        hover_name='movieNm',
        points="all",
        title="장르별 10위권 머문 날수 분포",
        labels={
            'genre_clean': '장르',
            'days_in_top10': '10위권 머문 날수 (일)'
        },
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_box.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>장르: %{x}<br>10위권 머문 날수: %{y}일'
    )
    fig_box.update_layout(showlegend=False, margin=dict(t=50, l=20, r=20, b=20))
    
    st.plotly_chart(fig_box, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 장르에 따라 박스오피스 상위권(Top 10)에 장기 집권하는 지속력의 차이와 개별 영화의 스펙트럼(최솟값, 중앙값, 아웃라이어)을 한눈에 비교할 수 있습니다.")

    st.divider()

    # 4. 산점도 (스크린수 vs 총 관객수)
    st.header("4. 개봉일 스크린수와 총 관객수의 관계")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='first_scrn',
        y='total_audi',
        color='genre_clean',
        hover_name='movieNm',
        title="개봉일 스크린수 vs 총 관객수 (색상: 장르)",
        labels={
            'first_scrn': '개봉일 스크린수',
            'total_audi': '총 관객수',
            'genre_clean': '장르'
        },
        hover_data={
            'first_scrn': ':,.0f',
            'total_audi': ':,.0f',
            'genre_clean': True
        }
    )
    fig_scatter.update_traces(
        marker=dict(size=9, opacity=0.8),
        hovertemplate='<b>%{hovertext}</b><br>장르: %{customdata[2]}<br>개봉일 스크린수: %{x:,.0f}개<br>총 관객수: %{y:,.0f}명'
    )
    fig_scatter.update_layout(margin=dict(t=50, l=20, r=20, b=20))
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 당일 확보한 스크린수가 많을수록 최종 총 관객수가 높아지는 경향이 있는지 확인하고, 동일한 스크린수 대비 높은 흥행을 거둔 장르 및 개별 성과 영화를 탐색할 수 있습니다.")

    st.divider()

    # 5. 주요 장르별 관객수 박스 플롯
    st.header("5. 주요 장르별 총 관객수 분포 (박스 플롯)")
    
    genre_counts_series = filtered_df['genre_clean'].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
    
    df_major_genres = filtered_df[filtered_df['genre_clean'].isin(major_genres)]
    
    if len(df_major_genres) > 0:
        fig_box_audi = px.box(
            df_major_genres,
            x='genre_clean',
            y='total_audi',
            color='genre_clean',
            hover_name='movieNm',
            points="outliers",
            title="주요 장르(10편 이상)별 총 관객수 분포 및 흥행 이상치(Outlier)",
            labels={
                'genre_clean': '장르',
                'total_audi': '총 관객수'
            },
            hover_data={
                'genre_clean': True,
                'total_audi': ':,.0f'
            },
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_box_audi.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>장르: %{x}<br>총 관객수: %{y:,.0f}명'
        )
        fig_box_audi.update_layout(showlegend=False, margin=dict(t=50, l=20, r=20, b=20))
        
        st.plotly_chart(fig_box_audi, use_container_width=True)
        st.info("💡 **이 그래프로 알 수 있는 것:** 데이터 수가 충분한 주요 장르(10편 이상) 내에서 평균적인 흥행 규모(중앙값)와 함께, 통계적 상범주를 벗어나 대풍년을 기록한 '초대형 흥행 영화(아웃라이어)'들을 한눈에 식별할 수 있습니다.")
    else:
        st.warning("선택한 필터 조건 내에 10편 이상의 영화를 가진 장르가 없습니다.")

    st.divider()

    # 6. 버블 차트
    st.header("6. 스크린수, 첫 주 관객수, 최종 관객수의 다차원 버블 관계")
    
    fig_bubble = px.scatter(
        filtered_df,
        x='first_scrn',
        y='total_audi',
        size='first_week_audi',
        color='genre_clean',
        hover_name='movieNm',
        size_max=45,
        title="개봉일 스크린수 vs 총 관객수 (버블 크기: 개봉 첫 주 관객수)",
        labels={
            'first_scrn': '개봉일 스크린수',
            'total_audi': '최종 총 관객수',
            'first_week_audi': '개봉 첫 주 관객수',
            'genre_clean': '장르'
        },
        hover_data={
            'first_scrn': ':,.0f',
            'total_audi': ':,.0f',
            'first_week_audi': ':,.0f',
            'genre_clean': True
        }
    )
    fig_bubble.update_traces(
        marker=dict(opacity=0.7, line=dict(width=1, color='DarkSlateGrey')),
        hovertemplate='<b>%{hovertext}</b><br>장르: %{customdata[3]}<br>개봉일 스크린수: %{x:,.0f}개<br>개봉 첫 주 관객수: %{customdata[2]:,.0f}명<br>최종 총 관객수: %{y:,.0f}명'
    )
    fig_bubble.update_layout(margin=dict(t=50, l=20, r=20, b=20))
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린수와 최종 관객수의 관계뿐만 아니라, 원의 크기를 통해 개봉 첫 주 초반 화력(첫 주 관객수)이 최종 흥행 규모 및 스크린 효율성에 미친 종합적인 영향을 한눈에 파악할 수 있습니다.")

    st.divider()

    # 7. 선버스트 차트
    st.header("7. 제작 국가 및 장르별 영화 편수 계층 구조 (선버스트)")
    
    sunburst_df = filtered_df.groupby(['nation_clean', 'genre_clean']).size().reset_index(name='movie_count')
    
    fig_sunburst = px.sunburst(
        sunburst_df,
        path=['nation_clean', 'genre_clean'],
        values='movie_count',
        color='nation_clean',
        title="제작 국가 → 장르 계층별 영화 편수 (칸 크기: 영화 편수)",
        color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    
    fig_sunburst.update_traces(
        hovertemplate='<b>%{label}</b><br>영화 편수: %{value:,}편<br>상위 영역 대비 비율: %{percentParent:.1%}<br>전체 대비 비율: %{percentRoot:.1%}',
        textinfo='label+value'
    )
    fig_sunburst.update_layout(margin=dict(t=50, l=10, r=10, b=10))
    
    st.plotly_chart(fig_sunburst, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 주요 영화 제작 국가(예: 한국, 미국 등)별로 어떤 장르의 영화가 주류를 이루고 있는지 국가별 장르 다양성과 편수 비중의 계층적 구조를 한눈에 확인할 수 있습니다.")

    st.divider()

    # 8. 한국 vs 해외 영화 비교 산점도
    st.header("8. 한국 영화와 해외 영화 간의 개봉일 평균 스크린수와 평균 총 관객수에는 어떤 차이가 있나요?")
    
    fig_nation_scatter = px.scatter(
        filtered_df,
        x='days_in_top10',
        y='total_audi',
        color='nation_clean',
        size='first_scrn',
        hover_name='movieNm',
        size_max=35,
        title="한국 영화와 해외 영화 간의 개봉일 평균 스크린수와 평균 총 관객수에는 어떤 차이가 있나요?",
        labels={
            'days_in_top10': '10위권에 머문 날수',
            'total_audi': '총 관객수',
            'nation_clean': '제작 국가',
            'first_scrn': '개봉일 스크린수'
        },
        hover_data={
            'days_in_top10': True,
            'total_audi': ':,.0f',
            'first_scrn': ':,.0f',
            'nation_clean': True
        }
    )
    
    fig_nation_scatter.update_traces(
        marker=dict(opacity=0.75, line=dict(width=1, color='DarkSlateGrey')),
        hovertemplate='<b>%{hovertext}</b><br>제작국가: %{customdata[3]}<br>10위권 머문 날수: %{x}일<br>개봉일 스크린수: %{customdata[2]:,.0f}개<br>총 관객수: %{y:,.0f}명'
    )
    fig_nation_scatter.update_layout(margin=dict(t=50, l=20, r=20, b=20))
    
    st.plotly_chart(fig_nation_scatter, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 한국 영화와 해외 영화 간에 개봉일 스크린수(점 크기) 확보 규모 차이, Top 10 체류 일수(X축) 및 최종 총 관객수(Y축)에 따른 유통·흥행 구조의 차이를 한눈에 파악할 수 있습니다.")

    st.divider()

    with st.expander("📄 원본 데이터 일부 보기"):
        st.dataframe(filtered_df[['movieNm', 'nation_clean', 'genre_clean', 'openDt', 'first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']])

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
