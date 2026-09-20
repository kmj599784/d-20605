import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set Page Config
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics and insight boxes
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .insight-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 1rem 1.25rem;
        border-radius: 0.5rem;
        margin-top: 0.75rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .insight-header {
        font-weight: 700;
        color: #1E40AF;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .insight-text {
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.5;
        margin: 0;
    }
    .metric-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_URL)
        
        # 1. 장르 전처리: '|' 구분 시 첫 번째 장르만 추출
        df['genre_clean'] = df['genre'].astype(str).apply(
            lambda x: x.split('|')[0].strip() if pd.notnull(x) and x != 'nan' else '기타'
        )
        
        # 2. 수치형 컬럼 변환
        numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        # 3. 개봉일 날짜형 변환
        if 'openDt' in df.columns:
            df['openDt_str'] = df['openDt'].astype(str).str.replace('.0', '', regex=False)
            df['openDt_parsed'] = pd.to_datetime(df['openDt_str'], format='%Y%m%d', errors='coerce')
            
        return df
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

df = load_data()

# App Header
st.markdown('<div class="main-title">🎬 영화 데이터 그래프 도감 2</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">영화 흥행 데이터의 분포와 관계 분석 (KOBIS 216편 데이터 기준)</div>', unsafe_allow_html=True)

if df.empty:
    st.stop()

# Sidebar controls & info
with st.sidebar:
    st.header("⚙️ 분석 설정")
    st.info("💡 영화 데이터의 장르별 비중, 총 관객 수 관찰, 흥행 분포를 탐색해보세요.")
    
    st.divider()
    st.markdown("### 📊 데이터 요약")
    st.metric("총 분석 영화 수", f"{len(df):,} 편")
    st.metric("총 관객 수 합계", f"{int(df['total_audi'].sum()):,} 명")
    st.metric("평균 10위권 체류일", f"{df['days_in_top10'].mean():.1f} 일")
    
    st.divider()
    
    with st.expander("📦 requirements.txt 보기"):
        st.code("""streamlit
pandas
plotly""", language="text")

# Key Metrics Overview
top_movie = df.loc[df['total_audi'].idxmax()] if not df.empty else None
top_genre = df['genre_clean'].mode()[0] if not df.empty else "N/A"

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.markdown('<div class="metric-card"><b>총 분석 영화 편수</b><h3>216 편</h3></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="metric-card"><b>최다 영화 장르</b><h3>{top_genre}</h3></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown(f'<div class="metric-card"><b>최다 관객 수 영화</b><h3>{top_movie["movieNm"] if top_movie is not None else "-"}</h3></div>', unsafe_allow_html=True)
with col_m4:
    st.markdown('<div class="metric-card"><b>평균 총 관객 수</b><h3>' + f"{int(df['total_audi'].mean()):,} 명" + '</h3></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Helper function for rendering insightful text callouts
def render_insight(text):
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-header">💡 이 그래프로 알 수 있는 것</div>
        <p class="insight-text">{text}</p>
    </div>
    """, unsafe_allow_html=True)

st.subheader("1. 장르별 영화 편수 비율 (도넛 그래프)")

genre_counts = df['genre_clean'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

fig_donut = px.pie(
    genre_counts,
    names='장르',
    values='편수',
    hole=0.45,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_donut.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>"
)

fig_donut.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    legend_title_text="장르",
    height=420
)

st.plotly_chart(fig_donut, use_container_width=True)

render_insight(
    "상위 박스오피스 영화 중 <b>드라마, 액션, 애니메이션</b> 장르가 절반 이상을 차지하며, 영화 제작 및 박스오피스 진입이 특정 장르에 집중되어 있음을 파악할 수 있습니다."
)

st.divider()

st.subheader("2. 장르 및 영화별 총 관객 수 (트리맵)")

# Ensure non-zero total_audi for treemap visualization
df_treemap = df.copy()
df_treemap['total_audi_plot'] = df_treemap['total_audi'].apply(lambda x: max(x, 1))

fig_treemap = px.treemap(
    df_treemap,
    path=[px.Constant("전체 영화"), 'genre_clean', 'movieNm'],
    values='total_audi_plot',
    color='genre_clean',
    color_discrete_sequence=px.colors.qualitative.Set3,
    custom_data=['movieNm', 'total_audi', 'genre_clean']
)

fig_treemap.update_traces(
    hovertemplate="<b>영화명:</b> %{customdata[0]}<br><b>장르:</b> %{customdata[2]}<br><b>총 관객 수:</b> %{customdata[1]:,}명<extra></extra>",
    marker=dict(cornersize=4)
)

fig_treemap.update_layout(
    margin=dict(t=30, b=20, l=10, r=10),
    height=550
)

st.plotly_chart(fig_treemap, use_container_width=True)

render_insight(
    "트리맵 칸의 크기를 통해 장르 내 어떤 영화가 독보적인 관객 수(total_audi)를 끌어모았는지 직관적으로 확인이 가능하며, 대형 흥행작 몇 편이 장르 전체의 관객 파이를 크게 견인함을 알 수 있습니다."
)

st.divider()

st.subheader("3. 개봉 첫 주 관객 수와 총 관객 수의 관계")

fig_scatter = px.scatter(
    df,
    x='first_week_audi',
    y='total_audi',
    color='genre_clean',
    size='days_in_top10',
    hover_name='movieNm',
    hover_data={'first_week_audi': ':,', 'total_audi': ':,', 'days_in_top10': True, 'genre_clean': False},
    labels={
        'first_week_audi': '개봉 첫 주 관객 수 (명)',
        'total_audi': '총 관객 수 (명)',
        'genre_clean': '주요 장르',
        'days_in_top10': '10위권 유지일'
    },
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_scatter.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    height=480
)

st.plotly_chart(fig_scatter, use_container_width=True)

render_insight(
    "개봉 첫 주 관객 수가 많을수록 최종 총 관객 수 또한 비례하여 커지는 강한 선형 관계를 보이며, 초기 흥행 성과가 영화의 최종 스코어 결정에 매우 핵심적임을 알 수 있습니다."
)

st.divider()

st.subheader("4. 주요 장르별 총 관객 수 분포 (박스플롯)")

top_genres = genre_counts.head(6)['장르'].tolist()
df_top_genres = df[df['genre_clean'].isin(top_genres)]

fig_box = px.box(
    df_top_genres,
    x='genre_clean',
    y='total_audi',
    color='genre_clean',
    points='all',
    hover_name='movieNm',
    labels={'genre_clean': '장르', 'total_audi': '총 관객 수 (명)'},
    color_discrete_sequence=px.colors.qualitative.Safe
)

fig_box.update_layout(
    showlegend=False,
    margin=dict(t=20, b=20, l=20, r=20),
    height=450
)

st.plotly_chart(fig_box, use_container_width=True)

render_insight(
    "대부분의 장르에서 영화별 관객 수가 하위~중앙 영역에 집중된 편이나, 액션과 드라마 등의 특정 장르에서는 상단에 이상치(Outlier)에 해당하는 메가 히트작들이 존재함을 확인할 수 있습니다."
)

st.divider()

st.subheader("5. 10위권 유지 날수(days_in_top10) 분포")

fig_hist = px.histogram(
    df,
    x='days_in_top10',
    nbins=20,
    color_discrete_sequence=['#6366F1'],
    labels={'days_in_top10': 'Top 10 유지 날수', 'count': '영화 수'},
    text_auto=True
)

fig_hist.update_layout(
    xaxis_title="TOP 10 머문 날수 (일)",
    yaxis_title="영화 수 (편)",
    bargap=0.1,
    margin=dict(t=20, b=20, l=20, r=20),
    height=400
)

st.plotly_chart(fig_hist, use_container_width=True)

render_insight(
    "대부분의 박스오피스 영화는 10~30일 이내에 TOP 10 권역에서 이탈하며, 50일 이상 장기 흥행을 이어가는 작품은 극히 소수에 해당합니다."
)

st.divider()

with st.expander("📄 원본 데이터 전체 보기"):
    st.dataframe(
        df[['movieCd', 'movieNm', 'genre_clean', 'nation', 'openDt_str', 'first_scrn', 'first_week_audi', 'total_audi', 'days_in_top10']],
        use_container_width=True,
        hide_index=True
    )
