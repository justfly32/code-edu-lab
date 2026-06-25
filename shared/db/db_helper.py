"""
공유 SQLite 데이터베이스 헬퍼 모듈
code-edu-lab 프로젝트에서 공통으로 사용되는 데이터베이스 유틸리티입니다.
"""

import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edu.db")


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    데이터베이스 연결을 반환합니다.
    
    Args:
        db_path: DB 파일 경로 (선택사항, 기본값은 모듈에 설정된 경로)
    
    Returns:
        sqlite3.Connection 객체 (foreign_keys 활성화, Row 팩토리 설정)
    """
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def get_all_students() -> list[dict]:
    """모든 학생 목록을 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM students ORDER BY id;")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_courses() -> list[dict]:
    """모든 과목 목록을 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM courses ORDER BY id;")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_enrollments_by_course(course_id: int) -> list[dict]:
    """
    특정 과목의 수강 학생 목록을 반환합니다.
    
    Args:
        course_id: 과목 ID
    
    Returns:
        학생 정보 및 성적이 포함된 수강 목록
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT e.id, e.student_id, s.name AS student_name, s.email,
               e.enrolled_at, e.grade
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE e.course_id = ?
        ORDER BY s.name;
        """,
        (course_id,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_lessons_by_course(course_id: int) -> list[dict]:
    """
    특정 과목의 강의 목록을 반환합니다.
    
    Args:
        course_id: 과목 ID
    
    Returns:
        강의 목록 (순서대로 정렬)
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT id, course_id, title, content, order_num, duration_min
        FROM lessons
        WHERE course_id = ?
        ORDER BY order_num;
        """,
        (course_id,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_submissions_summary() -> list[dict]:
    """
    제출 요약 정보를 반환합니다.
    
    Returns:
        각 과목별 제출 건수, 평균 점수, 최고 점수 요약
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT c.title AS course_title,
               COUNT(s.id) AS total_submissions,
               ROUND(AVG(s.score), 1) AS avg_score,
               MAX(s.score) AS max_score,
               MIN(s.score) AS min_score
        FROM submissions s
        JOIN lessons l ON s.lesson_id = l.id
        JOIN courses c ON l.course_id = c.id
        GROUP BY c.id
        ORDER BY c.title;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_student_performance() -> list[dict]:
    """
    학생별 성적 성과를 반환합니다.
    
    Returns:
        학생별 제출 건수, 평균 점수, 수강 과목 수
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT st.id, st.name, st.email,
               COUNT(DISTINCT s.id) AS total_submissions,
               ROUND(AVG(s.score), 1) AS avg_score,
               COUNT(DISTINCT e.course_id) AS enrolled_courses
        FROM students st
        LEFT JOIN submissions s ON st.id = s.student_id
        LEFT JOIN enrollments e ON st.id = e.student_id
        GROUP BY st.id
        ORDER BY avg_score DESC;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_course_statistics() -> list[dict]:
    """
    과목별 통계 정보를 반환합니다.
    
    Returns:
        과목별 학생 수, 강의 수, 제출 건수, 평균 점수
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT c.id, c.title, c.instructor, c.level, c.student_count,
               COUNT(DISTINCT l.id) AS lesson_count,
               COUNT(DISTINCT s.id) AS total_submissions,
               ROUND(AVG(s.score), 1) AS avg_submission_score
        FROM courses c
        LEFT JOIN lessons l ON c.id = l.course_id
        LEFT JOIN submissions s ON l.id = s.lesson_id
        GROUP BY c.id
        ORDER BY c.id;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    import json

    print("=== 코드교육 랩 데이터베이스 헬퍼 ===\n")

    print("📚 전체 학생:")
    for s in get_all_students():
        print(f"  {s['id']}. {s['name']} ({s['email']}) - 수강 {s['course_count']}과목")

    print("\n📖 전체 과목:")
    for c in get_all_courses():
        print(f"  {c['id']}. [{c['level']}] {c['title']} - 강사: {c['instructor']} (수강생: {c['student_count']}명)")

    print("\n📊 과목별 통계:")
    for stat in get_course_statistics():
        print(f"  {stat['title']}: 수강생 {stat['student_count']}명, 강의 {stat['lesson_count']}개, 제출 {stat['total_submissions']}건, 평균 {stat['avg_submission_score']}점")

    print("\n🏆 학생별 성과:")
    for p in get_student_performance():
        print(f"  {p['name']}: 제출 {p['total_submissions']}건, 평균 {p['avg_score']}점, 수강 {p['enrolled_courses']}과목")

    print("\n📝 제출 요약:")
    for s in get_submissions_summary():
        print(f"  {s['course_title']}: {s['total_submissions']}건, 평균 {s['avg_score']}점 (최고: {s['max_score']}, 최저: {s['min_score']})")
