"""
==============================================================================
코드교육 랩 (Code Education Lab) — Flask 메인 애플리케이션
==============================================================================

이 파일은 Flask 기반 학습 관리 시스템(LMS) 대시보드의 메인 애플리케이션입니다.
학생, 과목, 강의, 제출, 커리큘럼 진행 상황을 관리하는 웹 서버의 진입점(entry point)입니다.

전체 구조 개요 (Route / Template / DB 연결 방식):
──────────────────────────────────────────────────────────
1. 라우트(Route) 구조:
   ┌─────────────────────────────────────────────────────────────┐
   │  GET  /                           → index.html (대시보드)   │
   │  GET  /students                   → students.html (학생목록)│
   │  GET  /courses                    → courses.html (과목목록) │
   │  GET  /lessons/<course_id>        → lessons.html (강의목록) │
   │  GET  /submissions                → submissions.html (제출)  │
   │  GET  /progress                   → progress.html (진행률)   │
   │  GET  /curriculum                 → curriculum.html (커리큘럼)│
   │  GET  /curriculum/<course_id>     → curriculum_detail.html   │
   │  GET  /curriculum/<course_id>/step/<step_id>                │
   │                                  → curriculum_step.html      │
   │  POST /curriculum/<course_id>/step/<step_id>/complete       │
   │                                  → (완료처리 API)             │
   └─────────────────────────────────────────────────────────────┘

2. 템플릿(Template) 엔진: Jinja2 (Flask 내장)
   - Flask는 기본적으로 'templates/' 폴더에서 HTML 템플릿을 찾습니다.
   - render_template('이름.html', 변수=값) 으로 템플릿에 데이터를 전달합니다.
   - 템플릿 내에서 {{ 변수 }} 로 데이터를 출력하고,
     {% for item in list %} ... {% endfor %} 로 반복문을 사용합니다.

3. 데이터베이스(DB) 연결 방식:
   - 첫 번째 방식 (초기 헬퍼 함수들): db_helper 모듈을 통해 간접 접근
     → shared/db/db_helper.py 에 정의된 get_all_students(), get_all_courses() 등 사용
   - 두 번째 방식 (커리큘럼 모듈): 직접 SQLite3 연결
     → get_db_connection() 함수로 edu.db 파일에 직접 SQL 쿼리 실행
   - 두 방식 모두 동일한 SQLite 파일(shared/db/edu.db)을 사용합니다.
     첫 번째 방식은 db_helper의 추상화 계층을 통해, 두 번째 방식은 직접 접근합니다.

개발 환경:
  - Python 3.x, Flask
  - SQLite3 (파일 기반 DB, 서버 설치 불필요)
  - 실행: python app.py (http://localhost:5000)
"""

# ============================================================
# 표준 라이브러리 임포트 (Standard Library Imports)
# ============================================================
import sys  # sys.path 조작 등 시스템 관련 기능
import os   # 파일 경로 조작, 환경 변수 등 OS 기능


# ============================================================
# sys.path.insert()로 공유 DB 모듈 경로 추가하기
# ============================================================
#
# ■ 왜 필요한가?
#   이 Flask 앱은 'shared/db/' 디렉토리에 있는 db_helper.py 모듈을 사용합니다.
#   그런데 db_helper.py는 이 app.py와 같은 디렉토리에 있지 않고,
#   상대 경로로 '../shared/db/' 에 위치합니다.
#   파이썬은 기본적으로 sys.path(모듈 검색 경로 리스트)에 등록된
#   디렉토리만 import할 수 있습니다.
#
# ■ sys.path.insert(0, ...) 의 원리:
#   sys.path는 파이썬이 import 문을 만났을 때 모듈을 찾아보는
#   디렉토리 목록입니다. 순서대로 검색하며 처음 찾은 것을 사용합니다.
#   insert(0, 경로)는 이 리스트의 맨 앞(인덱스 0)에 경로를 추가합니다.
#   맨 앞에 넣는 이유는 같은 이름의 모듈이 다른 곳에 있을 때
#   우리가 원하는 모듈이 먼저 발견되도록 하기 위해서입니다.
#
# ■ os.path.join(os.path.dirname(__file__), "..", "shared", "db") 설명:
#   - __file__      : 현재 이 파일(app.py)의 절대 경로
#   - os.path.dirname() : 파일의 부모 디렉토리 경로
#   - ".."          : 한 단계 상위 디렉토리
#   - "shared", "db": 하위 디렉토리
#   → 최종 결과: /Users/.../code-edu-lab/python-flask/../shared/db/
#     즉, /Users/.../code-edu-lab/shared/db/ (정규화된 경로)
#
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "shared", "db"),
)

# ============================================================
# Flask 및 데이터베이스 헬퍼 모듈 임포트
# ============================================================

# Flask 핵심 컴포넌트들:
#   Flask          : 앱 인스턴스를 생성하는 메인 클래스
#   render_template: Jinja2 템플릿을 렌더링하여 HTML 응답을 생성
#   request        : 현재 HTTP 요청의 데이터(폼, 쿼리 파라미터 등)에 접근
#   jsonify        : 파이썬 dict/list를 JSON 응답으로 변환
#   redirect       : 다른 URL로 리다이렉트(301/302) 응답 생성
#   url_for        : 라우트 함수 이름으로 URL을 역으로 생성
#
from flask import Flask, render_template, request, jsonify, redirect, url_for

# db_helper 모듈에서 필요한 함수들을 임포트합니다.
# 이 함수들은 shared/db/ 디렉토리의 SQLite 데이터베이스(edu.db)와 통신합니다.
# 각 함수의 반환값은 dict 또는 list[dict] 형태입니다.
from db_helper import (
    get_all_students,           # 모든 학생 정보 반환
    get_all_courses,            # 모든 과목 정보 반환
    get_enrollments_by_course,  # 특정 과목의 수강생 목록 반환
    get_lessons_by_course,      # 특정 과목의 강의(레슨) 목록 반환
    get_submissions_summary,    # 모든 제출 정보 요약 반환
    get_student_performance,    # 학생별 평균 성적/성과 데이터 반환
    get_course_statistics,      # 과목별 통계(학생수, 제출수 등) 반환
)


# ============================================================
# 진행률 추적을 위한 전역 변수 (Global progress tracker)
# ============================================================
#
# ⚠️ _completed_steps = set()   ← 주의사항 (한계점 설명)
# ────────────────────────────────────────────────────────
# 이 전역 변수는 현재 프로세스가 실행되는 동안만 유지되는
# 메모리 내(in-memory) 세트(set)입니다.
#
# ■ 현재의 한계 (왜 실제 서비스에 적합하지 않은가):
#   1. 휘발성(Volatile):
#      서버가 재시작되거나 코드가 리로드되면 모든 데이터가 사라집니다.
#   2. 프로세스 격리 문제:
#      Gunicorn/uWSGI 등으로 멀티 프로세스로 실행하면 각 프로세스가
#      각자의 _completed_steps를 가지고 있어 데이터가 불일치합니다.
#   3. 사용자 구분 불가:
#      모든 사용자가 하나의 세트를 공유하므로 사용자별 진행률을
#      구분할 수 없습니다. 지금은 개발/데모 목적으로만 사용됩니다.
#
# ■ 실제 서비스에서는 무엇을 사용해야 하는가:
#   - 관계형 데이터베이스 (PostgreSQL, MySQL)
#     → student_progress 테이블: (user_id, step_id, completed_at, ...)
#   - Redis / Memcached (인메모리 캐시)
#     → Set 자료구조 활용: "user:42:completed_steps" = {step1, step2, ...}
#   - Flask 세션 (클라이언트 측 쿠키 기반)
#     → 간단한 앱에 적합, 하지만 보안/크기 제한이 있음
#
_completed_steps = set()


# ============================================================
# 헬퍼 함수 섹션 1: 초기 커리큘럼 헬퍼 (db_helper 기반)
# ============================================================
#
# 아래 함수들은 db_helper 모듈의 함수들을 호출하여
# 커리큘럼 개요, 모듈 상세, 스텝 상세 정보를 구성합니다.
# 이들은 "레슨(lesson)" 단위로 동작하며, 데이터는 db_helper → SQLite 로 흐릅니다.


def get_curriculum_overview():
    """
    [커리큘럼 개요 조회 함수]
    모든 과목의 개요 정보를 반환합니다.
    각 과목별로 과목명, 강사, 설명, 난이도, 모듈(강의) 수,
    전체 스텝 수, 완료 스텝 수, 완료율(%)을 포함합니다.

    Returns:
        list[dict]: 과목별 커리큘럼 개요 정보 리스트.
                    예: [{"id": 1, "title": "파이썬 기초", "module_count": 5, ...}, ...]

    동작 단계:
        1. get_all_courses()로 모든 과목 정보를 조회한다.
        2. 각 과목별로 get_lessons_by_course()로 강의 목록을 조회한다.
        3. 각 강의의 id가 _completed_steps에 있는지 확인하여 완료 여부를 판단한다.
        4. 완료율을 계산하고 각 과목의 개요 정보를 딕셔너리로 구성한다.
        5. 모든 과목의 개요 정보를 리스트에 담아 반환한다.

    Jinja2 템플릿에서의 사용:
        {% for course in overview %}
            {{ course.title }} - 완료율: {{ course.completion_percentage }}%
        {% endfor %}
    """
    # 1단계: 모든 과목 정보 조회
    # get_all_courses()는 shared/db/edu.db의 courses 테이블을 조회하여
    # 각 과목의 id, title, instructor, description, level을 반환합니다.
    courses = get_all_courses()

    # 2단계: 각 과목에 대해 강의 목록 및 완료율 계산
    overview = []  # 결과를 저장할 빈 리스트

    for course in courses:
        # course가 딕셔너리라고 가정: {"id": 1, "title": "파이썬 기초", ...}
        lessons = get_lessons_by_course(course["id"])  # course id로 강의 조회
        total_steps = len(lessons)  # 전체 강의 수 = 스텝 수

        # 완료된 스텝 수 계산
        # _completed_steps 세트에 강의(lesson)의 id가 존재하는지 확인합니다.
        # 존재하면 이미 완료한 강의로 간주합니다.
        completed_count = sum(
            1 for lesson in lessons if lesson["id"] in _completed_steps
        )

        # 완료율 계산 (소수점 첫째 자리까지 반올림)
        # total_steps가 0이면 0으로 처리 (ZeroDivisionError 방지)
        completion_pct = (
            round((completed_count / total_steps * 100), 1) if total_steps > 0 else 0
        )

        # 3단계: 과목별 개요 정보를 딕셔너리로 구성하여 리스트에 추가
        overview.append(
            {
                "id": course["id"],                              # 과목 고유 ID
                "title": course["title"],                        # 과목명 (예: "파이썬 기초")
                "instructor": course["instructor"],              # 강사명
                "description": course["description"],            # 과목 설명
                "level": course["level"],                        # 난이도 (초급/중급/고급)
                "module_count": total_steps,                     # 모듈(강의) 수
                "total_steps": total_steps,                      # 전체 스텝 수
                "completed_steps": completed_count,              # 완료한 스텝 수
                "completion_percentage": completion_pct,         # 완료율 (%)
            }
        )

    # 4단계: 완성된 개요 리스트 반환
    return overview


def get_module_detail(course_id):
    """
    [모듈(강의) 상세 정보 조회 함수]
    특정 과목(course_id)에 속한 모든 모듈(강의)의 상세 정보와
    진행 현황을 반환합니다.

    Args:
        course_id (int): 조회할 과목의 ID

    Returns:
        dict: 과목 정보 + 모듈(강의) 목록 + 진행 통계.
              과목이 없으면 None을 반환.

    동작 단계:
        1. get_all_courses()로 모든 과목을 조회하고, course_id와 일치하는 과목 찾기
        2. 과목이 없으면 None 반환
        3. get_lessons_by_course()로 해당 과목의 모든 강의 조회
        4. 각 강의별로 이전/다음 강의 ID를 계산 (네비게이션용)
        5. 완료/미완료 상태를 _completed_steps 기반으로 설정
        6. 전체/완료 통계를 계산하여 반환

    Jinja2 템플릿에서의 사용:
        {{ result.course.title }}              # 과목명 출력
        {% for module in result.modules %}
            {{ module.title }}                 # 모듈명 출력
            {{ "완료" if module.is_completed else "미완료" }}
        {% endfor %}
        전체 진행률: {{ result.completion_percentage }}%
    """
    # 1단계: 과목 정보 조회
    # next() 함수는 이터레이터에서 조건에 맞는 첫 번째 요소를 반환합니다.
    # courses 리스트에서 course["id"] == course_id 인 첫 번째 요소를 찾습니다.
    # 조건에 맞는 요소가 없으면 None을 반환합니다.
    courses = get_all_courses()
    course = next((c for c in courses if c["id"] == course_id), None)

    # 2단계: 과목이 존재하지 않는 경우
    if not course:
        return None  # None 반환 → 호출 측에서 404 또는 에러 처리

    # 3단계: 해당 과목의 모든 강의 조회
    lessons = get_lessons_by_course(course_id)

    # 4단계: 각 강의별 모듈 정보 구성
    modules = []
    for idx, lesson in enumerate(lessons):
        # lesson은 딕셔너리: {"id": 1, "title": "파이썬 시작하기", "content": "...", ...}
        module = {
            "id": lesson["id"],                    # 강의(모듈) 고유 ID
            "title": lesson["title"],              # 강의 제목
            "content": lesson["content"],          # 강의 내용 (본문)
            "order_num": lesson["order_num"],      # 강의 순서 번호 (정렬용)
            "duration_min": lesson["duration_min"],  # 예상 소요 시간 (분)
            "is_completed": lesson["id"] in _completed_steps,  # 완료 여부
            # 이전 강의 ID (첫 번째 강의면 None)
            "prev_id": lessons[idx - 1]["id"] if idx > 0 else None,
            # 다음 강의 ID (마지막 강의면 None)
            "next_id": lessons[idx + 1]["id"] if idx < len(lessons) - 1 else None,
        }
        modules.append(module)

    # 5단계: 진행 통계 계산
    total_steps = len(modules)
    completed_count = sum(1 for m in modules if m["is_completed"])
    completion_pct = (
        round((completed_count / total_steps * 100), 1) if total_steps > 0 else 0
    )

    # 6단계: 결과 반환
    return {
        "course": course,                 # 과목 정보 (dict)
        "modules": modules,               # 모듈(강의) 목록 (list[dict])
        "total_steps": total_steps,       # 전체 강의 수
        "completed_steps": completed_count,  # 완료한 강의 수
        "completion_percentage": completion_pct,  # 완료율 (%)
    }


def get_step_detail(course_id, step_id):
    """
    [개별 스텝(강의) 상세 정보 조회 함수]
    특정 과목 + 특정 강의의 상세 정보를 반환합니다.
    코드 예제, 예상 출력, 힌트 등을 포함하여 학습자가
    강의 내용을 실습할 수 있도록 준비합니다.

    Args:
        course_id (int): 과목 ID
        step_id (int):   스텝(강의) ID

    Returns:
        dict: 스텝 상세 정보. 스텝이나 과목이 없으면 None 반환.
              포함 필드: course, step, code_example, expected_output, hints, 등

    동작 단계:
        1. get_all_courses()로 과목 확인
        2. get_lessons_by_course()로 강의 목록 조회 후 step_id와 일치하는 강의 찾기
        3. 이전/다음 스텝 찾기 (강의 네비게이션용)
        4. _generate_code_example()로 강의 내용 기반 코드 예제 생성
        5. _generate_expected_output()로 예상 출력 생성
        6. _generate_hints()로 힌트 목록 생성
        7. 모든 정보를 하나의 딕셔너리로 반환
    """
    # 1단계: 과목 존재 여부 확인
    courses = get_all_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return None

    # 2단계: 해당 과목의 강의 목록에서 step_id와 일치하는 강의 찾기
    lessons = get_lessons_by_course(course_id)
    step = next((l for l in lessons if l["id"] == step_id), None)
    if not step:
        return None

    # 3단계: 이전/다음 스텝 찾기
    # 현재 스텝의 인덱스(current_idx)를 lessons 리스트에서 찾습니다.
    # 이 정보로 "이전 강의"와 "다음 강의" 버튼의 연결을 만듭니다.
    # enumerate()로 (인덱스, 값) 쌍을 순회하며 일치하는 id를 찾습니다.
    current_idx = next(
        (i for i, l in enumerate(lessons) if l["id"] == step_id), -1
    )
    # 이전 강의: 현재 인덱스가 0보다 크면 이전 요소, 아니면 None
    prev_step = lessons[current_idx - 1] if current_idx > 0 else None
    # 다음 강의: 현재 인덱스가 마지막이 아니면 다음 요소, 아니면 None
    next_step = (
        lessons[current_idx + 1] if current_idx < len(lessons) - 1 else None
    )

    # 4단계: 코드 예제, 예상 출력, 힌트 생성
    # _generate_* 함수들은 강의의 제목과 내용을 기반으로
    # 미리 정의된 예제 데이터를 반환합니다 (딕셔너리 룩업 방식).
    code_example = _generate_code_example(step)
    expected_output = _generate_expected_output(step)
    hints = _generate_hints(step)

    # 5단계: 결과 반환
    return {
        "course": course,                # 과목 정보
        "step": step,                    # 현재 스텝(강의) 정보
        "step_id": step_id,              # 현재 스텝 ID
        "code_example": code_example,    # 코드 예제 문자열
        "expected_output": expected_output,  # 예상 출력 문자열
        "hints": hints,                  # 힌트 리스트 (list[str])
        "is_completed": step_id in _completed_steps,  # 완료 여부
        "prev_step": prev_step,          # 이전 스텝 정보 (또는 None)
        "next_step": next_step,          # 다음 스텝 정보 (또는 None)
    }


# ============================================================
# 코드 예제 생성 함수들 (_generate_* 패턴 설명)
# ============================================================
#
# ■ _generate_* 함수들의 공통 패턴:
#   이 함수들은 모두 "강의 제목(title)을 키(key)로 하는 딕셔너리"
#   에서 미리 준비된 데이터를 조회(lookup)하는 방식으로 동작합니다.
#
#   패턴 구조:
#     1. lesson 딕셔너리에서 title 값을 추출
#     2. 미리 정의된 examples/outputs/hints 딕셔너리에서
#        title을 키로 검색 (dict.get(title, fallback))
#     3. 일치하는 항목이 있으면 해당 데이터 반환
#     4. 일치하는 항목이 없으면 기본값(fallback) 반환
#
# ■ 이 패턴의 장점:
#   - 간단하고 직관적: 데이터와 로직이 분리되어 있음
#   - 확장 용이: 새로운 강의가 추가되면 딕셔너리에 항목만 추가하면 됨
#   - 빠른 조회: 딕셔너리 해시 테이블 → O(1) 시간 복잡도
#
# ■ 이 패턴의 한계와 실제 서비스에서의 접근법:
#   - 현재: 모든 데이터를 파이썬 코드에 하드코딩
#   - 실제 서비스: 데이터베이스에 저장하고 쿼리로 조회
#     → curriculum_steps 테이블의 code_example, expected_output, hints 컬럼
#   - 또는: 마크다운 파일(YAML frontmatter)로 관리하고 파싱
#


def _generate_code_example(lesson):
    """
    [코드 예제 생성 함수]
    강의 제목을 기반으로 해당 강의에 맞는 코드 예제를 반환합니다.
    학습자가 실습 화면에서 참고할 수 있는 예제 코드를 제공합니다.

    Args:
        lesson (dict): 강의 정보 (title, content 키 포함)

    Returns:
        str: 코드 예제 문자열 (파이썬/자바스크립트 등 언어별 코드)

    패턴:
        examples 딕셔너리에서 lesson["title"]을 키로 조회합니다.
        일치하는 항목이 없으면 fallback 예제를 반환합니다.
    """
    title = lesson["title"]
    content = lesson["content"]

    # 강의 제목과 내용을 기반으로 적절한 코드 예제 반환
    # 각 항목은 "강의 제목": "코드 예제 문자열" 로 구성
    # 코드 예제는 실제 실행 가능한 완전한 코드 조각입니다.
    examples = {
        "파이썬 시작하기": "# 파이썬 첫 번째 프로그램\nprint('안녕하세요, 파이썬!')\nprint('코드교육 랩에 오신 것을 환영합니다.')",
        "변수와 자료형": "# 변수 선언과 자료형\nname = '김민수'\nage = 25\nheight = 175.5\nis_student = True\n\nprint(f'이름: {name}')\nprint(f'나이: {age}')\nprint(f'키: {height}cm')\nprint(f'학생 여부: {is_student}')",
        "조건문과 반복문": "# 조건문과 반복문 예제\nfor i in range(1, 11):\n    if i % 2 == 0:\n        print(f'{i}은(는) 짝수입니다.')\n    else:\n        print(f'{i}은(는) 홀수입니다.')",
        "함수 정의하기": "# 함수 정의하기\ndef greet(name):\n    return f'안녕하세요, {name}님!'\n\ndef add(a, b):\n    return a + b\n\nprint(greet('태호'))\nprint(f'10 + 20 = {add(10, 20)}')",
        "Flask 소개 및 설치": "# Flask 기본 앱 구조\nfrom flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return '안녕하세요, Flask!'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
        "라우팅과 뷰 함수": "# 라우팅과 뷰 함수\nfrom flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return '메인 페이지'\n\n@app.route('/about')\ndef about():\n    return '소개 페이지'\n\n@app.route('/user/<name>')\ndef user(name):\n    return f'안녕하세요, {name}님!'",
        "템플릿과 폼 처리": "# 템플릿 렌더링과 폼 처리\nfrom flask import Flask, render_template, request\n\napp = Flask(__name__)\n\n@app.route('/')\ndef index():\n    return render_template('index.html', title='홈')\n\n@app.route('/submit', methods=['POST'])\ndef submit():\n    name = request.form.get('name')\n    return f'제출됨: {name}'",
        "Node.js 기초": "// Node.js 기초\nconst http = require('http');\n\nconst server = http.createServer((req, res) => {\n    res.writeHead(200, {'Content-Type': 'text/plain'});\n    res.end('안녕하세요, Node.js!');\n});\n\nserver.listen(3000, () => {\n    console.log('서버가 3000번 포트에서 실행 중입니다.');\n});",
        "Express 서버 만들기": "// Express 서버 만들기\nconst express = require('express');\nconst app = express();\n\napp.get('/', (req, res) => {\n    res.send('메인 페이지');\n});\n\napp.get('/api/users', (req, res) => {\n    res.json([{name: '김민수'}, {name: '이서연'}]);\n});\n\napp.listen(3000, () => {\n    console.log('Express 서버 실행 중');\n});",
        "비동기 처리": "// async/await 비동기 처리\nasync function fetchData() {\n    try {\n        const response = await fetch('https://api.example.com/data');\n        const data = await response.json();\n        console.log(data);\n        return data;\n    } catch (error) {\n        console.error('에러 발생:', error);\n    }\n}\n\nfetchData();",
        "Streamlit 시작하기": "# Streamlit 기본 앱\nimport streamlit as st\n\nst.title('내 첫 Streamlit 앱')\nst.write('안녕하세요!')\n\nname = st.text_input('이름을 입력하세요')\nif st.button('인사하기'):\n    st.success(f'안녕하세요, {name}님!')",
        "데이터 시각화": "# 데이터 시각화\nimport streamlit as st\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n# 데이터 생성\ndf = pd.DataFrame({\n    '이름': ['김민수', '이서연', '박지훈'],\n    '점수': [95, 88, 92]\n})\n\n# 차트 표시\nst.bar_chart(df.set_index('이름'))\n\n# Matplotlib 차트\nfig, ax = plt.subplots()\nax.bar(df['이름'], df['점수'])\nst.pyplot(fig)",
    }

    # dict.get(key, default) 메서드:
    # - key가 딕셔너리에 있으면 해당 값을 반환
    # - key가 없으면 default 값을 반환
    # 아래 코드는 강의 제목이 examples에 없을 경우
    # 기본 코드 예제를 생성하여 반환합니다.
    return examples.get(
        title,
        f"# {title}\n# {content}\nprint(\"실습 코드를 작성해보세요.\")",
    )


def _generate_expected_output(lesson):
    """
    [예상 출력 생성 함수]
    강의 제목을 기반으로 코드 예제를 실행했을 때의
    예상 출력(콘솔 결과)을 반환합니다.

    Args:
        lesson (dict): 강의 정보 (title 키 포함)

    Returns:
        str: 예상 출력 문자열 (콘솔에 표시될 내용)

    패턴:
        _generate_code_example()과 동일한 딕셔너리 룩업 패턴을 사용합니다.
        outputs 딕셔너리에서 lesson["title"]을 키로 조회합니다.
    """
    title = lesson["title"]

    # 강의 제목별 예상 출력을 딕셔너리로 정의
    # 각 항목은 실행 결과로 콘솔/브라우저에 표시될 내용입니다.
    outputs = {
        "파이썬 시작하기": "안녕하세요, 파이썬!\n코드교육 랩에 오신 것을 환영합니다.",
        "변수와 자료형": "이름: 김민수\n나이: 25\n키: 175.5cm\n학생 여부: True",
        "조건문과 반복문": "1은(는) 홀수입니다.\n2은(는) 짝수입니다.\n3은(는) 홀수입니다.\n4은(는) 짝수입니다.\n5은(는) 홀수입니다.\n6은(는) 짝수입니다.\n7은(는) 홀수입니다.\n8은(는) 짝수입니다.\n9은(는) 홀수입니다.\n10은(는) 짝수입니다.",
        "함수 정의하기": "안녕하세요, 태호님!\n10 + 20 = 30",
        "Flask 소개 및 설치": " * Running on http://127.0.0.1:5000/\n * Debug mode: on",
        "라우팅과 뷰 함수": "브라우저에서 각 경로에 접속하면 해당 페이지가 표시됩니다.\n/ → '메인 페이지'\n/about → '소개 페이지'\n/user/김민수 → '안녕하세요, 김민수님!'",
        "템플릿과 폼 처리": "제출됨: 김민수",
        "Node.js 기초": "서버가 3000번 포트에서 실행 중입니다.",
        "Express 서버 만들기": "Express 서버 실행 중",
        "비동기 처리": "{ data: 'sample response' }",
        "Streamlit 시작하기": "브라우저에서 Streamlit 앱이 실행됩니다.\n텍스트 입력란과 버튼이 표시됩니다.",
        "데이터 시각화": "막대 차트가 표시됩니다.\n이름별 점수가 시각화됩니다.",
    }

    return outputs.get(title, "# 콘솔에 결과가 출력됩니다.")


def _generate_hints(lesson):
    """
    [힌트 생성 함수]
    강의 제목을 기반으로 학습자에게 도움이 되는
    힌트 목록을 생성하여 반환합니다.

    Args:
        lesson (dict): 강의 정보 (title 키 포함)

    Returns:
        list[str]: 힌트 문자열 리스트 (하나의 힌트가 하나의 문자열)

    패턴:
        _generate_code_example()과 동일한 딕셔너리 룩업 패턴을 사용합니다.
        hints 딕셔너리에서 lesson["title"]을 키로 조회하여
        list[str] 타입의 힌트 목록을 반환합니다.
        일치하는 항목이 없으면 기본 힌트 2개를 반환합니다.
    """
    title = lesson["title"]

    # 강의 제목별 힌트 리스트를 딕셔너리로 정의
    # 각 힌트는 학습자가 스스로 해결할 수 있도록 방향을 제시합니다.
    # 힌트는 점진적으로 공개되는 것이 효과적입니다 (첫 번째 힌트 → 두 번째 힌트).
    hints = {
        "파이썬 시작하기": [
            "print() 함수는 괄호 안의 내용을 화면에 출력합니다.",
            "문자열은 작은따옴표(')나 큰따옴표(\")로 감싸서 표현합니다.",
            "파이썬은 세미콜론(;)을 사용하지 않아도 됩니다.",
        ],
        "변수와 자료형": [
            "변수는 값을 저장하는 공간입니다. = 기호로 값을 할당합니다.",
            "f-string을 사용하면 문자열 안에 변수를 삽입할 수 있습니다: f'이름: {name}'",
            "type() 함수로 변수의 자료형을 확인할 수 있습니다.",
        ],
        "조건문과 반복문": [
            "if문은 조건이 True일 때만 실행됩니다.",
            "for문은 시퀀스(리스트, 범위 등)를 순회합니다.",
            "range(1, 11)은 1부터 10까지의 숫자를 생성합니다.",
        ],
        "함수 정의하기": [
            "def 키워드로 함수를 정의합니다.",
            "return 문으로 함수의 결과값을 반환합니다.",
            "매개변수는 함수 호출 시 전달되는 값입니다.",
        ],
        "Flask 소개 및 설치": [
            "Flask는 가벼운 파이썬 웹 프레임워크입니다.",
            "가상환경을 사용하는 것이 좋습니다: python -m venv venv",
            "app = Flask(__name__)으로 Flask 앱 인스턴스를 생성합니다.",
        ],
        "라우팅과 뷰 함수": [
            "@app.route() 데코레이터로 URL 경로를 지정합니다.",
            "뷰 함수는 해당 경로로 접속했을 때 실행되는 함수입니다.",
            "동적 경로는 꺾쇠괄호(<>)로 지정합니다: /user/<name>",
        ],
        "템플릿과 폼 처리": [
            "render_template()로 HTML 템플릿을 렌더링합니다.",
            "request.form으로 POST 방식의 폼 데이터를 가져옵니다.",
            "request.args로 GET 방식의 쿼리 파라미터를 가져옵니다.",
        ],
        "Node.js 기초": [
            "Node.js는 자바스크립트 런타임입니다.",
            "require() 함수로 모듈을 가져옵니다.",
            "npm init으로 패키지를 초기화합니다.",
        ],
        "Express 서버 만들기": [
            "Express는 Node.js용 웹 프레임워크입니다.",
            "app.get()으로 GET 요청을 처리합니다.",
            "res.send()로 응답을 전송합니다.",
        ],
        "비동기 처리": [
            "async/await는 비동기 처리를 간단하게 만들어줍니다.",
            "try-catch 블록으로 에러를 처리합니다.",
            "fetch() API로 HTTP 요청을 보냅니다.",
        ],
        "Streamlit 시작하기": [
            "Streamlit은 데이터 앱을 쉽게 만들 수 있는 프레임워크입니다.",
            "st.title()로 제목을 설정합니다.",
            "st.text_input()으로 텍스트 입력란을 만듭니다.",
        ],
        "데이터 시각화": [
            "st.bar_chart()로 간단한 막대 차트를 만듭니다.",
            "Pandas DataFrame으로 데이터를 관리합니다.",
            "Matplotlib과 연동하여 세밀한 차트를 그릴 수 있습니다.",
        ],
    }

    return hints.get(
        title,
        ["강의 내용을 잘 읽고 따라해보세요.", "공식 문서를 참고하세요."],
    )


# ============================================================
# Flask 애플리케이션 인스턴스 생성
# ============================================================
#
# Flask(__name__)은 Flask 애플리케이션의 인스턴스를 생성합니다.
# __name__은 현재 모듈의 이름(__main__ 또는 'app')을 전달하여
# Flask가 템플릿, 정적 파일 등의 경로를 찾을 수 있도록 합니다.
# 이 인스턴스를 통해 라우트 등록, 설정, 실행을 수행합니다.
#
app = Flask(__name__)


# ============================================================
# 라우트(Route) 섹션 1: 메인 대시보드
# ============================================================


@app.route("/")
def dashboard():
    """
    ============================================================
    [메인 대시보드 페이지] — GET /
    ============================================================
    ■ 이 라우트가 하는 일:
      애플리케이션의 첫 화면(홈페이지)을 렌더링합니다.
      KPI(핵심 성과 지표) 카드 4개(총 학생 수, 총 과목 수, 총 강의 수, 총 제출 수),
      과목별 학생 수 막대 차트, 성적 분포 파이 차트, 월별 제출 추세선 차트를 표시합니다.

    ■ HTTP 메서드: GET
      (데이터를 조회하여 화면에 표시하는 읽기 전용 페이지)

    ■ 템플릿 경로: templates/index.html
      - kpi 딕셔너리의 값을 카드 형태로 표시
      - course_labels와 course_student_counts로 Chart.js 막대 차트 렌더링
      - grade_distribution 리스트로 Chart.js 파이 차트 렌더링
      - monthly_labels와 monthly_submissions로 Chart.js 라인 차트 렌더링
    """
    # ─── 1단계: 데이터 수집 ───────────────────────────────
    # db_helper의 여러 함수를 호출하여 대시보드에 필요한 데이터를 수집합니다.
    students = get_all_students()             # list[dict]: 모든 학생 정보
    courses = get_all_courses()               # list[dict]: 모든 과목 정보
    course_stats = get_course_statistics()     # list[dict]: 과목별 통계
    submissions_summary = get_submissions_summary()  # list[dict]: 제출 요약

    # ─── 2단계: KPI(핵심 성과 지표) 계산 ─────────────────
    # KPI는 대시보드 상단의 카드 4개에 각각 표시됩니다.
    # 각 KPI는 데이터 수집 결과에서 집계(aggregation)하여 계산합니다.

    # KPI ①: 총 학생 수
    total_students = len(students)
    # get_all_students()가 반환한 리스트의 길이 = 등록된 전체 학생 수

    # KPI ②: 총 과목 수
    total_courses = len(courses)
    # get_all_courses()가 반환한 리스트의 길이 = 개설된 전체 과목 수

    # KPI ③: 총 강의 수
    # course_stats는 각 과목의 통계를 담고 있으며, lesson_count 필드가 있음
    # sum()으로 모든 과목의 lesson_count를 더함 = 전체 강의 수
    total_lessons = sum(c["lesson_count"] for c in course_stats)

    # KPI ④: 총 제출 수
    # course_stats의 total_submissions 필드를 모두 합산 = 전체 제출 수
    total_submissions = sum(c["total_submissions"] for c in course_stats)

    # ─── 3단계: 차트 데이터 준비 ──────────────────────────
    # Chart.js(자바스크립트 차트 라이브러리)가 사용할 수 있는 형식으로
    # 데이터를 가공합니다. Chart.js는 labels(레이블) 배열과
    # data(숫자) 배열을 받아 차트를 그립니다.

    # ■ 막대 차트 (Bar Chart) — "과목별 학생 수"
    #   X축: 과목명 (course_labels)
    #   Y축: 해당 과목의 학생 수 (course_student_counts)
    #   용도: 어떤 과목에 학생이 많이 몰리는지 한눈에 파악
    course_labels = [c["title"] for c in course_stats]                  # ["파이썬 기초", "JavaScript", ...]
    course_student_counts = [c["student_count"] for c in course_stats]   # [30, 25, ...]

    # ■ 파이 차트 (Pie Chart) — "성적 분포"
    #   학생들의 평균 점수를 기준으로 A(90+), B(80+), C(70+), D(60+), F(<60), 미평가(None)로 분류
    #   용도: 전체 학생의 성적 분포 비율을 시각적으로 파악
    student_perf = get_student_performance()  # list[dict]: 학생별 성과 데이터
    # 각 등급별 학생 수를 집계합니다.
    # 조건 리스트 컴프리헨션 + sum() 패턴:
    #   True는 1, False는 0으로 계산되어 조건을 만족하는 요소의 개수를 셉니다.
    grade_a = sum(1 for s in student_perf if s["avg_score"] and s["avg_score"] >= 90)      # 90점 이상
    grade_b = sum(1 for s in student_perf if s["avg_score"] and 80 <= s["avg_score"] < 90)  # 80~89점
    grade_c = sum(1 for s in student_perf if s["avg_score"] and 70 <= s["avg_score"] < 80)  # 70~79점
    grade_d = sum(1 for s in student_perf if s["avg_score"] and 60 <= s["avg_score"] < 70)  # 60~69점
    grade_f = sum(1 for s in student_perf if s["avg_score"] and s["avg_score"] < 60)        # 60점 미만
    grade_none = sum(1 for s in student_perf if s["avg_score"] is None)                     # 평가 없음

    # ■ 라인 차트 (Line Chart) — "월별 제출 현황"
    #   ×축: 월 (monthly_labels)
    #   Y축: 해당 월의 제출 수 (monthly_submissions)
    #   용도: 시간에 따른 학습 활동 추세 파악
    #
    # ⚠️ 현재 데이터 한계:
    #   submissions_summary에는 월별 데이터가 없으므로 더미 데이터를 사용합니다.
    #   실제 서비스에서는 제출 테이블의 created_at 컬럼을
    #   GROUP BY month 로 집계하여 사용해야 합니다.
    #   예: SELECT strftime('%m', created_at) AS month, COUNT(*) ...
    monthly_labels = ["1월", "2월", "3월", "4월", "5월", "6월"]
    monthly_submissions = [0] * 6  # [0, 0, 0, 0, 0, 0] — 기본값 (추후 구현 필요)

    # ─── 4단계: KPI 딕셔너리 구성 ────────────────────────
    kpi = {
        "total_students": total_students,        # int: 총 학생 수
        "total_courses": total_courses,          # int: 총 과목 수
        "total_lessons": total_lessons,          # int: 총 강의 수
        "total_submissions": total_submissions,  # int: 총 제출 수
    }

    # ─── 5단계: 템플릿 렌더링 ────────────────────────────
    # render_template()에 전달하는 각 변수의 의미:
    #
    #   kpi (dict)              → index.html에서 kpi.total_students 등으로 접근
    #                             {{ kpi.total_students }} → 150
    #
    #   course_labels (list)    → Chart.js 막대 차트의 X축 레이블
    #                             JSON으로 변환되어 <canvas> data-labels 속성에 저장됨
    #
    #   course_student_counts (list) → Chart.js 막대 차트의 Y축 값 (데이터)
    #
    #   grade_distribution (list)    → Chart.js 파이 차트의 데이터 값
    #                                 [A학생수, B학생수, C학생수, D학생수, F학생수, 미평가]
    #
    #   monthly_labels (list)        → Chart.js 라인 차트의 X축 레이블
    #
    #   monthly_submissions (list)   → Chart.js 라인 차트의 Y축 값
    #
    #   submissions_summary (list)   → 최근 제출 목록 테이블
    #                                   {% for sub in submissions_summary %}
    #                                     <tr><td>{{ sub.student_name }}</td>...</tr>
    #                                   {% endfor %}
    #
    return render_template(
        "index.html",
        kpi=kpi,
        course_labels=course_labels,
        course_student_counts=course_student_counts,
        grade_distribution=[
            grade_a,
            grade_b,
            grade_c,
            grade_d,
            grade_f,
            grade_none,
        ],
        monthly_labels=monthly_labels,
        monthly_submissions=monthly_submissions,
        submissions_summary=submissions_summary,
    )


# ============================================================
# 라우트 섹션 2: 학생 목록 페이지
# ============================================================


@app.route("/students")
def students():
    """
    ============================================================
    [학생 목록 페이지] — GET /students
    ============================================================
    ■ 이 라우트가 하는 일:
      모든 학생의 목록과 각 학생의 성과 요약(평균 점수, 제출 수 등)을
      테이블 형태로 표시합니다. 검색 기능을 지원하여 학생 이름이나
      이메일로 필터링할 수 있습니다.

    ■ HTTP 메서드: GET
      (쿼리 파라미터 ?search=검색어 로 검색 기능 지원)

    ■ 템플릿 경로: templates/students.html
      - students 리스트를 순회하며 각 학생의 정보를 테이블 행으로 표시
      - search_query로 검색창 값 유지 (입력한 검색어가 사라지지 않음)
      - 검색 결과가 없으면 "검색 결과가 없습니다" 메시지 표시

    ■ render_template()에 전달하는 변수의 의미:
      - students (list[dict]): 학생 성과 데이터 리스트.
          템플릿에서 {% for s in students %} 로 순회하며
          s.name, s.email, s.avg_score 등에 접근합니다.
      - search_query (str): 현재 검색어. 검색창의 value 속성에
          바인딩되어 사용자가 입력한 검색어가 유지됩니다.
    """
    # ─── 1단계: 검색어 처리 ──────────────────────────────
    # request.args.get("key", default)로 URL 쿼리 파라미터를 읽습니다.
    # URL 예: /students?search=김민수
    # request.args는 GET 파라미터를 담고 있는 ImmutableMultiDict입니다.
    # .strip()으로 앞뒤 공백을 제거합니다.
    search_query = request.args.get("search", "").strip()

    # ─── 2단계: 학생 성과 데이터 조회 ─────────────────────
    # get_student_performance()는 학생별 평균 점수, 과목 수 등의 정보를 반환합니다.
    student_perf = get_student_performance()

    # ─── 3단계: 검색 필터링 ──────────────────────────────
    # 검색어가 있으면 학생 이름 또는 이메일에 검색어가 포함된 항목만 남깁니다.
    # 대소문자 구분 없이 검색하기 위해 .lower()로 소문자 변환 후 비교합니다.
    if search_query:
        student_perf = [
            s
            for s in student_perf
            if search_query.lower() in s["name"].lower()
            or search_query.lower() in s.get("email", "").lower()
        ]

    # ─── 4단계: 템플릿 렌더링 ────────────────────────────
    return render_template(
        "students.html",
        students=student_perf,   # list[dict]: 필터링된 학생 성과 데이터
        search_query=search_query,  # str: 검색어 (검색창 value 바인딩용)
    )


# ============================================================
# 라우트 섹션 3: 과목 목록 페이지
# ============================================================


@app.route("/courses")
def courses():
    """
    ============================================================
    [과목 목록 페이지] — GET /courses
    ============================================================
    ■ 이 라우트가 하는 일:
      모든 과목의 목록을 카드 형태로 표시합니다.
      각 과목 카드에는 과목명, 강사, 수강생 수, 강의 수,
      제출 수 등의 통계가 포함됩니다.

    ■ HTTP 메서드: GET

    ■ 템플릿 경로: templates/courses.html
      - courses 리스트를 순회하며 각 과목의 정보를 카드로 표시
      - {% for c in courses %} → <div class="course-card"> ...
      - 각 카드에서 c.title, c.instructor, c.lesson_count 등에 접근

    ■ render_template()에 전달하는 변수의 의미:
      - courses (list[dict]): get_course_statistics()의 반환값.
          각 항목: {id, title, instructor, student_count, lesson_count,
                    total_submissions, avg_score, ...}
    """
    # ─── 1단계: 과목 통계 데이터 조회 ─────────────────────
    # get_course_statistics()는 각 과목의 통계 정보를 집계하여 반환합니다.
    course_stats = get_course_statistics()

    # ─── 2단계: 템플릿 렌더링 ────────────────────────────
    return render_template(
        "courses.html",
        courses=course_stats,  # list[dict]: 과목별 통계 데이터
    )


# ============================================================
# 라우트 섹션 4: 강의 목록 페이지
# ============================================================


@app.route("/lessons/<int:course_id>")
def lessons(course_id):
    """
    ============================================================
    [강의 목록 페이지] — GET /lessons/<int:course_id>
    ============================================================
    ■ 이 라우트가 하는 일:
      특정 과목(course_id)에 속한 모든 강의(레슨) 목록을 표시합니다.
      과목별로 강의 제목, 내용, 순서 등을 확인할 수 있습니다.
      상단에 과목 선택 드롭다운이 있어 다른 과목으로 쉽게 전환할 수 있습니다.

    ■ HTTP 메서드: GET
      URL 경로에 과목 ID가 포함됨 (예: /lessons/1)

    ■ 템플릿 경로: templates/lessons.html
      - lessons 리스트 순회 → 각 강의의 제목, 내용 미리보기 표시
      - course 객체로 현재 과목명 표시
      - all_courses로 과목 선택 드롭다운 생성
      - selected_course_id로 현재 선택된 과목을 드롭다운에서 하이라이트

    ■ render_template()에 전달하는 변수의 의미:
      - lessons (list[dict]):
          get_lessons_by_course() 반환값.
          템플릿에서 {% for lesson in lessons %} → {{ lesson.title }}
      - course (dict | None):
          현재 선택된 과목 정보.
          템플릿에서 {{ course.title }} 로 과목명 표시.
          None이면 "선택된 과목 없음" 처리.
      - all_courses (list[dict]):
          전체 과목 목록. 드롭다운/필터 UI용.
          {% for c in all_courses %} → <option value="{{ c.id }}">{{ c.title }}</option>
      - selected_course_id (int):
          현재 선택된 과목 ID. 드롭다운에서 selected 속성 바인딩용.
    """
    # ─── 1단계: 해당 과목의 강의 목록 조회 ────────────────
    course_lessons = get_lessons_by_course(course_id)

    # ─── 2단계: 전체 과목 목록에서 현재 과목 찾기 ────────
    # next() + 제너레이터 표현식으로 리스트에서 조건에 맞는 첫 요소 찾기
    courses = get_all_courses()
    # courses 리스트에서 id가 course_id와 같은 첫 번째 요소 반환
    current_course = next((c for c in courses if c["id"] == course_id), None)

    # ─── 3단계: 모든 과목 목록 (필터/드롭다운용) ─────────
    all_courses = courses

    # ─── 4단계: 템플릿 렌더링 ────────────────────────────
    return render_template(
        "lessons.html",
        lessons=course_lessons,    # list[dict]: 현재 과목의 강의 목록
        course=current_course,     # dict | None: 현재 과목 정보
        all_courses=all_courses,   # list[dict]: 모든 과목 목록 (드롭다운)
        selected_course_id=course_id,  # int: 선택된 과목 ID
    )


# ============================================================
# 라우트 섹션 5: 제출 목록 페이지
# ============================================================


@app.route("/submissions")
def submissions():
    """
    ============================================================
    [제출 목록 페이지] — GET /submissions
    ============================================================
    ■ 이 라우트가 하는 일:
      학생들이 제출한 모든 코드 과제를 목록 형태로 표시합니다.
      각 제출 항목에는 제출자, 과목, 코드 미리보기, 점수, 피드백,
      제출 일시 등의 정보가 포함됩니다.

    ■ HTTP 메서드: GET

    ■ 템플릿 경로: templates/submissions.html
      - submissions 리스트를 순회하며 각 제출 정보를 테이블 행으로 표시
      - {% for sub in submissions %} → <tr> ... </tr>
      - 코드 미리보기는 <pre><code>...</code></pre>로 표시
      - 점수에 따라 색상이 다르게 표시됨 (높은 점수=초록, 낮은 점수=빨강)

    ■ render_template()에 전달하는 변수의 의미:
      - submissions (list[dict]):
          get_submissions_summary() 반환값.
          각 항목: {id, student_name, course_title, code_snippet,
                    score, feedback, submitted_at, ...}
    """
    # ─── 1단계: 제출 요약 데이터 조회 ─────────────────────
    submissions_summary = get_submissions_summary()

    # ─── 2단계: 템플릿 렌더링 ────────────────────────────
    return render_template(
        "submissions.html",
        submissions=submissions_summary,  # list[dict]: 제출 요약 데이터
    )


# ============================================================
# 라우트 섹션 6: 학습 진행 현황 페이지
# ============================================================


@app.route("/progress")
def progress():
    """
    ============================================================
    [학습 진행 현황 페이지] — GET /progress
    ============================================================
    ■ 이 라우트가 하는 일:
      모든 과목의 학습 진행 상황을 종합하여 대시보드 형태로 표시합니다.
      각 과목별 완료율, 전체 진행률, 완료한 스텝 수 등을 시각화합니다.

    ■ HTTP 메서드: GET

    ■ 템플릿 경로: templates/progress.html
      - overview 리스트로 각 과목의 진행 상황을 카드/진행바로 표시
      - stats 딕셔너리로 전체 통계 요약 표시
      - {% for c in overview %}
          <div class="progress-bar" style="width: {{ c.completion_percentage }}%">
        {% endfor %}

    ■ render_template()에 전달하는 변수의 의미:
      - overview (list[dict]):
          get_curriculum_overview() 반환값.
          각 항목: {id, title, instructor, description, level,
                    module_count, total_steps, completed_steps,
                    completion_percentage}
          템플릿에서:
            {{ c.title }}           → 과목명
            {{ c.completion_percentage }}%  → 진행률 (진행바 너비로 사용)
            {{ c.completed_steps }}/{{ c.total_steps }}  → "3/5 완료"

      - stats (dict):
          전체 통계 요약.
          {total_courses, total_steps, total_completed, overall_percentage}
          템플릿에서:
            {{ stats.total_courses }}       → 전체 과목 수
            {{ stats.overall_percentage }}% → 전체 진행률
    """
    # ─── 1단계: 커리큘럼 개요 데이터 조회 ─────────────────
    # get_curriculum_overview()는 모든 과목의 진행 상황을 계산하여 반환합니다.
    # ※ 참고: 이 파일에는 동일한 이름의 함수가 두 번 정의되어 있습니다.
    #   첫 번째 정의 (초기)는 db_helper 기반, 두 번째 정의 (아래)에서
    #   동일 이름으로 다시 정의되어 첫 번째를 덮어씁니다(override).
    #   파이썬은 함수 정의가 나중에 오는 것이 우선합니다.
    overview = get_curriculum_overview()

    # ─── 2단계: 전체 통계 계산 ───────────────────────────
    # 모든 과목의 데이터를 합산하여 전체 진행 통계를 계산합니다.
    total_steps = sum(c["total_steps"] for c in overview)         # 모든 과목의 전체 스텝 수 합계
    total_completed = sum(c["completed_steps"] for c in overview) # 모든 과목의 완료 스텝 수 합계
    # 전체 완료율 = (완료 스텝 수 / 전체 스텝 수) * 100
    overall_percentage = (
        round((total_completed / total_steps * 100), 1) if total_steps > 0 else 0
    )

    # ─── 3단계: 통계 요약 딕셔너리 구성 ───────────────────
    stats = {
        "total_courses": len(overview),          # int: 전체 과목 수
        "total_steps": total_steps,              # int: 전체 스텝 수
        "total_completed": total_completed,      # int: 완료된 스텝 수
        "overall_percentage": overall_percentage,  # float: 전체 완료율 (%)
    }

    # ─── 4단계: 템플릿 렌더링 ────────────────────────────
    return render_template(
        "progress.html",
        overview=overview,  # list[dict]: 과목별 진행 상황
        stats=stats,        # dict: 전체 통계 요약
    )


# ============================================================
# 헬퍼 함수 섹션 2: 커리큘럼 모듈 기반 헬퍼 (직접 SQLite 연결)
# ============================================================
#
# ※ 위에서 get_curriculum_overview(), get_step_detail() 등을
#   이미 정의했지만, 아래에 동일한 이름의 함수가 다시 정의됩니다.
#   파이썬에서는 나중에 정의된 함수가 이전 정의를 덮어씁니다(override).
#
# 아래 함수들은 db_helper 모듈을 경유하지 않고, 직접 SQLite3 데이터베이스에
# 연결하여 커리큘럼 모듈(curriculum_modules)과 스텝(curriculum_steps)
# 테이블을 조회합니다. 이는 "레슨(lesson)"이 아닌 "모듈-스텝" 구조로
# 커리큘럼을 관리하기 위한 것입니다.
#
# 데이터베이스 스키마 (관련 테이블):
#   curriculum_modules: id, course_id, title, description, order_num
#   curriculum_steps:   id, module_id, title, content, code_example,
#                       expected_output, hints, order_num


def get_curriculum_overview():
    """
    [커리큘럼 개요 조회 함수 — 모듈 기반 버전]
    ※ 이 함수는 위의 동명 함수를 덮어씁니다.
    모든 과목의 개요 정보를 모듈-스텝 구조로 반환합니다.
    첫 번째 버전과 달리, 이 함수는 각 과목의 모듈 수와
    각 모듈 내 스텝 수를 계산하여 더 세분화된 개요를 제공합니다.

    Returns:
        list[dict]: 과목별 커리큘럼 개요 정보 리스트.
                    첫 번째 버전과 동일한 인터페이스이지만,
                    module_count와 total_steps 계산 방식이 다릅니다.
                    (첫 번째: lessons 수 = total_steps
                     두 번째: modules 수 = module_count, steps 합계 = total_steps)

    동작 단계:
        1. get_all_courses()로 모든 과목 조회
        2. 각 과목별로 get_curriculum_by_course()로 모듈 목록 조회
        3. 각 모듈의 steps 리스트 길이를 합산 → total_steps
        4. _completed_steps 세트로 완료 스텝 계산
        5. 완료율 계산 후 개요 정보 구성
    """
    # db_helper에서 커리큘럼 관련 함수를 지연 임포트(lazy import)
    # 함수 내부에서 import하는 이유:
    #   모듈 상단에서 import하면 순환 참조 문제가 생길 수 있음
    #   또는 이 함수가 호출될 때만 필요하므로 메모리 절약
    from db_helper import get_curriculum_by_course, get_student_progress

    # 1단계: 모든 과목 조회
    courses = get_all_courses()
    overview = []

    # 2단계: 각 과목별로 모듈 및 스텝 정보 수집
    for course in courses:
        # get_curriculum_by_course()는 해당 과목의 모든 curriculum_modules를
        # 조회하고, 각 모듈에 속한 steps도 함께 반환합니다.
        modules = get_curriculum_by_course(course["id"])

        # 전체 스텝 수 = 각 모듈의 steps 리스트 길이 합계
        total_steps = sum(len(m.get("steps", [])) for m in modules)

        # 완료된 스텝 수 계산
        # _completed_steps 세트에 각 스텝의 id가 존재하는지 확인
        completed_steps = 0
        for module in modules:
            for step in module.get("steps", []):
                if step["id"] in _completed_steps:
                    completed_steps += 1

        # 완료율 계산 (total_steps가 0이면 0으로 처리)
        completion_pct = (
            round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
        )

        # 3단계: 과목 개요 정보 구성
        overview.append(
            {
                "id": course["id"],                              # 과목 ID
                "title": course["title"],                        # 과목명
                "instructor": course["instructor"],              # 강사
                "description": course["description"],            # 설명
                "level": course["level"],                        # 난이도
                "module_count": len(modules),                    # 모듈 수 (첫 번째 버전과 차이)
                "total_steps": total_steps,                      # 전체 스텝 수
                "completed_steps": completed_steps,              # 완료 스텝 수
                "completion_percentage": completion_pct,         # 완료율
            }
        )

    return overview


def get_course_modules(course_id):
    """
    [과목 모듈 목록 조회 함수]
    특정 과목(course_id)의 모든 모듈과 각 모듈에 속한
    모든 스텝을 계층 구조로 반환합니다.

    Args:
        course_id (int): 조회할 과목 ID

    Returns:
        dict: 과목 정보 + 모듈(스텝 포함) 목록 + 진행 통계.
              과목이 없으면 None 반환.

    동작 단계:
        1. 과목 존재 확인 (get_all_courses()에서 course_id 검색)
        2. get_curriculum_by_course()로 모듈-스텡 계층 조회
        3. _completed_steps 기반으로 진행 통계 계산
        4. 결과 딕셔너리 반환

    Jinja2 템플릿에서의 사용:
        {% for module in result.modules %}
            {{ module.title }} ({{ module.steps | length }}개 스텝)
            {% for step in module.steps %}
                {{ step.title }}
                {{ "✓" if step.id in completed_set else "○" }}
            {% endfor %}
        {% endfor %}
    """
    from db_helper import get_curriculum_by_course

    # 1단계: 과목 정보 조회 및 존재 확인
    courses = get_all_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return None

    # 2단계: 모듈-스텝 계층 구조 조회
    modules = get_curriculum_by_course(course_id)

    # 3단계: 진행 통계 계산
    total_steps = sum(len(m.get("steps", [])) for m in modules)
    completed_steps = 0
    for module in modules:
        for step in module.get("steps", []):
            if step["id"] in _completed_steps:
                completed_steps += 1

    completion_pct = (
        round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
    )

    # 4단계: 결과 반환
    return {
        "course": course,                   # dict: 과목 정보
        "modules": modules,                 # list[dict]: 모듈 목록 (각 모듈은 steps 포함)
        "total_steps": total_steps,         # int: 전체 스텝 수
        "completed_steps": completed_steps,  # int: 완료 스텝 수
        "completion_percentage": completion_pct,  # float: 완료율
    }


def get_module_detail(module_id):
    """
    [모듈 상세 정보 조회 함수]
    특정 모듈(module_id)의 상세 정보와 해당 모듈에 속한
    모든 스텝을 반환합니다. 직접 SQLite 쿼리를 실행합니다.

    Args:
        module_id (int): 조회할 모듈 ID

    Returns:
        dict: 모듈 정보 + 스텝 목록. 모듈이 없으면 None 반환.

    동작 단계:
        1. get_db_connection()으로 SQLite 연결
        2. curriculum_modules 테이블에서 module_id로 모듈 조회
        3. curriculum_steps 테이블에서 module_id로 스텝 목록 조회 (order_num 정렬)
        4. 모듈에 스텝 목록을 추가하여 반환
        5. 데이터베이스 연결 종료 (conn.close())
    """
    # 1단계: 데이터베이스 연결
    # get_db_connection()은 sqlite3.connect()로 연결을 열고
    # row_factory를 sqlite3.Row로 설정하여 컬럼명으로 접근 가능하게 합니다.
    conn = get_db_connection()

    # 2단계: 모듈 정보 조회
    # SELECT * FROM curriculum_modules WHERE id = ?;
    # ?는 파라미터 바인딩(parameter binding) — SQL 인젝션 방지
    cursor = conn.execute(
        "SELECT * FROM curriculum_modules WHERE id = ?;",
        (module_id,),
    )
    module = cursor.fetchone()  # 첫 번째 행 반환 (없으면 None)

    # 3단계: 모듈이 없으면 None 반환
    if not module:
        conn.close()  # 연결 닫기 (리소스 해제)
        return None

    # sqlite3.Row 객체를 dict로 변환
    # dict() 생성자에 Row 객체를 전달하면 {컬럼명: 값} 형태로 변환됩니다.
    module = dict(module)

    # 4단계: 모듈에 속한 모든 스텝 조회
    # order_num으로 정렬하여 커리큘럼 순서를 유지합니다.
    cursor = conn.execute(
        "SELECT * FROM curriculum_steps WHERE module_id = ? ORDER BY order_num;",
        (module_id,),
    )
    steps = [dict(row) for row in cursor.fetchall()]  # 모든 스텝을 dict 리스트로 변환
    conn.close()  # 연결 닫기

    # 5단계: 모듈 정보에 스텝 목록 추가
    module["steps"] = steps          # list[dict]: 스텝 목록
    module["step_count"] = len(steps)  # int: 스텝 개수
    module["course_id"] = module.get("course_id")  # int: 과목 ID (모듈의 부모 과목)

    return module


def get_step_detail(step_id):
    """
    [개별 스텝 상세 정보 조회 함수 — 직접 SQLite 버전]
    ※ 이 함수는 위의 동명 함수(course_id, step_id 버전)를 덮어씁니다.
    특정 스텝(step_id)의 모든 상세 정보를 반환합니다.
    JOIN 쿼리로 스텝에 연결된 모듈명과 과목 ID도 함께 조회합니다.

    Args:
        step_id (int): 조회할 스텝 ID

    Returns:
        dict: 스텝 상세 정보 (지시문, 코드 예제, 예상 출력, 힌트, 이전/다음 스텝 등).
              스텝이 없으면 None 반환.

    동작 단계:
        1. 직접 SQLite 연결 → JOIN 쿼리로 스텝 + 모듈 정보 조회
        2. 스텝 데이터를 dict로 변환
        3. DB에서 code_example, expected_output 추출 (첫 번째 버전과 달리 DB에서 직접 조회)
        4. hints 필드를 JSON 또는 CSV 문자열에서 리스트로 파싱
        5. get_course_modules()로 모든 모듈-스텝 조회 후 이전/다음 스텝 계산
        6. 완료 여부와 함께 결과 반환
    """
    # 1단계: 데이터베이스 연결 및 스텝 + 모듈 정보 JOIN 조회
    # JOIN: curriculum_steps와 curriculum_modules 테이블을 module_id로 연결
    #   → 스텝 정보에 모듈 제목(module_title)과 과목 ID(course_id)를 함께 가져옴
    conn = get_db_connection()
    cursor = conn.execute(
        """
        SELECT cs.*, cm.title AS module_title, cm.course_id
        FROM curriculum_steps cs
        JOIN curriculum_modules cm ON cs.module_id = cm.id
        WHERE cs.id = ?;
        """,
        (step_id,),
    )
    step = cursor.fetchone()

    # 2단계: 스텝이 없으면 None 반환
    if not step:
        conn.close()
        return None

    # sqlite3.Row → dict 변환
    step = dict(step)
    conn.close()

    # 3단계: 코드 예제와 예상 출력 가져오기
    # 첫 번째 버전의 get_step_detail()과 달리,
    # 여기서는 _generate_* 함수를 사용하지 않고 DB에 저장된 값을 직접 사용합니다.
    # DB의 curriculum_steps 테이블에 code_example, expected_output 컬럼이 있다고 가정합니다.
    code_example = step.get("code_example", "")
    expected_output = step.get("expected_output", "")

    # 4단계: 힌트 파싱
    # 힌트는 DB에 다음과 같은 형식으로 저장될 수 있습니다:
    #   (a) JSON 배열: '["힌트1", "힌트2"]'
    #   (b) CSV 문자열: '힌트1, 힌트2'
    #   (c) 빈 문자열: ''
    # json.loads()로 JSON 파싱을 시도하고, 실패하면 CSV 형식으로 fallback 처리합니다.
    hints_raw = step.get("hints", "")
    if hints_raw:
        import json

        try:
            # JSON 배열 형식으로 저장된 경우
            hints = json.loads(hints_raw)
        except (json.JSONDecodeError, TypeError):
            # CSV 형식으로 저장된 경우: 쉼표로 분할 후 각 항목의 공백 제거
            hints = [h.strip() for h in hints_raw.split(",") if h.strip()]
    else:
        hints = ["참고 자료를 확인하세요."]

    # 5단계: 이전/다음 스텝 찾기
    # get_course_modules()로 해당 과목의 모든 모듈-스텝 구조를 조회한 후,
    # 현재 스텝의 위치를 찾아 이전/다음 스텝을 결정합니다.
    course_id = step["course_id"]
    module_id = step["module_id"]

    modules = get_course_modules(course_id)  # 전체 모듈-스텝 구조 조회
    prev_step = None
    next_step = None
    current_idx = -1

    # 모든 모듈을 순회하며 현재 스텝의 위치를 찾고
    # 이전 스텝(같은 모듈의 이전 스텝 또는 이전 모듈의 마지막 스텝)과
    # 다음 스텝(같은 모듈의 다음 스텝 또는 다음 모듈의 첫 번째 스텝)을 찾습니다.
    for module in modules["modules"]:
        for i, s in enumerate(module["steps"]):
            if s["id"] == step_id:
                current_idx = i
                # --- 이전 스텝 찾기 ---
                if i > 0:
                    # 같은 모듈 내 이전 스텝
                    prev_step = module["steps"][i - 1]
                else:
                    # 현재 모듈의 첫 번째 스텝 → 이전 모듈의 마지막 스텝
                    mod_idx = next(
                        (
                            j
                            for j, m in enumerate(modules["modules"])
                            if m["id"] == module_id
                        ),
                        -1,
                    )
                    if mod_idx > 0:
                        prev_mod = modules["modules"][mod_idx - 1]
                        if prev_mod["steps"]:
                            prev_step = prev_mod["steps"][-1]
                # --- 다음 스텝 찾기 ---
                if i < len(module["steps"]) - 1:
                    # 같은 모듈 내 다음 스텝
                    next_step = module["steps"][i + 1]
                else:
                    # 현재 모듈의 마지막 스텝 → 다음 모듈의 첫 번째 스텝
                    mod_idx = next(
                        (
                            j
                            for j, m in enumerate(modules["modules"])
                            if m["id"] == module_id
                        ),
                        -1,
                    )
                    if mod_idx < len(modules["modules"]) - 1:
                        next_mod = modules["modules"][mod_idx + 1]
                        if next_mod["steps"]:
                            next_step = next_mod["steps"][0]
                break

    # 6단계: 결과 반환
    return {
        "step": step,                    # dict: 스텝 전체 정보
        "step_id": step_id,              # int: 스텝 ID
        "course_id": course_id,          # int: 과목 ID
        "module_id": module_id,          # int: 모듈 ID
        "module_title": step["module_title"],  # str: 모듈 제목 (JOIN 결과)
        "code_example": code_example,    # str: 코드 예제
        "expected_output": expected_output,  # str: 예상 출력
        "hints": hints,                  # list[str]: 힌트 목록
        "is_completed": step_id in _completed_steps,  # bool: 완료 여부
        "prev_step": prev_step,          # dict | None: 이전 스텝
        "next_step": next_step,          # dict | None: 다음 스텝
    }


def get_db_connection():
    """
    [데이터베이스 연결 함수]
    SQLite3 데이터베이스(edu.db)에 대한 연결을 생성하고 반환합니다.

    Returns:
        sqlite3.Connection: SQLite 데이터베이스 연결 객체

    동작 단계:
        1. sqlite3 모듈 임포트 (표준 라이브러리, 별도 설치 불필요)
        2. DB 파일 경로 계산:
           os.path.join(os.path.dirname(__file__), "..", "shared", "db", "edu.db")
           = 현재 파일의 상위/상위/shared/db/edu.db
        3. sqlite3.connect()로 연결 생성
        4. PRAGMA foreign_keys = ON:
           외래 키 제약 조건을 활성화합니다.
           SQLite는 기본적으로 외래 키 제약을 비활성화하므로,
           연결 시마다 명시적으로 활성화해야 합니다.
        5. row_factory = sqlite3.Row:
           기본값은 튜플(tuple)로 반환되지만,
           sqlite3.Row로 설정하면 컬럼명으로 접근 가능:
           row["title"] (O) vs row[1] (X)
        6. 연결 객체 반환
    """
    import sqlite3

    # DB 파일의 절대 경로 계산
    db_path = os.path.join(
        os.path.dirname(__file__),  # 이 파일(app.py)의 디렉토리
        "..",                         # 한 단계 위 (python-flask/)
        "..",                         # 또 한 단계 위 (code-edu-lab/)
        "shared",
        "db",
        "edu.db",                     # 최종: ~/code-edu-lab/shared/db/edu.db
    )
    conn = sqlite3.connect(db_path)  # SQLite 연결 열기
    conn.execute("PRAGMA foreign_keys = ON;")  # 외래 키 제약 활성화
    conn.row_factory = sqlite3.Row  # 컬럼명 접근 가능하도록 설정
    return conn


# ============================================================
# 라우트 섹션 7: 커리큘럼 모듈 기반 페이지
# ============================================================
# 아래 라우트들은 위에서 정의한 모듈-스텝 기반 헬퍼 함수들을 사용하여
# 커리큘럼 구조를 탐색하는 페이지들을 제공합니다.


@app.route("/curriculum")
def curriculum():
    """
    ============================================================
    [커리큘럼 개요 페이지] — GET /curriculum
    ============================================================
    ■ 이 라우트가 하는 일:
      모든 과목의 커리큘럼 구조를 모듈-스텝 계층으로 표시합니다.
      각 과목의 모듈 수, 스텝 수, 완료율 등의 개요 정보를 보여줍니다.

    ■ HTTP 메서드: GET

    ■ 템플릿 경로: templates/curriculum.html
      - overview 리스트를 순회하며 각 과목의 커리큘럼 카드 표시
      - {% for c in overview %}
          <a href="/curriculum/{{ c.id }}">{{ c.title }}</a>
          진행률: {{ c.completion_percentage }}%
        {% endfor %}
      - 각 카드에서 과목 상세 페이지(curriculum_detail)로 이동 가능

    ■ render_template()에 전달하는 변수의 의미:
      - overview (list[dict]):
          get_curriculum_overview() 반환값 (모듈 기반 버전).
          각 항목: {id, title, instructor, description, level,
                    module_count, total_steps, completed_steps,
                    completion_percentage}
    """
    overview = get_curriculum_overview()
    return render_template("curriculum.html", overview=overview)


@app.route("/curriculum/<int:course_id>")
def curriculum_detail(course_id):
    """
    ============================================================
    [과목 상세(커리큘럼) 페이지] — GET /curriculum/<int:course_id>
    ============================================================
    ■ 이 라우트가 하는 일:
      특정 과목(course_id)의 커리큘럼 상세 정보를 표시합니다.
      과목에 속한 모든 모듈과 각 모듈의 스텝 목록을 계층 구조로 보여줍니다.
      각 스텝은 개별 페이지로 연결됩니다.

    ■ HTTP 메서드: GET

    ■ 템플릿 경로: templates/curriculum_detail.html
      - detail.course: 과목 정보 표시 (제목, 강사, 설명)
      - detail.modules: 모듈 목록 순회
        {% for module in detail.modules %}
          {{ module.title }} ({{ module.steps | length }}개 스텝)
          {% for step in module.steps %}
            스텝: <a href="/curriculum/{{ course_id }}/step/{{ step.id }}">
                    {{ step.title }}</a>
            {% if step.id in completed_set %} ✓ {% endif %}
          {% endfor %}
        {% endfor %}
      - detail.completion_percentage: 전체 진행률 표시

    ■ render_template()에 전달하는 변수의 의미:
      - detail (dict):
          get_course_modules() 반환값.
          {course, modules, total_steps, completed_steps, completion_percentage}
      - 오류 처리:
          과목이 존재하지 않으면 에러 메시지와 함께 개요 페이지로 리다이렉트
    """
    # ─── 1단계: 과목 모듈 데이터 조회 ─────────────────────
    detail = get_course_modules(course_id)

    # ─── 2단계: 과목이 없으면 에러 처리 ──────────────────
    if not detail:
        # 과목 ID가 유효하지 않은 경우 → 커리큘럼 개요 페이지로 돌아가며 에러 표시
        return render_template(
            "curriculum.html",
            overview=get_curriculum_overview(),
            error="과목을 찾을 수 없습니다.",
        )

    # ─── 3단계: 템플릿 렌더링 ────────────────────────────
    return render_template("curriculum_detail.html", detail=detail)


@app.route("/curriculum/<int:course_id>/step/<int:step_id>", methods=["GET"])
def curriculum_step(course_id, step_id):
    """
    ============================================================
    [개별 스텝(커리큘럼) 페이지] — GET /curriculum/<course_id>/step/<step_id>
    ============================================================
    ■ 이 라우트가 하는 일:
      특정 과목의 특정 스텝(강의)의 상세 페이지를 표시합니다.
      스텝의 본문(content), 코드 예제, 예상 출력, 힌트 등을 보여주고
      학습자가 '완료' 버튼을 누를 수 있도록 합니다.
      이전/다음 스텝으로 이동하는 네비게이션도 제공합니다.

    ■ HTTP 메서드: GET

    ■ 템플릿 경로: templates/curriculum_step.html
      - detail.step.content: 강의 본문 내용
      - detail.code_example: 코드 예제 (<pre><code> 영역)
      - detail.expected_output: 예상 출력
      - detail.hints: 힌트 목록 (접이식 UI)
      - detail.is_completed: 완료 버튼 상태 (완료 시 비활성화)
      - detail.prev_step / detail.next_step: 이전/다음 스텝 링크
      - JavaScript fetch()로 POST /curriculum/.../complete 호출

    ■ render_template()에 전달하는 변수의 의미:
      - detail (dict):
          get_step_detail(step_id) 반환값.
          {step, step_id, course_id, module_id, module_title,
           code_example, expected_output, hints, is_completed,
           prev_step, next_step}
          템플릿에서:
            {{ detail.step.title }}         → 스텝 제목
            {{ detail.step.content }}       → 강의 본문
            {{ detail.code_example }}       → 코드 예제
            {{ detail.expected_output }}    → 예상 출력
            {% for h in detail.hints %}
              <li>{{ h }}</li>
            {% endfor %}
            {{ "완료" if detail.is_completed else "미완료" }}
            {% if detail.prev_step %}
              <a href=".../step/{{ detail.prev_step.id }}">이전</a>
            {% endif %}
    """
    # ─── 1단계: 스텝 상세 정보 조회 ──────────────────────
    detail = get_step_detail(step_id)

    # ─── 2단계: 유효성 검사 ──────────────────────────────
    # 스텝이 존재하지 않거나, 요청된 course_id와 스텝의 실제 course_id가
    # 일치하지 않으면 커리큘럼 개요 페이지로 리다이렉트합니다.
    if not detail or detail["course_id"] != course_id:
        return redirect(url_for("curriculum"))

    # ─── 3단계: 템플릿 렌더링 ────────────────────────────
    return render_template("curriculum_step.html", detail=detail)


@app.route(
    "/curriculum/<int:course_id>/step/<int:step_id>/complete",
    methods=["POST"],
)
def curriculum_step_complete(course_id, step_id):
    """
    ============================================================
    [스텝 완료 처리 API] — POST /curriculum/<course_id>/step/<step_id>/complete
    ============================================================
    ■ 이 라우트가 하는 일:
      학습자가 스텝을 완료했을 때 호출되는 API 엔드포인트입니다.
      진행 상황을 데이터베이스에 저장하고, 메모리 내 _completed_steps 세트도
      업데이트합니다. AJAX 요청과 일반 폼 제출 모두 처리합니다.

    ■ HTTP 메서드: POST
      (GET 요청은 허용되지 않음 → 405 Method Not Allowed)

    ■ 응답 형식:
      - AJAX 요청 (X-Requested-With: XMLHttpRequest):
        JSON 응답 → {"success": true, "step_id": 1, "status": "completed"}
      - 일반 폼 제출:
        HTTP 302 리다이렉트 → /curriculum/<course_id>/step/<step_id>

    동작 단계:
        1. 폼에서 student_id를 받음 (기본값: 1, 실제로는 세션에서 가져와야 함)
        2. update_student_progress() 호출 → DB에 진행 상황 저장
        3. 성공 시 _completed_steps 세트에도 추가 (메모리 동기화)
        4. 요청이 AJAX인지 일반 폼 제출인지에 따라 응답 방식 결정

    ⚠️ 보안 참고사항:
      - 현재 student_id는 폼 데이터에서 받아오므로 위조 가능
      - 실제 서비스에서는 Flask 세션(session) 또는 JWT 토큰에서
        인증된 사용자의 ID를 추출해야 함
      - CSRF 보호도 필요 (Flask-WTF 확장 사용)
    """
    # ─── 1단계: db_helper에서 진행률 업데이트 함수 임포트 ─
    from db_helper import update_student_progress

    # ─── 2단계: 학생 ID 가져오기 ──────────────────────────
    # 실제 환경: 세션 또는 인증 시스템에서 가져와야 함
    # 예: student_id = session['user_id']
    # 현재: 폼 데이터 또는 기본값 1 사용 (데모 목적)
    student_id = request.form.get("student_id", 1)

    # ─── 3단계: DB에 진행 상황 저장 ───────────────────────
    # update_student_progress()는 student_progress 테이블에
    # (student_id, step_id, status) 레코드를 INSERT 또는 UPDATE합니다.
    success = update_student_progress(student_id, step_id, "completed")

    # ─── 4단계: 메로리 내 세트도 함께 업데이트 ──────────
    # DB와 메모리 상태를 동기화하여, 이번 요청에서 즉시
    # 반영된 진행률을 볼 수 있도록 합니다.
    if success:
        _completed_steps.add(step_id)

    # ─── 5단계: 응답 생성 ────────────────────────────────
    # AJAX 요청인지 확인하는 방법:
    #   클라이언트(JavaScript)가 fetch() 또는 XMLHttpRequest로 요청할 때
    #   X-Requested-With: XMLHttpRequest 헤더를 함께 보냅니다.
    #   일반 HTML 폼 제출에는 이 헤더가 없습니다.
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # AJAX 응답: JSON 형식으로 성공 여부와 함께 반환
        return jsonify(
            {
                "success": success,    # bool: 저장 성공 여부
                "step_id": step_id,    # int: 완료된 스텝 ID
                "status": "completed", # str: 상태 메시지
            }
        )

    # 일반 폼 제출: 완료된 스텝 페이지로 리다이렉트
    return redirect(
        url_for("curriculum_step", course_id=course_id, step_id=step_id)
    )


# ============================================================
# 애플리케이션 진입점 (Entry Point)
# ============================================================
#
# if __name__ == "__main__": 의 의미:
#   파이썬 스크립트는 직접 실행될 때 __name__ 변수에 "__main__"이 할당됩니다.
#   다른 모듈에서 import될 때는 __name__이 "app"과 같은 모듈명이 됩니다.
#   따라서 아래 코드 블록은 이 파일을 직접 실행할 때만(app.run()) 실행되고,
#   다른 모듈에서 import할 때는 실행되지 않습니다.
#
# app.run(debug=True, port=5000):
#   - debug=True: 코드 변경 시 자동 리로드, 에러 발생 시 디버거 표시
#   - port=5000: http://localhost:5000 에서 서비스 시작
#   - 실제 배포 시에는 Gunicorn/Waitress 등의 WSGI 서버를 사용
#     → debug=False, host='0.0.0.0', port=8080 등
#
if __name__ == "__main__":
    app.run(debug=True, port=5000)
