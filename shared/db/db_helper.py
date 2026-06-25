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


def get_curriculum_by_course(course_id: int) -> list[dict]:
    """
    특정 과목의 커리큘럼(모듈 + 스텝)을 계층적으로 반환합니다.
    
    Args:
        course_id: 과목 ID
    
    Returns:
        모듈 목록 (각 모듈에 steps 키로 스텝 리스트 포함)
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT id, title, description, order_num, estimated_minutes, difficulty
        FROM curriculum_modules
        WHERE course_id = ?
        ORDER BY order_num;
        """,
        (course_id,),
    )
    modules = [dict(row) for row in cursor.fetchall()]

    for module in modules:
        cursor = conn.execute(
            """
            SELECT id, title, instruction, code_example, expected_output,
                   hints, check_query, check_description, order_num
            FROM curriculum_steps
            WHERE module_id = ?
            ORDER BY order_num;
            """,
            (module["id"],),
        )
        module["steps"] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return modules


def get_student_progress(student_id: int) -> list[dict]:
    """
    학생의 진행 상황을 스텝 상세 정보와 함께 반환합니다.
    
    Args:
        student_id: 학생 ID
    
    Returns:
        진행 상황 목록 (스텝 및 모듈 정보 포함)
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT sp.id, sp.step_id, sp.status, sp.completed_at, sp.attempts,
               cs.title AS step_title, cs.order_num AS step_order,
               cm.id AS module_id, cm.title AS module_title
        FROM student_progress sp
        JOIN curriculum_steps cs ON sp.step_id = cs.id
        JOIN curriculum_modules cm ON cs.module_id = cm.id
        WHERE sp.student_id = ?
        ORDER BY cm.order_num, cs.order_num;
        """,
        (student_id,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def update_student_progress(student_id: int, step_id: int, status: str) -> bool:
    """
    학생의 진행 상황을 업데이트합니다. 기록이 없으면 새로 생성합니다.
    
    Args:
        student_id: 학생 ID
        step_id: 스텝 ID
        status: 진행 상태 ('not_started', 'in_progress', 'completed')
    
    Returns:
        성공 여부
    """
    conn = get_db_connection()
    try:
        # Check if record exists
        cursor = conn.execute(
            "SELECT id, attempts FROM student_progress WHERE student_id = ? AND step_id = ?;",
            (student_id, step_id),
        )
        existing = cursor.fetchone()

        if existing:
            # Update existing record
            completed_at = "datetime('now')" if status == "completed" else "NULL"
            conn.execute(
                f"""
                UPDATE student_progress
                SET status = ?,
                    completed_at = {completed_at},
                    attempts = attempts + 1
                WHERE student_id = ? AND step_id = ?;
                """,
                (status, student_id, step_id),
            )
        else:
            # Insert new record
            completed_at = "datetime('now')" if status == "completed" else "NULL"
            conn.execute(
                f"""
                INSERT INTO student_progress (student_id, step_id, status, completed_at, attempts)
                VALUES (?, ?, ?, {completed_at}, 1);
                """,
                (student_id, step_id, status),
            )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Error updating progress: {e}")
        return False


def get_next_step(student_id: int, course_id: int) -> Optional[dict]:
    """
    학생이 다음에 완료해야 할 스텝을 반환합니다.
    
    Args:
        student_id: 학생 ID
        course_id: 과목 ID
    
    Returns:
        다음 미완료 스텝 정보 (모듈 정보 포함), 모든 완료 시 None
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT cs.id AS step_id, cs.title AS step_title, cs.order_num AS step_order,
               cm.id AS module_id, cm.title AS module_title, cm.order_num AS module_order
        FROM curriculum_steps cs
        JOIN curriculum_modules cm ON cs.module_id = cm.id
        WHERE cm.course_id = ?
          AND cs.id NOT IN (
              SELECT step_id FROM student_progress
              WHERE student_id = ? AND status = 'completed'
          )
        ORDER BY cm.order_num, cs.order_num
        LIMIT 1;
        """,
        (course_id, student_id),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ===== 추가 함수 (Streamlit 대시보드용) =====

def get_all_submissions() -> list[dict]:
    """
    모든 제출 정보를 상세 정보와 함께 반환합니다.
    
    Returns:
        제출 목록 (학생명, 수업명, 과목명, 코드, 점수, 제출일시, 상태 포함)
    """
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT s.id, st.name AS student_name, l.title AS lesson_title,
               c.title AS course_title, s.code_text AS code, s.score,
               s.submitted_at,
               CASE
                   WHEN s.score >= 90 THEN '우수'
                   WHEN s.score >= 70 THEN '통과'
                   ELSE '미흡'
               END AS status
        FROM submissions s
        JOIN students st ON s.student_id = st.id
        JOIN lessons l ON s.lesson_id = l.id
        JOIN courses c ON l.course_id = c.id
        ORDER BY s.submitted_at DESC;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_student_count() -> int:
    """전체 학생 수를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(*) AS cnt FROM students;")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_course_count() -> int:
    """전체 과목 수를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(*) AS cnt FROM courses;")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_submission_count() -> int:
    """전체 제출 수를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(*) AS cnt FROM submissions;")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_avg_score() -> float:
    """전체 평균 점수를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute("SELECT ROUND(AVG(score), 1) AS avg FROM submissions;")
    row = cursor.fetchone()
    conn.close()
    return row["avg"] if row and row["avg"] is not None else 0.0


def get_students_by_course() -> list[dict]:
    """과목별 학생 수를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT c.title AS title, COUNT(e.student_id) AS student_count
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id
        ORDER BY c.id;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_grade_distribution() -> list[dict]:
    """학점 분포를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT grade, COUNT(*) AS count
        FROM enrollments
        WHERE grade IS NOT NULL
        GROUP BY grade
        ORDER BY grade;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_submissions_timeline() -> list[dict]:
    """월별 제출 추이를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT strftime('%Y-%m', submitted_at) AS month, COUNT(*) AS count
        FROM submissions
        GROUP BY month
        ORDER BY month;
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def search_students(query: str) -> list[dict]:
    """이름 또는 이메일로 학생을 검색합니다."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT * FROM students
        WHERE name LIKE ? OR email LIKE ?
        ORDER BY name;
        """,
        (f"%{query}%", f"%{query}%"),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_lessons() -> list[dict]:
    """모든 수업 정보를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT l.*, c.title AS course_title
        FROM lessons l
        JOIN courses c ON l.course_id = c.id
        ORDER BY c.id, l.order_num;
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
