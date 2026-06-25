"""
코드교육 � 대시보드 메인 애플리케이션
Flask 기반 학습 관리 시스템 대시보드입니다.
"""

import sys
import os

# 공유 데이터베이스 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared", "db"))

from flask import Flask, render_template, request, jsonify
from db_helper import (
    get_all_students,
    get_all_courses,
    get_enrollments_by_course,
    get_lessons_by_course,
    get_submissions_summary,
    get_student_performance,
    get_course_statistics,
)

app = Flask(__name__)


@app.route("/")
def dashboard():
    """메인 대시보드 페이지 - KPI 카드와 차트를 �시합니다."""
    students = get_all_students()
    courses = get_all_courses()
    course_stats = get_course_statistics()
    submissions_summary = get_submissions_summary()

    # KPI 데이터 계산
    total_students = len(students)
    total_courses = len(courses)
    total_lessons = sum(c["lesson_count"] for c in course_stats)
    total_submissions = sum(c["total_submissions"] for c in course_stats)

    # 차트 데이터: 과목별 학생 수 (bar chart)
    course_labels = [c["title"] for c in course_stats]
    course_student_counts = [c["student_count"] for c in course_stats]

    # 차트 데이터: 성적 분포 (pie chart) - 학생 평균 점수 기반
    student_perf = get_student_performance()
    grade_a = sum(1 for s in student_perf if s["avg_score"] and s["avg_score"] >= 90)
    grade_b = sum(1 for s in student_perf if s["avg_score"] and 80 <= s["avg_score"] < 90)
    grade_c = sum(1 for s in student_perf if s["avg_score"] and 70 <= s["avg_score"] < 80)
    grade_d = sum(1 for s in student_perf if s["avg_score"] and 60 <= s["avg_score"] < 70)
    grade_f = sum(1 for s in student_perf if s["avg_score"] and s["avg_score"] < 60)
    grade_none = sum(1 for s in student_perf if s["avg_score"] is None)

    # 월별 제출 데이터 (line chart) - 제출 요약을 시계열로 변환
    # submissions_summary에는 월별 데이터가 없으므로 과목별 제출 건수를 시�레이션
    monthly_labels = ["1월", "2월", "3월", "4월", "5월", "6월"]
    # 실제 데이터에서 월별 제출 건수를 집계하려면 �리가 필요하므로 기본값 사용
    monthly_submissions = [0] * 6  # 기본값

    kpi = {
        "total_students": total_students,
        "total_courses": total_courses,
        "total_lessons": total_lessons,
        "total_submissions": total_submissions,
    }

    return render_template(
        "index.html",
        kpi=kpi,
        course_labels=course_labels,
        course_student_counts=course_student_counts,
        grade_distribution=[grade_a, grade_b, grade_c, grade_d, grade_f, grade_none],
        monthly_labels=monthly_labels,
        monthly_submissions=monthly_submissions,
        submissions_summary=submissions_summary,
    )


@app.route("/students")
def students():
    """학생 목록 페이지 - �색 � 성과 요약을 제공합니다."""
    search_query = request.args.get("search", "").strip()
    student_perf = get_student_performance()

    # 검색 필터링
    if search_query:
        student_perf = [
            s
            for s in student_perf
            if search_query.lower() in s["name"].lower()
            or search_query.lower() in s.get("email", "").lower()
        ]

    return render_template(
        "students.html",
        students=student_perf,
        search_query=search_query,
    )


@app.route("/courses")
def courses():
    """과목 목록 페이지 - 과목별 통계 카드를 표시합니다."""
    course_stats = get_course_statistics()
    return render_template("courses.html", courses=course_stats)


@app.route("/lessons/<int:course_id>")
def lessons(course_id):
    """강의 목록 페이지 - 특정 과목의 강의를 �시합니다."""
    course_lessons = get_lessons_by_course(course_id)
    courses = get_all_courses()
    # 현재 과목 정보 �기
    current_course = next((c for c in courses if c["id"] == course_id), None)

    # 모든 과목 목록 (필터용)
    all_courses = courses

    return render_template(
        "lessons.html",
        lessons=course_lessons,
        course=current_course,
        all_courses=all_courses,
        selected_course_id=course_id,
    )


@app.route("/submissions")
def submissions():
    """제출 목록 페이지 - 코드 미리보기, 점수, 피드백을 표시합니다."""
    submissions_summary = get_submissions_summary()
    return render_template("submissions.html", submissions=submissions_summary)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
