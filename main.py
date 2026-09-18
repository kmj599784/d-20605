import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="영화 박스오피스 분석", page_icon="🎬", layout="wide"
)

# App 제목
st.title("🎬 영화 박스오피스 데이터 분석 App")


# [1. 데이터 불러오기]
# @st.cache_data decorator를 사용하여 데이터가 캐시에 저장되도록 합니다.
# 이렇게 하면 앱이 다시 실행될 때 파일 전달을 위해 매번 다운로드하지 않고 저장된 데이터를 재사용합니다.
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
# 영화별 최대 누적관객수를 구해 내림차순 정렬
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


# [5. 구역 나누기]
# 구역 1: 기본 추이 분석 (선 그래프)
st.header(f"📌 '{selected_movie}' 관객수 추이")

# [4. 선그래프 그리기]
# 선택된 영화의 '기준일자'별 '해당일관객수' 변화를 Plotly 선그래프로 생성합니다.
fig1 = px.line(
    filtered_data,
    x="기준일자",
    y="해당일관객수",
    title=f"일자별 관객수 변화 그래프",
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면에 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 하단 분석 결과 안내 문구 자리
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 개봉 후 일자별 관객수 증감 추이 및 흥행 피크 시점을 확인할 수 있습니다."
)

st.markdown("---")  # 구분선

# [5. 추가 그래프를 위한 구역 (예시 구역)]
st.header("📌 추가 분석 구역 (추후 업데이트 예정)")
st.caption("여기에 새로운 차트나 분석 항목을 계속 추가할 수 있습니다.")

# 예시: 추가 그래프용 하단 안내문구 자리
st.info("💡 **이 그래프로 알 수 있는 것:** (추가 예정인 그래프의 분석 요약)")
