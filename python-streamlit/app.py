"""
app.py - 교육용 Streamlit 대시보드 메인 애플리케이션
===================================================
(Educational Streamlit Dashboard Main Application)

========== 전체 구조 (Overall Structure) ==========

이 앱은 7개의 페이지로 구성된 Streamlit 교육용 대시보드입니다.
각 페이지는 SQLite 데이터베이스에서 데이터를 불러와 다양한 방식으로
시각화하고 관리하는 기능을 제공합니다.

📂 페이지 구성:
  1. 개요 (Overview)      → KPI 카드 + 차트 (막대/파이/라인)
  2. 학생 관리 (Students) → 학생 목록 테이블 + 검색
  3. 과목 현황 (Courses)  → 강좌 카드 리스트
  4. 강의 내용 (Lessons)  → 강좌별 수업 목록 (expander)
  5. 과제 제출 (Submissions) → 제출 목록 + 코드 미리보기
  6. 커리큘럼 (Curriculum)  → 모듈/스텝 학습 진행 관리
  7. 학습 현황 (Progress)   → 과목별/학생별 진행 통계

🔄 데이터 흐름 (Data Flow):
  SQLite DB → db_helper 함수들 → @st.cache_data 캐싱 → Pandas DataFrame
  → Altair 차트 / Streamlit 위젯으로 렌더링

🛠 사용된 주요 Streamlit 개념:
  - st.set_page_config()    : 페이지 기본 설정
  - st.sidebar.radio()      : 사이드바 페이지 네비게이션
  - @st.cache_data          : 데이터 캐싱 (성능 최적화)
  - st.columns()            : 컬럼 기반 레이아웃
  - st.dataframe()          : 인터랙티브 데이터 테이블
  - st.altair_chart()       : Altair 차트 렌더링
  - st.expander()           : 접이식 섹션
  - st.markdown()           : HTML/CSS 커스텀 렌더링

Streamlit의 동작 방식:
  Streamlit은 파이썬 스크립트를 위에서 아래로 실행하며,
  사용자 상호작용(클릭, 입력)이 발생할 때마다 전체 스크립트를
  다시 실행(re-run)합니다. @st.cache_data는 이 과정에서
  데이터베이스 호출을 최소화하여 성능을 향상시킵니다.
"""

import sys
import os

# 공유 DB 모듈 경로 추가 (Add shared DB module path)
# -----------------------------------------------------------------
# sys.path.insert(0, ...) 는 파이썬의 모듈 검색 경로를 수동으로 추가합니다.
# 여기서는 현재 파일(app.py)이 위치한 디렉토리에서 ../shared/db 로 이동하여
# db_helper.py 모듈을 임포트할 수 있도록 경로를 추가합니다.
#
# 📌 os.path.dirname(os.path.abspath(__file__))
#   - __file__: 현재 실행 중인 파일의 상대 경로
#   - os.path.abspath(): 상대 경로 → 절대 경로 변환
#   - os.path.dirname(): 파일의 부모 디렉토리 반환
# 이렇게 하면 어디서 실행하든 올바른 경로를 참조할 수 있습니다.
# -----------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared", "db"))

import streamlit as st
import pandas as pd
import altair as alt
from db_helper import (
    get_all_students,
    get_all_courses,
    get_lessons_by_course,
    get_all_submissions,
    get_student_count,
    get_course_count,
    get_submission_count,
    get_avg_score,
    get_students_by_course,
    get_grade_distribution,
    get_submissions_timeline,
    search_students,
    get_all_lessons,
    get_curriculum_by_course,
    get_student_progress,
    update_student_progress,
)

# =====================================================================
# 1. 페이지 설정 (Page Configuration)
# =====================================================================
# st.set_page_config()는 Streamlit 앱의 가장 첫 번째 Streamlit 명령어여야 합니다!
# 어떤 위젯(제목, 버튼 등)보다 먼저 호출되어야 하며, 그렇지 않으면 오류가 발생합니다.
#
# 📌 page_title:
#   브라우저 탭에 표시될 제목입니다. SEO와 사용자 경험에 영향을 줍니다.
#
# 📌 page_icon:
#   브라우저 탭 아이콘(favicon)으로 표시될 이모지 또는 이미지 경로입니다.
#   이모지를 사용하면 별도의 이미지 파일 없이 아이콘을 설정할 수 있습니다.
#
# 📌 layout="wide":
#   기본값은 "centered"(중앙 정렬, 약 800px 폭)입니다.
#   "wide"로 설정하면 브라우저 전체 너비를 사용하여 넓은 레이아웃을 구성할 수 있습니다.
#   대시보드나 데이터 시각화 앱에 특히 유용합니다.
#
# 📌 initial_sidebar_state="expanded":
#   사이드바의 초기 상태를 설정합니다.
#   - "expanded": 사이드바가 펼쳐진 상태로 시작
#   - "collapsed": 사이드바가 접힌 상태로 시작
#   - "auto": 사용자의 마지막 상태를 기억 (모바일 등)
# -----------------------------------------------------------------
st.set_page_config(
    page_title="교육 대시보드",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# 2. 커스텀 CSS 스타일 설정 (Custom CSS)
# =====================================================================
# st.markdown()에 unsafe_allow_html=True 옵션을 주면 HTML <style> 태그를
# 사용하여 페이지에 커스텀 CSS를 적용할 수 있습니다.
#
# ⚠️ unsafe_allow_html=True:
#   HTML/JS 주입 공격에 노출될 수 있으므로 신뢰할 수 있는 콘텐츠에만 사용하세요.
#   여기서는 직접 작성한 CSS이므로 안전합니다.
#
# 아래 CSS는 KPI(Key Performance Indicator) 카드의 스타일을 정의합니다:
# - .kpi-card: 카드 배경, 둥근 모서리, 그림자 효과
# - .kpi-value: 큰 숫자(KPI 값) 스타일 (2.5rem = 약 40px)
# - .kpi-label: 작은 레이블 텍스트 스타일
# -----------------------------------------------------------------
st.markdown(
    """
<style>
    .kpi-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 1rem;
        color: #555;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =====================================================================
# 3. 데이터 로딩 함수 (Data Loading Functions) - 캐싱 적용
# =====================================================================
# @st.cache_data 데코레이터 (Decorator)
# ---------------------------------------------------------------
# 📌 @st.cache_data의 역할:
#   Streamlit은 사용자 상호작용이 있을 때마다 스크립트 전체를 다시 실행(re-run)합니다.
#   이때 매번 데이터베이스에 쿼리를 보내면 성능이 크게 저하됩니다.
#   @st.cache_data는 함수의 반환값을 캐시(임시 저장)하여, 동일한 인자로 호출되면
#   실제 함수를 실행하지 않고 캐시된 결과를 반환합니다.
#
# 📌 ttl 파라미터 (Time-To-Live):
#   ttl=60은 캐시된 데이터의 유효 시간을 60초로 설정합니다.
#   60초가 지나면 캐시가 만료되고, 다음 호출 시 실제 함수가 다시 실행됩니다.
#   - ttl을 너무 짧게 설정하면 캐싱 효과가 줄어듭니다.
#   - ttl을 너무 길게 설정하면 데이터가 오래되어 실제 DB와 차이가 날 수 있습니다.
#   - ttl=None으로 설정하면 세션 동안 영구 캐시됩니다.
#
# 📌 해시 동작:
#   @st.cache_data는 함수명과 인자값을 기반으로 해시 키를 생성합니다.
#   입력 인자가 변경되면 자동으로 새로운 캐시를 생성합니다.
#
# 📌 st.cache_data.clear():
#   모든 캐시를 수동으로 초기화합니다. 커리큘럼 페이지에서
#   '완료' 버튼 클릭 후 데이터 변경사항을 반영하기 위해 사용됩니다.
# ---------------------------------------------------------------

# --- KPI 데이터 로드 (Load KPI Data) ---
@st.cache_data(ttl=60)
#                    ^^^^^^^^
#                    ttl=60: 60초 동안 캐시 유지.
#                    즉, 60초 안에 다시 호출되면 DB에 가지 않고 캐시된 값 사용.
def load_kpi_data():
    """
    KPI(핵심 성과 지표) 데이터를 로드합니다.

    반환값 (Return value):
        dict - 학생 수, 과목 수, 제출 수, 평균 점수를 담은 딕셔너리
    """
    return {
        "students": get_student_count(),
        "courses": get_course_count(),
        "submissions": get_submission_count(),
        "avg_score": get_avg_score(),
    }


# --- 학생 데이터 로드 (Load Students DataFrame) ---
@st.cache_data(ttl=60)
def load_students_df():
    """
    전체 학생 데이터를 Pandas DataFrame으로 반환합니다.

    📌 왜 pd.DataFrame 변환이 필요한가요?
      db_helper.get_all_students()는 SQLite Row 객체의 리스트를 반환합니다.
      SQLite Row 객체는 인덱스(숫자)와 키(컬럼명)로 접근 가능하지만,
      Streamlit의 st.dataframe()과 Altair 차트는 Pandas DataFrame만 입력으로 받습니다.
      따라서 dict()로 변환 후 pd.DataFrame()으로 감싸서 사용합니다.

      변환 과정: SQLite Row 객체 → dict → pd.DataFrame
      - dict(s): Row 객체의 각 컬럼을 {컬럼명: 값} 형태의 딕셔너리로 변환
      - [dict(s) for s in students]: 각 Row 객체를 딕셔너리로 변환한 리스트
      - pd.DataFrame([...]): 딕셔너리 리스트를 DataFrame으로 변환

    반환값 (Return value):
        pd.DataFrame - 학생 정보가 담긴 데이터프레임 (데이터 없으면 빈 DataFrame)
    """
    students = get_all_students()
    if students:
        # 리스트 컴프리헨션: 각 Row 객체를 dict로 변환 → DataFrame 생성
        df = pd.DataFrame([dict(s) for s in students])
        return df
    return pd.DataFrame()


# --- 강좌 데이터 로드 (Load Courses DataFrame) ---
@st.cache_data(ttl=60)
def load_courses_df():
    """강좌 데이터를 Pandas DataFrame으로 반환합니다."""
    courses = get_all_courses()
    if courses:
        df = pd.DataFrame([dict(c) for c in courses])
        return df
    return pd.DataFrame()


# --- 제출 데이터 로드 (Load Submissions DataFrame) ---
@st.cache_data(ttl=60)
def load_submissions_df():
    """과제 제출 데이터를 Pandas DataFrame으로 반환합니다."""
    submissions = get_all_submissions()
    if submissions:
        df = pd.DataFrame([dict(s) for s in submissions])
        return df
    return pd.DataFrame()


# --- 강좌별 수업 데이터 로드 (Load Lessons by Course) ---
@st.cache_data(ttl=60)
def load_lessons_by_course():
    """
    각 강좌에 속한 수업(lesson) 데이터를 딕셔너리 형태로 반환합니다.

    반환 구조 (Return structure):
        {
            "강좌명1": [lesson_dict1, lesson_dict2, ...],
            "강좌명2": [lesson_dict1, ...],
            ...
        }

    이 구조는 나중에 st.expander()로 강좌별로 그룹화하여 표시할 때 사용됩니다.
    """
    courses = get_all_courses()
    result = {}
    for course in courses:
        lessons = get_lessons_by_course(course["id"])
        # SQLite Row 객체 → dict 변환 (DataFrame 없이 dict 리스트로 유지)
        result[course["title"]] = [dict(l) for l in lessons] if lessons else []
    return result


# =====================================================================
# 4. 사이드바 네비게이션 (Sidebar Navigation)
# =====================================================================
# st.sidebar는 Streamlit에서 사이드바 영역을 구성하는 방법입니다.
# 일반 위젯(st.title, st.button 등) 앞에 'st.sidebar.'를 붙이면
# 해당 위젯이 메인 영역 대신 사이드바에 배치됩니다.
#
# 📌 사이드바를 페이지 전환에 사용하는 패턴:
#   st.sidebar.radio()로 선택된 페이지 이름을 'page' 변수에 저장하고,
#   이후 if-elif 조건문으로 page 값을 확인하여 해당 페이지 콘텐츠를 렌더링합니다.
#
#   이 패턴은 다음과 같은 장점이 있습니다:
#   1. 별도의 URL 라우팅(flask, django 등) 없이 페이지 전환 구현 가능
#   2. 하나의 .py 파일로 여러 페이지를 관리할 수 있음
#   3. 멀티페이지 앱보다 상태 공유가 쉬움 (변수, 캐시 등)
#
# 📌 st.sidebar.radio()의 주요 파라미터:
#   - label: 위젯 위에 표시될 텍스트
#   - options: 선택 가능한 옵션 리스트 (문자열 리스트)
#   - index: 기본 선택값 (0부터 시작)
#   - key: (선택사항) 위젯의 고유 키 - 세션 상태 유지에 사용
#
# 반환값: 사용자가 선택한 옵션 문자열 (예: "개요", "학생 관리", ...)
# -----------------------------------------------------------------
st.sidebar.title("📚 교육 대시보드")
st.sidebar.markdown("---")

# 페이지 선택 라디오 버튼 (Page Selection Radio)
# 반환된 문자열(page)로 이후 표시할 페이지를 결정합니다.
page = st.sidebar.radio(
    "페이지 선택 (Select Page)",                       # 라벨: 위젯 위에 표시
    ["개요", "학생 관리", "과목 현황", "강의 내용",      # 옵션 목록
     "과제 제출", "커리큘럼", "학습 현황"],
    index=0,                                           # 기본 선택: 첫 번째("개요")
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 이 앱은 Streamlit 교육용으로 제작되었습니다.\n"
    "(This app is built for Streamlit education.)"
    # 📌 st.sidebar.info() vs st.sidebar.warning() vs st.sidebar.error():
    #   - info()    : 파란색 정보 메시지 (일반 안내)
    #   - success() : 초록색 성공 메시지 (작업 완료)
    #   - warning(): 노란색 경고 메시지 (주의 필요)
    #   - error()   : 빨간색 오류 메시지 (문제 발생)
)


# =====================================================================
# 5. 메인 페이지 라우팅 (Main Page Routing)
# =====================================================================
# page 변수에 저장된 선택값에 따라 아래 if-elif 조건문으로
# 표시할 페이지 콘텐츠가 결정됩니다.
#
# 📌 조건부 렌더링 패턴:
#   if page == "개요":       → 개요 페이지 렌더링
#   elif page == "학생 관리": → 학생 관리 페이지 렌더링
#   ...
#
#   이 패턴의 특징:
#   - 모든 페이지 코드가 하나의 파일에 있으므로 공유 함수/변수 사용이 쉬움
#   - 페이지 전환 시 Streamlit이 스크립트를 다시 실행하므로 상태 관리 주의 필요
#   - 무거운 데이터 로딩 함수는 @st.cache_data로 캐싱하여 성능 확보
# =====================================================================

# ===== 1. 개요 페이지 (Overview Page) =====
if page == "개요":

    st.title("📊 대시보드 개요")
    st.markdown("교육 데이터의 전체적인 현황을 한눈에 확인합니다.")

    # --- KPI 카드 (Key Performance Indicator Cards) ---
    # KPI: 핵심 성과 지표. 데이터의 주요 수치를 한눈에 보여줍니다.
    kpi = load_kpi_data()

    # ================================================================
    # st.columns()로 레이아웃 구성하기
    # ----------------------------------------------------------------
    # st.columns(n)은 n개의 동일한 너비 컬럼을 생성합니다.
    # 반환값은 컬럼 객체의 리스트로, 각 컬럼을 with 문으로 열어
    # 독립적인 콘텐츠를 배치할 수 있습니다.
    #
    # 📌 다양한 컬럼 비율 지정:
    #   st.columns([1, 2, 1])  → 가운데 컬럼이 양옆의 2배 너비
    #   st.columns([2, 1])     → 왼쪽이 오른쪽의 2배 너비
    #   st.columns(3)          → 3개의 동일한 너비 컬럼
    #
    # 📌 with col1: ... 구문:
    #   Python의 with 문을 사용하여 특정 컬럼 안에 콘텐츠를 배치합니다.
    #   with 블록 안에서 st.***()를 호출하면 해당 컬럼 안에 렌더링됩니다.
    # ================================================================

    # 4개의 동일한 너비 컬럼 생성 → KPI 카드 4개 배치
    col1, col2, col3, col4 = st.columns(4)

    # 각 컬럼에 KPI 카드 표시
    # unsafe_allow_html=True로 HTML div를 직접 렌더링하여
    # 커스텀 스타일(.kpi-card, .kpi-value, .kpi-label)을 적용합니다.
    with col1:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['students']}</div>
            <div class="kpi-label">👨‍🎓 총 학생수</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['courses']}</div>
            <div class="kpi-label">📖 과목수</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['submissions']}</div>
            <div class="kpi-label">📝 제출수</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['avg_score']}</div>
            <div class="kpi-label">⭐ 평균 점수</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- 차트 영역 (Charts Section) ---
    # 2개의 동일한 너비 컬럼: 왼쪽에 막대 차트, 오른쪽에 파이 차트
    col_chart1, col_chart2 = st.columns(2)

    # ---- 강좌별 학생 수 막대 차트 (Bar Chart: Students per Course) ----
    with col_chart1:
        st.subheader("📊 강좌별 학생 수")

        course_data = get_students_by_course()
        if course_data:
            # SQLite Row → DataFrame 변환
            df_courses = pd.DataFrame([dict(c) for c in course_data])

            # ============================================================
            # Altair 차트 생성 - 각 레이어 설명
            # ------------------------------------------------------------
            # Altair은 선언적(declarative) 시각화 라이브러리입니다.
            # "무엇을 그리고 싶은지"만 지정하면 나머지는 Altair이 처리합니다.
            #
            # 📌 alt.Chart(data): 차트의 기반이 되는 데이터 소스를 지정합니다.
            #     pandas DataFrame을 직접 전달합니다.
            #
            # 📌 .mark_bar(): 막대 차트(Mark)를 선택합니다.
            #     - mark_bar()  : 막대 그래프 (Bar chart)
            #     - mark_line() : 선 그래프 (Line chart)
            #     - mark_point(): 산점도 (Scatter plot)
            #     - mark_arc()  : 파이/도넛 차트 (Pie chart)
            #     - mark_area() : 영역 차트 (Area chart)
            #     각 mark_* 함수는 스타일 파라미터(color, opacity, size 등)를 받을 수 있습니다.
            #
            # 📌 .encode(x=..., y=..., color=...):
            #     차트의 인코딩(encoding) 채널을 지정합니다.
            #     인코딩이란 데이터의 컬럼을 차트의 시각적 속성에 매핑하는 것을 말합니다:
            #
            #     - x (X축): 데이터를 수평 축에 매핑
            #       alt.X("컬럼명:데이터타입", title="표시할 이름")
            #       데이터타입: N(명목형), Q(수치형), T(시간형), O(순서형)
            #
            #     - y (Y축): 데이터를 수직 축에 매핑
            #
            #     - color: 데이터를 색상에 매핑 (범주 구분)
            #       alt.Color("컬럼명:N", title="범례 제목")
            #       legend=None → 범례 숨김
            #
            #     - tooltip: 마우스 호버 시 표시될 정보
            #       ["컬럼1", "컬럼2"] 형태로 리스트 전달
            #
            #     - theta: 파이 차트에서 각도(크기)를 결정하는 채널
            #
            # 📌 .properties(height=300):
            #     차트의 높이를 픽셀 단위로 지정합니다.
            #
            # 📌 st.altair_chart(chart, use_container_width=True):
            #     생성된 Altair 차트 객체를 Streamlit에 렌더링합니다.
            #     use_container_width=True → 컨테이너 너비에 맞춰 자동 크기 조절
            # ============================================================

            chart = (
                alt.Chart(df_courses)
                .mark_bar()
                #   ^^^^^^^^
                #   mark_bar(): 세로 막대 차트를 생성합니다.
                #   데이터 값을 막대의 높이로 표현하여 항목 간 비교에 효과적입니다.
                .encode(
                    x=alt.X(
                        "title:N",  # X축: 강좌명 (N=명목형, Nominal)
                        title="강좌명",  # 축 레이블
                        sort="-y",  # Y축 값 기준 내림차순 정렬
                        #   ^^^^^^^^
                        #   sort="-y": Y축(학생 수)이 큰 순서대로 X축 정렬
                        #   sort="y": 오름차순, sort="-y": 내림차순
                    ),
                    y=alt.Y(
                        "student_count:Q",  # Y축: 학생 수 (Q=수치형, Quantitative)
                        title="학생 수",
                    ),
                    color=alt.Color(
                        "title:N",  # 강좌명별로 다른 색상 부여
                        legend=None,  # 범례 숨김 (X축 레이블로 충분)
                    ),
                    tooltip=[
                        "title",  # 마우스 호버 시 강좌명 표시
                        "student_count",  # 마우스 호버 시 학생 수 표시
                    ],
                )
                .properties(height=300)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            # st.info(): 파란색 정보 메시지 (일반 안내, 데이터 없음 등)
            st.info("데이터가 없습니다.")

    # ---- 학점 분포 파이 차트 (Pie Chart: Grade Distribution) ----
    with col_chart2:
        st.subheader("🥧 학점 분포")

        grade_data = get_grade_distribution()
        if grade_data:
            df_grades = pd.DataFrame([dict(g) for g in grade_data])

            chart = (
                alt.Chart(df_grades)
                .mark_arc()
                #   ^^^^^^^^
                #   mark_arc(): 파이 차트 또는 도넛 차트를 생성합니다.
                #   전체에 대한 각 항목의 비율을 보여줄 때 사용합니다.
                .encode(
                    theta=alt.Theta(
                        "count:Q",  # 각도(크기): 제출 수 (Q=수치형)
                        # ^^^^^^^^^^^^^
                        # theta 채널: 파이 차트에서 각 조각의 각도(크기)를 결정합니다.
                        # 값이 클수록 더 넓은 각도를 차지합니다.
                    ),
                    color=alt.Color(
                        "grade:N",  # 색상: 학점별 (N=명목형)
                        title="학점",  # 범례 제목 표시
                    ),
                    tooltip=[
                        "grade",  # 마우스 호버 시 학점
                        "count",  # 마우스 호버 시 개수
                    ],
                )
                .properties(height=300)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # ---- 월별 제출 추이 라인 차트 (Line Chart: Submissions Over Time) ----
    st.markdown("---")
    st.subheader("📈 월별 제출 추이")

    timeline_data = get_submissions_timeline()
    if timeline_data:
        df_timeline = pd.DataFrame([dict(t) for t in timeline_data])

        chart = (
            alt.Chart(df_timeline)
            .mark_line(point=True)
            #   ^^^^^^^^^^^^^^^^^^^^
            #   mark_line(): 선 그래프. 시간에 따른 추세를 보여줍니다.
            #   point=True: 각 데이터 포인트에 점(marker)을 함께 표시합니다.
            #   point=False(기본값): 선만 표시합니다.
            .encode(
                x=alt.X(
                    "month:N",  # X축: 월 (N=명목형)
                    title="월",
                ),
                y=alt.Y(
                    "count:Q",  # Y축: 제출 수 (Q=수치형)
                    title="제출 수",
                ),
                tooltip=[
                    "month",  # 마우스 호버 시 월
                    "count",  # 마우스 호버 시 제출 수
                ],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")


# ===== 2. 학생 관리 페이지 (Student Management Page) =====
elif page == "학생 관리":

    st.title("👨‍🎓 학생 관리")
    st.markdown("학생 정보를 조회하고 검색합니다.")

    # --- 검색 기능 (Search Functionality) ---
    # st.text_input(): 텍스트 입력 위젯
    # 사용자가 입력한 검색어를 search_query 변수에 저장합니다.
    # Streamlit이 re-run될 때 search_query 값이 유지됩니다.
    search_query = st.text_input(
        "🔍 학생 검색 (이름 또는 이메일)",
        placeholder="예: 김민수",  # 입력 필드 안에 표시될 힌트 텍스트
    )

    # 검색어가 있으면 검색 결과, 없으면 전체 목록 표시
    if search_query:
        students = search_students(search_query)
        if students:
            df = pd.DataFrame([dict(s) for s in students])

            # ================================================================
            # st.dataframe() vs st.table() 차이점
            # ----------------------------------------------------------------
            # 📌 st.dataframe():
            #   - 인터랙티브(Interactive) 테이블
            #   - 컬럼 정렬 가능 (클릭으로 오름/내림차순)
            #   - 셀 선택 및 복사 가능
            #   - 대용량 데이터에 최적화 (가상 스크롤)
            #   - use_container_width=True로 너비 조절 가능
            #   - hide_index=True로 인덱스 컬럼 숨김 가능
            #   - height 파라미터로 높이 제한 가능
            #
            # 📌 st.table():
            #   - 정적(Static) 테이블
            #   - 정렬, 선택, 복사 불가능
            #   - 전체 데이터를 한 번에 렌더링 (대용량에 부적합)
            #   - 빠른 렌더링이 필요하고 상호작용이 필요 없는 경우에 사용
            #
            # ✅ 일반적으로 st.dataframe()이 더 유용합니다.
            #    st.table()은 출력물 캡처 등 정적인 표시가 필요할 때 사용합니다.
            # ================================================================
            st.dataframe(df, use_container_width=True, hide_index=True)

            # st.success(): 초록색 성공 메시지
            # 작업이 성공적으로 완료되었음을 알릴 때 사용합니다.
            st.success(f"{len(df)}명의 학생을 찾았습니다.")
        else:
            # st.warning(): 노란색 경고 메시지
            # 사용자 주의가 필요한 상황(검색 결과 없음 등)에 사용합니다.
            # error()보다 심각도가 낮습니다.
            st.warning("검색 결과가 없습니다.")
    else:
        # 전체 학생 목록 표시 (Display all students)
        df_students = load_students_df()

        if not df_students.empty:
            # 컬럼 이름을 한국어로 변경
            # .rename(columns={...}): DataFrame의 컬럼명을 변경합니다.
            # 원본(df_students)은 유지되고 새로운 DataFrame(df_display)이 생성됩니다.
            df_display = df_students.rename(
                columns={
                    "id": "ID",
                    "name": "이름",
                    "email": "이메일",
                    "enrolled_date": "등록일",
                    "grade": "학점",
                }
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # 통계 요약 (Summary Statistics)
            col1, col2 = st.columns(2)
            with col1:
                # st.metric(): KPI 지표를 간결하게 표시하는 위젯
                # label + value 형식으로, 선택적으로 delta(변화량)를 표시할 수 있습니다.
                st.metric("전체 학생 수", len(df_students))
            with col2:
                # value_counts(): pandas Series 메서드 - 각 값의 빈도 계산
                grade_counts = df_students["grade"].value_counts()
                most_common = grade_counts.index[0] if len(grade_counts) > 0 else "N/A"
                st.metric("가장 많은 학점", most_common)
        else:
            st.info("등록된 학생이 없습니다.")


# ===== 3. 과목 현황 페이지 (Courses Status Page) =====
elif page == "과목 현황":

    st.title("📖 과목 현황")
    st.markdown("개설된 강좌의 현황을 확인합니다.")

    courses = get_all_courses()
    if courses:
        # 강좌를 카드 형태로 2열 그리드로 표시
        # range(0, len(courses), 2): 0부터 2씩 증가 (0, 2, 4, ...)
        # 한 줄에 2개씩 배치하는 그리드 패턴입니다.
        for i in range(0, len(courses), 2):
            col1, col2 = st.columns(2)
            for j, col in enumerate([col1, col2]):
                if i + j < len(courses):
                    course = courses[i + j]
                    with col:
                        # f-string과 markdown을 사용한 카드 스타일
                        st.markdown(
                            f"""
                        ### 📘 {course['title']}
                        - **강사:** {course['instructor']}
                        - **카테고리:** {course['category']}
                        - **설명:** {course['description']}
                        """
                        )
                        st.markdown("---")
    else:
        st.info("등록된 과목이 없습니다.")


# ===== 4. 강의 내용 페이지 (Lessons Content Page) =====
elif page == "강의 내용":

    st.title("📚 강의 내용")
    st.markdown("강좌별 수업 내용을 확인합니다.")

    lessons_by_course = load_lessons_by_course()

    if lessons_by_course:
        # st.expander(): 접이식 컨테이너 (Accordion UI)
        # --------------------------------------------------------------
        # 📌 st.expander(label):
        #   - label: 접혔을 때 보이는 제목
        #   - with 문으로 내부에 콘텐츠 배치
        #   - 기본값: 접힌 상태(collapsed)
        #   - expanded=True: 펼쳐진 상태로 시작
        #
        # 📌 사용 목적:
        #   - 많은 콘텐츠를 그룹화하여 화면 공간 절약
        #   - 사용자가 원하는 섹션만 열어서 볼 수 있음
        #   - 트리 구조의 데이터 표시에 적합
        # --------------------------------------------------------------
        for course_title, lessons in lessons_by_course.items():
            with st.expander(f"📘 {course_title} ({len(lessons)}개 수업)"):
                if lessons:
                    for lesson in lessons:
                        st.markdown(
                            f"""
                        **{lesson['order_num']}. {lesson['title']}**
                        > {lesson['content']}
                        """
                        )
                        st.markdown("")
                else:
                    st.info("등록된 수업이 없습니다.")
    else:
        st.info("등록된 강의가 없습니다.")


# ===== 5. 과제 제출 페이지 (Submissions Page) =====
elif page == "과제 제출":

    st.title("📝 과제 제출")
    st.markdown("학생들의 과제 제출 현황을 확인합니다.")

    df_submissions = load_submissions_df()

    if not df_submissions.empty:
        # --- 상태 필터 (Status Filter) ---
        # st.multiselect(): 여러 항목을 선택할 수 있는 드롭다운
        # 반환값: 선택된 항목들의 리스트
        # --------------------------------------------------------------
        # 📌 주요 파라미터:
        #   - label: 위젯 위에 표시할 텍스트
        #   - options: 전체 선택 가능한 옵션 목록
        #   - default: 기본 선택값 (기본값: 빈 리스트 = 모두 선택 해제)
        #
        # 📌 활용 팁:
        #   options에 df["컬럼"].unique().tolist()를 사용하면
        #   데이터에 존재하는 고유값들만 동적으로 옵션으로 제공할 수 있습니다.
        # --------------------------------------------------------------
        status_filter = st.multiselect(
            "상태 필터",
            options=df_submissions["status"].unique().tolist(),
            default=df_submissions["status"].unique().tolist(),
        )

        # 필터 적용 (Apply filter)
        # pandas 불리언 인덱싱: df[df["컬럼"].isin(리스트)]
        if status_filter:
            df_filtered = df_submissions[df_submissions["status"].isin(status_filter)]
        else:
            df_filtered = df_submissions

        # --- 제출 목록 테이블 ---
        st.subheader("📋 제출 목록")

        # 컬럼명 한글화
        df_display = df_filtered.rename(
            columns={
                "id": "ID",
                "student_name": "학생명",
                "lesson_title": "수업명",
                "course_title": "과목명",
                "score": "점수",
                "submitted_at": "제출일시",
                "status": "상태",
            }
        )
        # 특정 컬럼만 선택하여 표시 ([[...]] 로 컬럼 서브셋 지정)
        st.dataframe(
            df_display[["ID", "학생명", "과목명", "수업명", "점수", "제출일시", "상태"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # --- 코드 미리보기 (Code Preview Section) ---
        st.subheader("💻 코드 미리보기")

        # selectbox 옵션 생성: {표시 텍스트: ID} 딕셔너리
        # 딕셔너리 컴프리헨션으로 각 행의 ID와 학생명/수업명을 조합
        submission_options = {
            f"#{row['id']} - {row['student_name']} ({row['lesson_title']})": row["id"]
            for _, row in df_filtered.iterrows()
        }

        # st.selectbox(): 단일 선택 드롭다운
        selected = st.selectbox(
            "제출을 선택하세요",
            options=list(submission_options.keys()),
        )

        if selected:
            sub_id = submission_options[selected]
            sub_row = df_submissions[df_submissions["id"] == sub_id].iloc[0]

            # 2:1 비율 컬럼 (왼쪽 2, 오른쪽 1)
            # st.columns()는 정수뿐만 아니라 리스트로 비율 지정 가능
            col1, col2 = st.columns([2, 1])

            with col1:
                # st.code(): 코드 블록을 구문 강조(Syntax Highlighting)하여 표시
                # 주요 파라미터:
                #   - body: 표시할 코드 문자열
                #   - language: 구문 강조 언어 (python, javascript, sql 등)
                st.code(sub_row["code"], language="python")

            with col2:
                # 제출 메타데이터 표시
                st.metric("점수", f"{sub_row['score']}점")
                st.metric("상태", sub_row["status"])
                st.metric("학생", sub_row["student_name"])
                st.metric("수업", sub_row["lesson_title"])
                st.metric("과목", sub_row["course_title"])
                st.text(f"제출일시: {sub_row['submitted_at']}")

    else:
        st.info("제출된 과제가 없습니다.")


# ===== 6. 커리큘럼 페이지 (Curriculum Page) =====
elif page == "커리큘럼":

    st.title("🎯 커리큘럼")
    st.markdown("과목별 커리큘럼 모듈과 스텝을 학습합니다.")

    courses = get_all_courses()
    students = get_all_students()

    if not courses:
        st.info("등록된 과목이 없습니다.")
    else:
        # --- 학생 선택 ---
        # 딕셔너리 컴프리헨션: 학생 목록을 {표시명: ID} 형태로 변환
        student_options = (
            {f"{s['name']} ({s['email']})": s["id"] for s in students}
            if students
            else {}
        )
        if not student_options:
            st.warning("등록된 학생이 없습니다. 먼저 학생을 등록해주세요.")
        else:
            selected_student_name = st.selectbox(
                "👨‍🎓 학생 선택 (Select Student)",
                options=list(student_options.keys()),
                key="curriculum_student_select",  # 고유 key로 다른 selectbox와 구분
            )
            selected_student_id = student_options[selected_student_name]

            st.markdown("---")

            # --- 과목 선택 ---
            course_options = {
                f"{c['title']} [{c.get('level', '')}]": c["id"] for c in courses
            }
            selected_course_label = st.selectbox(
                "📘 과목 선택 (Select Course)",
                options=list(course_options.keys()),
                key="curriculum_course_select",
            )
            selected_course_id = course_options[selected_course_label]

            st.markdown("---")

            # --- 커리큘럼 데이터 로드 ---
            modules = get_curriculum_by_course(selected_course_id)
            student_progress = get_student_progress(selected_student_id)

            # 세트(Set) 컴프리헨션: 완료된 스텝 ID를 집합으로 저장
            # 집합을 사용하면 'in' 연산이 O(1)로 매우 빠릅니다.
            completed_step_ids = {
                p["step_id"]
                for p in student_progress
                if p["status"] == "completed"
            }

            # --- 진행 현황 요약 (Progress Summary) ---
            # sum() + 삼중 리스트 컴프리헨션으로 전체 스텝 수 계산
            total_steps = sum(len(m.get("steps", [])) for m in modules)
            completed_count = sum(
                1
                for m in modules
                for s in m.get("steps", [])
                if s["id"] in completed_step_ids
            )
            progress_pct = (completed_count / total_steps * 100) if total_steps > 0 else 0

            col_prog1, col_prog2, col_prog3 = st.columns(3)
            with col_prog1:
                st.metric("전체 스텝", f"{total_steps}개")
            with col_prog2:
                st.metric("완료 스텝", f"{completed_count}개")
            with col_prog3:
                st.metric("진행률", f"{progress_pct:.1f}%")

            # st.progress(): 진행률 바 표시 (0.0 ~ 1.0 사이 값)
            st.progress(progress_pct / 100)
            st.markdown("---")

            # --- 모듈별 아코디언 (Module Sections) ---
            if not modules:
                st.info("이 과목에 등록된 커리큘럼 모듈이 없습니다.")
            else:
                for module in modules:
                    module_steps = module.get("steps", [])
                    module_completed = sum(
                        1 for s in module_steps if s["id"] in completed_step_ids
                    )
                    module_total = len(module_steps)
                    module_pct = (
                        (module_completed / module_total * 100)
                        if module_total > 0
                        else 0
                    )

                    # 진행률에 따라 아이콘 변경 (조건부 아이콘)
                    if module_pct >= 100:
                        icon = "✅"
                    elif module_pct > 0:
                        icon = "🔄"
                    else:
                        icon = "📌"

                    with st.expander(
                        f"{icon} 모듈 {module['order_num']}: {module['title']} "
                        f"({module_completed}/{module_total} 완료, {module_pct:.0f}%)"
                    ):
                        # 모듈 메타데이터 표시
                        if module.get("description"):
                            st.markdown(f"**설명:** {module['description']}")
                        if module.get("estimated_minutes"):
                            st.markdown(
                                f"⏱️ 예상 소요시간: {module['estimated_minutes']}분"
                            )
                        if module.get("difficulty"):
                            st.markdown(f"📊 난이도: {module['difficulty']}")

                        st.markdown("---")

                        # 스텝별 표시 (Steps within Module)
                        if not module_steps:
                            st.info("이 모듈에 등록된 스텝이 없습니다.")
                        else:
                            for step in module_steps:
                                is_completed = step["id"] in completed_step_ids

                                # 완료 여부에 따른 아이콘
                                status_icon = "✅" if is_completed else "⬜"
                                st.markdown(
                                    f"### {status_icon} 스텝 {step['order_num']}: {step['title']}"
                                )

                                # 각종 스텝 정보 (조건부 표시)
                                if step.get("instruction"):
                                    st.markdown(
                                        f"**📖 지시사항:**\n\n{step['instruction']}"
                                    )

                                if step.get("code_example"):
                                    st.markdown("**💻 코드 예시:**")
                                    st.code(step["code_example"], language="python")

                                if step.get("expected_output"):
                                    st.markdown("**📤 예상 출력:**")
                                    st.code(step["expected_output"], language="text")

                                if step.get("hints"):
                                    with st.expander("💡 힌트 보기"):
                                        st.markdown(step["hints"])

                                if step.get("check_description"):
                                    # st.info()로 확인 사항 안내
                                    st.info(
                                        f"🔍 **확인:** {step['check_description']}"
                                    )

                                # 완료 버튼 (Complete Button)
                                if is_completed:
                                    st.success("✔️ 이 스텝은 이미 완료되었습니다.")
                                else:
                                    if st.button(
                                        "✅ 완료",
                                        key=f"complete_step_{step['id']}",
                                        use_container_width=True,
                                    ):
                                        success = update_student_progress(
                                            selected_student_id,
                                            step["id"],
                                            "completed",
                                        )
                                        if success:
                                            st.success("완료 처리되었습니다! 🎉")
                                            # 캐시 초기화: 데이터 변경사항 반영
                                            st.cache_data.clear()
                                            # st.rerun(): 페이지를 즉시 다시 실행
                                            # 완료 상태가 반영된 UI를 보여줌
                                            st.rerun()
                                        else:
                                            # st.error(): 빨간색 오류 메시지
                                            # 심각한 문제 발생 시 사용
                                            st.error(
                                                "저장 중 오류가 발생했습니다. 다시 시도해주세요."
                                            )

                                st.markdown("---")


# ===== 7. 학습 현황 페이지 (Learning Status Page) =====
elif page == "학습 현황":

    st.title("📊 학습 현황")
    st.markdown("전체 과목에 걸친 학습 진행 상황과 통계를 확인합니다.")

    courses = get_all_courses()
    students = get_all_students()

    if not courses or not students:
        st.info("데이터가 충분하지 않습니다. 과목과 학생을 먼저 등록해주세요.")
    else:
        # --- 전체 통계 계산 (Overall Statistics) ---
        all_course_stats = []
        total_modules_all = 0
        total_steps_all = 0
        total_completed_all = 0

        for course in courses:
            modules = get_curriculum_by_course(course["id"])
            course_total_steps = sum(len(m.get("steps", [])) for m in modules)
            course_module_count = len(modules)

            # 모든 학생의 완료 스텝 수 계산
            course_completed_steps = 0
            for student in students:
                progress = get_student_progress(student["id"])
                student_completed_ids = {
                    p["step_id"] for p in progress if p["status"] == "completed"
                }
                for module in modules:
                    for step in module.get("steps", []):
                        if step["id"] in student_completed_ids:
                            course_completed_steps += 1

            total_possible = course_total_steps * len(students) if students else 0
            course_pct = (
                (course_completed_steps / total_possible * 100)
                if total_possible > 0
                else 0
            )

            all_course_stats.append(
                {
                    "course": course,
                    "module_count": course_module_count,
                    "total_steps": course_total_steps,
                    "completed_steps": course_completed_steps,
                    "total_possible": total_possible,
                    "completion_pct": course_pct,
                }
            )

            total_modules_all += course_module_count
            total_steps_all += course_total_steps
            total_completed_all += course_completed_steps

        # --- KPI 카드 (KPI Summary) ---
        overall_pct = (
            (
                total_completed_all
                / (total_steps_all * len(students))
                * 100
            )
            if total_steps_all > 0 and students
            else 0
        )

        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric("전체 과목 수", f"{len(courses)}개")
        with kpi_col2:
            st.metric("전체 모듈 수", f"{total_modules_all}개")
        with kpi_col3:
            st.metric("전체 스텝 수", f"{total_steps_all}개")
        with kpi_col4:
            st.metric("전체 진행률", f"{overall_pct:.1f}%")

        st.progress(overall_pct / 100)
        st.markdown("---")

        # --- 과목별 진행 현황 (Progress by Course) ---
        st.subheader("📘 과목별 진행 현황")

        for stat in all_course_stats:
            course = stat["course"]
            with st.expander(
                f"📘 {course['title']} - 진행률 {stat['completion_pct']:.1f}% "
                f"({stat['completed_steps']}/{stat['total_possible']})"
            ):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("모듈 수", f"{stat['module_count']}개")
                with col_b:
                    st.metric("스텝 수", f"{stat['total_steps']}개")
                with col_c:
                    st.metric("완료 스텝", f"{stat['completed_steps']}")

                st.progress(stat["completion_pct"] / 100)

                # 모듈별 상세 (Module Details)
                modules = get_curriculum_by_course(course["id"])
                if modules:
                    st.markdown("**모듈별 상세:**")
                    for module in modules:
                        module_steps = module.get("steps", [])
                        module_total = len(module_steps)

                        module_completed = 0
                        for student in students:
                            progress = get_student_progress(student["id"])
                            student_completed_ids = {
                                p["step_id"]
                                for p in progress
                                if p["status"] == "completed"
                            }
                            for step in module_steps:
                                if step["id"] in student_completed_ids:
                                    module_completed += 1

                        module_possible = module_total * len(students) if students else 0
                        module_pct = (
                            (module_completed / module_possible * 100)
                            if module_possible > 0
                            else 0
                        )

                        st.markdown(
                            f"- **모듈 {module['order_num']}:** {module['title']} "
                            f"({module_completed}/{module_possible}, {module_pct:.0f}%)"
                        )
                        st.progress(module_pct / 100)

        st.markdown("---")

        # --- 학생별 진행 현황 (Progress by Student) ---
        st.subheader("👨‍🎓 학생별 진행 현황")

        student_stats = []
        for student in students:
            progress = get_student_progress(student["id"])
            completed_ids = {
                p["step_id"] for p in progress if p["status"] == "completed"
            }

            student_total = 0
            student_completed = 0
            for course in courses:
                modules = get_curriculum_by_course(course["id"])
                for module in modules:
                    for step in module.get("steps", []):
                        student_total += 1
                        if step["id"] in completed_ids:
                            student_completed += 1

            student_pct = (
                (student_completed / student_total * 100)
                if student_total > 0
                else 0
            )
            student_stats.append(
                {
                    "student": student,
                    "total": student_total,
                    "completed": student_completed,
                    "pct": student_pct,
                }
            )

        # 정렬: 진행률 높은 순 (내림차순)
        # sort()의 key 파라미터로 정렬 기준을 람다 함수로 지정합니다.
        # reverse=True: 내림차순 정렬
        student_stats.sort(key=lambda x: x["pct"], reverse=True)

        for stat in student_stats:
            student = stat["student"]
            st.markdown(
                f"**{student['name']}** ({student['email']}) - "
                f"{stat['completed']}/{stat['total']} 완료 ({stat['pct']:.1f}%)"
            )
            st.progress(stat["pct"] / 100)


# =====================================================================
# 6. 푸터 (Footer)
# =====================================================================
# 모든 페이지에서 공통으로 표시되는 푸터 영역입니다.
# HTML + CSS로 중앙 정렬된 회색 텍스트를 렌더링합니다.
# -----------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888;'>
        📚 교육용 Streamlit 대시보드 | Made with ❤️ for learning
    </div>
    """,
    unsafe_allow_html=True,
)
