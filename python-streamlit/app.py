"""
app.py - 교육용 Streamlit 대시보드 메인 애플리케이션
(Educational Streamlit Dashboard Main Application)

이 앱은 SQLite 데이터베이스에 연결하여 교육 관련 데이터를
시각화하고 관리하는 대시보드를 제공합니다.
(This app connects to a SQLite database to visualize and manage educational data.)
"""

import sys
import os

# 공유 DB 모듈 경로 추가 (Add shared DB module path)
# ../shared/db 디렉토리의 db_helper.py를 임포트하기 위해 sys.path에 추가
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
)

# ===== 페이지 설정 (Page Configuration) =====
# 레이아웃을 'wide'로 설정하여 넓은 화면 활용
st.set_page_config(
    page_title="교육 대시보드",  # 페이지 제목 (Page title)
    page_icon="📚",  # 페이지 아이콘 (Page icon)
    layout="wide",  # 넓은 레이아웃 (Wide layout)
    initial_sidebar_state="expanded",  # 사이드바 펼침 상태 (Sidebar expanded)
)

# ===== 스타일 설정 (Style Configuration) =====
# KPI 카드를 위한 커스텀 CSS
st.markdown("""
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
""", unsafe_allow_html=True)


# ===== 헬퍼 함수 (Helper Functions) =====
@st.cache_data(ttl=60)  # 60초 캐시 (60-second cache)
def load_kpi_data():
    """KPI 데이터를 로드합니다 (Load KPI data)"""
    return {
        "students": get_student_count(),
        "courses": get_course_count(),
        "submissions": get_submission_count(),
        "avg_score": get_avg_score(),
    }


@st.cache_data(ttl=60)
def load_students_df():
    """학생 데이터를 DataFrame으로 반환합니다 (Return students as DataFrame)"""
    students = get_all_students()
    if students:
        df = pd.DataFrame([dict(s) for s in students])
        return df
    return pd.DataFrame()


@st.cache_data(ttl=60)
def load_courses_df():
    """강좌 데이터를 DataFrame으로 반환합니다 (Return courses as DataFrame)"""
    courses = get_all_courses()
    if courses:
        df = pd.DataFrame([dict(c) for c in courses])
        return df
    return pd.DataFrame()


@st.cache_data(ttl=60)
def load_submissions_df():
    """제출 데이터를 DataFrame으로 반환합니다 (Return submissions as DataFrame)"""
    submissions = get_all_submissions()
    if submissions:
        df = pd.DataFrame([dict(s) for s in submissions])
        return df
    return pd.DataFrame()


@st.cache_data(ttl=60)
def load_lessons_by_course():
    """강좌별 수업 데이터를 반환합니다 (Return lessons grouped by course)"""
    courses = get_all_courses()
    result = {}
    for course in courses:
        lessons = get_lessons_by_course(course["id"])
        result[course["title"]] = [dict(l) for l in lessons] if lessons else []
    return result


# ===== 사이드바 네비게이션 (Sidebar Navigation) =====
st.sidebar.title("📚 교육 대시보드")  # 사이드바 제목
st.sidebar.markdown("---")  # 구분선

# 페이지 선택 라디오 버튼
page = st.sidebar.radio(
    "페이지 선택 (Select Page)",  # 라벨
    ["개요", "학생 관리", "과목 현황", "강의 내용", "과제 제출"],  # 옵션 목록
    index=0,  # 기본 선택 (Default selection)
)

st.sidebar.markdown("---")
st.sidebar.info("💡 이 앱은 Streamlit 교육용으로 제작되었습니다.\n(This app is built for Streamlit education.)")

# ===== 메인 콘텐츠 영역 (Main Content Area) =====

# ===== 1. 개요 페이지 (Overview Page) =====
if page == "개요":
    st.title("📊 대시보드 개요")  # 페이지 제목
    st.markdown("교육 데이터의 전체적인 현황을 한눈에 확인합니다.")

    # KPI 카드 섹션 (KPI Cards Section)
    kpi = load_kpi_data()

    # 4개의 컬럼으로 KPI 카드 배치
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['students']}</div>
            <div class="kpi-label">👨‍🎓 총 학생수</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['courses']}</div>
            <div class="kpi-label">📖 과목수</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['submissions']}</div>
            <div class="kpi-label">📝 제출수</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{kpi['avg_score']}</div>
            <div class="kpi-label">⭐ 평균 점수</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 차트 영역 (Charts Section) - 2개 컬럼
    col_chart1, col_chart2 = st.columns(2)

    # 강좌별 학생 수 바 차트 (Bar Chart: Students per Course)
    with col_chart1:
        st.subheader("📊 강좌별 학생 수")  # 차트 제목
        course_data = get_students_by_course()
        if course_data:
            df_courses = pd.DataFrame([dict(c) for c in course_data])
            chart = alt.Chart(df_courses).mark_bar().encode(
                x=alt.X("title:N", title="강좌명", sort="-y"),  # X축: 강좌명
                y=alt.Y("student_count:Q", title="학생 수"),  # Y축: 학생 수
                color=alt.Color("title:N", legend=None),  # 색상
                tooltip=["title", "student_count"],  # 툴팁
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # 학점 분포 파이 차트 (Pie Chart: Grade Distribution)
    with col_chart2:
        st.subheader("🥧 학점 분포")  # 차트 제목
        grade_data = get_grade_distribution()
        if grade_data:
            df_grades = pd.DataFrame([dict(g) for g in grade_data])
            chart = alt.Chart(df_grades).mark_arc().encode(
                theta=alt.Theta("count:Q"),  # 각도 (크기)
                color=alt.Color("grade:N", title="학점"),  # 색상
                tooltip=["grade", "count"],  # 툴팁
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # 제출 타임라인 라인 차트 (Line Chart: Submissions Over Time)
    st.markdown("---")
    st.subheader("📈 월별 제출 추이")  # 차트 제목
    timeline_data = get_submissions_timeline()
    if timeline_data:
        df_timeline = pd.DataFrame([dict(t) for t in timeline_data])
        chart = alt.Chart(df_timeline).mark_line(point=True).encode(
            x=alt.X("month:N", title="월"),  # X축: 월
            y=alt.Y("count:Q", title="제출 수"),  # Y축: 제출 수
            tooltip=["month", "count"],  # 툴팁
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")


# ===== 2. 학생 관리 페이지 (Student Management Page) =====
elif page == "학생 관리":
    st.title("👨‍🎓 학생 관리")  # 페이지 제목
    st.markdown("학생 정보를 조회하고 검색합니다.")

    # 검색 기능 (Search Function)
    search_query = st.text_input(
        "🔍 학생 검색 (이름 또는 이메일)",  # 라벨
        placeholder="예: 김민수",  # 플레이스홀더
    )

    # 검색어가 있으면 검색 결과, 없으면 전체 목록
    if search_query:
        # 검색 결과 표시 (Display search results)
        students = search_students(search_query)
        if students:
            df = pd.DataFrame([dict(s) for s in students])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.success(f"{len(df)}명의 학생을 찾았습니다.")  # 검색 결과 수
        else:
            st.warning("검색 결과가 없습니다.")
    else:
        # 전체 학생 목록 표시 (Display all students)
        df_students = load_students_df()
        if not df_students.empty:
            # 컬럼 이름을 한국어로 변경 (Rename columns to Korean)
            df_display = df_students.rename(columns={
                "id": "ID",
                "name": "이름",
                "email": "이메일",
                "enrolled_date": "등록일",
                "grade": "학점",
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # 통계 요약 (Summary Statistics)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("전체 학생 수", len(df_students))
            with col2:
                grade_counts = df_students["grade"].value_counts()
                most_common = grade_counts.index[0] if len(grade_counts) > 0 else "N/A"
                st.metric("가장 많은 학점", most_common)
        else:
            st.info("등록된 학생이 없습니다.")


# ===== 3. 과목 현황 페이지 (Courses Status Page) =====
elif page == "과목 현황":
    st.title("📖 과목 현황")  # 페이지 제목
    st.markdown("개설된 강좌의 현황을 확인합니다.")

    courses = get_all_courses()
    if courses:
        # 강좌를 카드 형태로 표시 (Display courses as cards)
        # 한 줄에 2개씩 배치
        for i in range(0, len(courses), 2):
            col1, col2 = st.columns(2)
            for j, col in enumerate([col1, col2]):
                if i + j < len(courses):
                    course = courses[i + j]
                    with col:
                        # 카드 스타일로 강좌 정보 표시
                        st.markdown(f"""
                        ### 📘 {course['title']}
                        - **강사:** {course['instructor']}
                        - **카테고리:** {course['category']}
                        - **설명:** {course['description']}
                        """)
                        st.markdown("---")
    else:
        st.info("등록된 과목이 없습니다.")


# ===== 4. 강의 내용 페이지 (Lessons Content Page) =====
elif page == "강의 내용":
    st.title("📚 강의 내용")  # 페이지 제목
    st.markdown("강좌별 수업 내용을 확인합니다.")

    lessons_by_course = load_lessons_by_course()

    if lessons_by_course:
        # 강좌별로 확장/접기 가능한 섹션 (Expandable sections by course)
        for course_title, lessons in lessons_by_course.items():
            # expander 위젯으로 강좌 그룹화
            with st.expander(f"📘 {course_title} ({len(lessons)}개 수업)"):
                if lessons:
                    for lesson in lessons:
                        # 수업 정보 표시
                        st.markdown(f"""
                        **{lesson['order_num']}. {lesson['title']}**
                        > {lesson['content']}
                        """)
                        st.markdown("")  # 간격 추가
                else:
                    st.info("등록된 수업이 없습니다.")
    else:
        st.info("등록된 강의가 없습니다.")


# ===== 5. 과제 제출 페이지 (Submissions Page) =====
elif page == "과제 제출":
    st.title("📝 과제 제출")  # 페이지 제목
    st.markdown("학생들의 과제 제출 현황을 확인합니다.")

    df_submissions = load_submissions_df()

    if not df_submissions.empty:
        # 제출 상태 필터 (Filter by status)
        status_filter = st.multiselect(
            "상태 필터",
            options=df_submissions["status"].unique().tolist(),
            default=df_submissions["status"].unique().tolist(),
        )

        # 필터 적용 (Apply filter)
        if status_filter:
            df_filtered = df_submissions[df_submissions["status"].isin(status_filter)]
        else:
            df_filtered = df_submissions

        # 제출 테이블 표시 (Display submission table)
        st.subheader("📋 제출 목록")
        df_display = df_filtered.rename(columns={
            "id": "ID",
            "student_name": "학생명",
            "lesson_title": "수업명",
            "course_title": "과목명",
            "score": "점수",
            "submitted_at": "제출일시",
            "status": "상태",
        })
        st.dataframe(
            df_display[["ID", "학생명", "과목명", "수업명", "점수", "제출일시", "상태"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        # 코드 미리보기 섹션 (Code Preview Section)
        st.subheader("💻 코드 미리보기")

        # 제출 선택 드롭다운
        submission_options = {
            f"#{row['id']} - {row['student_name']} ({row['lesson_title']})": row["id"]
            for _, row in df_filtered.iterrows()
        }

        selected = st.selectbox(
            "제출을 선택하세요",
            options=list(submission_options.keys()),
        )

        if selected:
            # 선택한 제출의 코드 표시 (Display selected submission's code)
            sub_id = submission_options[selected]
            sub_row = df_submissions[df_submissions["id"] == sub_id].iloc[0]

            col1, col2 = st.columns([2, 1])

            with col1:
                # 코드 블록으로 표시
                st.code(sub_row["code"], language="python")

            with col2:
                # 제출 정보 표시
                st.metric("점수", f"{sub_row['score']}점")
                st.metric("상태", sub_row["status"])
                st.metric("학생", sub_row["student_name"])
                st.metric("수업", sub_row["lesson_title"])
                st.metric("과목", sub_row["course_title"])
                st.text(f"제출일시: {sub_row['submitted_at']}")

    else:
        st.info("제출된 과제가 없습니다.")


# ===== 푸터 (Footer) =====
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888;'>
        📚 교육용 Streamlit 대시보드 | Made with ❤️ for learning
    </div>
    """,
    unsafe_allow_html=True,
)
