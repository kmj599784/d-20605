import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="영화 박스오피스 분석", page_icon="🎬", layout="wide"
)

# App 제목
st.title("🎬 영화 박스오피스 데이터 분석 App")


# [1. 데이터 불러오기]
# @st.cache_data decorator를 사용하여 데이터가 캐시에 저장되도록 합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(값이 없는 데이터)가 있는 행을 제거합니다.
    df = df.dropna()

    # '기준일자' 컬럼을 datetime(날짜) 형식으로 변환합니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 오름차순으로 정렬합니다.
    df = df.sort_values(by="기준일자", ascending=True)

    return df


# 데이터 로드 실행
data = load_data()


# [3. 영화 선택 기능]
# 누적관객수가 가장 높은 순서대로 중복 없이 영화 이름을 추출합니다.
movie_order = (
    data.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에서 분석할 영화를 선택할 수 있게 만듭니다.
st.sidebar.header("🔍 설정")
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요:", options=movie_order
)

# 사용자가 선택한 영화의 데이터만 필터링합니다.
filtered_data = data[data["영화명"] == selected_movie]


# [4. 구역 1: 개별 영화 일자별 관객수 (선 그래프)]
st.header(f"📌 '{selected_movie}' 일별 관객수 추이")

fig1 = px.line(
    filtered_data,
    x="기준일자",
    y="해당일관객수",
    title="일자별 관객수 변화",
    markers=True,
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 개봉 후 일자별 관객수 증감 추이 및 흥행 피크 시점을 확인할 수 있습니다."
)

st.markdown("---")


# [5. 구역 2: 개별 영화 누적관객수 추이 (영역 차트)]
st.header(f"📌 '{selected_movie}' 누적 관객수 추이")

fig2 = px.area(
    filtered_data,
    x="기준일자",
    y="누적관객수",
    title="일자별 누적 관객수 증가 추이",
    markers=True,
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 시간 경과에 따라 '{selected_movie}'의 전체 누적 관객수가 어떤 속도로 증가했는지(상승 완만도/급증 구간) 한눈에 파악할 수 있습니다."
)

st.markdown("---")


# [6. 구역 3: 조건을 만족하는 상위 5개 영화 누적관객수 비교 (다중 선 그래프)]
st.header("📌 장기 흥행 TOP 5 영화 누적 관객수 비교")

movie_counts = data.groupby("영화명").size()
long_running_movies = movie_counts[movie_counts >= 20].index
filtered_long_data = data[data["영화명"].isin(long_running_movies)]

top5_long_movies = (
    filtered_long_data.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

top5_data = data[data["영화명"].isin(top5_long_movies)]

fig3 = px.line(
    top5_data,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP10 20일 이상 진입 영화 중 누적 관객수 상위 5개 비교",
    markers=True,
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** TOP10 차트에 20일 이상 유지된 장기 흥행작 중 상위 5개 영화({', '.join(top5_long_movies)})의 일자별 누적 관객수 성장세를 비교하여, 장기 흥행 영화들의 관객 동원력 차이를 확인할 수 있습니다."
)

st.markdown("---")


# [7. 구역 4: 전체 박스오피스 관객수 및 7일 이동평균 (선 그래프)]
st.header("📌 전체 박스오피스 일별 총관객수 & 7일 이동평균 추이")

daily_total = (
    data.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

daily_total["7일_이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7).mean()
)

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 총관객수 (원본)",
        line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),
    )
)

fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#FF4B4B", width=3),
    )
)

fig4.update_layout(
    title="전체 박스오피스 관객수 추이 및 7일 이동평균선",
    xaxis_title="기준일자",
    yaxis_title="해당일 총관객수",
    hovermode="x unified",
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 요일별 관객수 변동(주말 급증, 평일 감소) 노이즈를 7일 이동평균선으로 완화하여 전체 영화 시장의 중장기적인 성수기/비수기 흐름과 흥행 트렌드를 파악할 수 있습니다."
)

st.markdown("---")


# [8. 구역 5: 전체 박스오피스 월별 총관객수 (막대 그래프)]
st.header("📌 전체 박스오피스 월별 총관객수")

daily_total["연월"] = daily_total["기준일자"].dt.to_period("M").astype(str)

monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

fig5 = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 박스오피스 관객수 합계",
    text_auto=".2s",
    labels={"연월": "월", "해당일관객수": "월간 총관객수"},
)

fig5.update_traces(marker_color="#4F8BF9", textposition="outside")
fig5.update_layout(xaxis_type="category")

st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 월별 박스오피스 총 관객수 규모를 비교하여 영화 시장의 연중 최고 성수기 월과 비수기 월을 한눈에 식별할 수 있습니다."
)

st.markdown("---")


# [9. 구역 6: 캘린더 히트맵 (월/주차 x 요일)]
st.header("📌 캘린더 히트맵 (요일 및 월별 관객수 분포)")

# 1) 요일 및 월/주차 정보 생성
# YYYY-MM-DD 포맷 텍스트 저장 (마우스 호버용)
daily_total["날짜텍스트"] = daily_total["기준일자"].dt.strftime("%Y-%m-%d")

# 한국어 요일 지정 및 순서 정렬
day_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
daily_total["요일"] = daily_total["기준일자"].dt.dayofweek.map(day_map)
days_order = ["월", "화", "수", "목", "금", "토", "일"]

# y축 표시를 위한 연-월 및 월 내 주차 표현 (예: 2023-08 W1)
daily_total["월_주차"] = (
    daily_total["기준일자"].dt.strftime("%Y-%m")
    + " W"
    + daily_total["기준일자"].dt.day.apply(lambda d: str((d - 1) // 7 + 1))
)

# 2) Density Heatmap 생성
fig6 = px.density_heatmap(
    daily_total,
    x="요일",
    y="월_주차",
    z="해당일관객수",
    category_orders={"요일": days_order},  # 월요일부터 일요일 순 정렬
    color_continuous_scale="Reds",  # 관객수가 많을수록 진한 빨간색
    title="일별 전체 관객수 캘린더 히트맵",
    hover_data={
        "날짜텍스트": True,
        "해당일관객수": ":,",
        "요일": False,
        "월_주차": False,
    },
    labels={
        "해당일관객수": "총관객수",
        "날짜텍스트": "날짜 (YYYY-MM-DD)",
        "월_주차": "월 / 주차",
    },
)

# 히트맵 레이아웃 세부 설정
fig6.update_layout(
    xaxis_title="요일",
    yaxis_title="월 / 주차",
    coloraxis_colorbar=dict(title="관객수"),
)

st.plotly_chart(fig6, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** 주말(토·일)과 평일 간의 관객수 격차뿐만 아니라, 특정 주차나 공휴일/명절 시기에 관객수가 집중되는 패턴을 캘린더 형태의 색상 농도로 직관적으로 확인할 수 있습니다."
)
