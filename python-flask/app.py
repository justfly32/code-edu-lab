"""
코드교육 � 대시보드 메인 애플리케이션
Flask 기반 학습 관리 시스템 대시보드입니다.
"""

import sys
import os

# 공유 데이터베이스 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared", "db"))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from db_helper import (
    get_all_students,
    get_all_courses,
    get_enrollments_by_course,
    get_lessons_by_course,
    get_submissions_summary,
    get_student_performance,
    get_course_statistics,
)

# ============================================================
# 커리큘럼 관련 헬퍼 함수 (Curriculum helper functions)
# ============================================================

# 진행률 추적을 위한 전역 딕셔너리 (Global dict for tracking progress)
# 실제 운영 환경에서는 데이터베이스나 세션을 사용해야 합니다
_completed_steps = set()


def get_curriculum_overview():
    """
    커리큘럼 개요를 반환합니다.
    각 과목별로 모듈 수, 전체 스텝 수, 완료율을 포함합니다.
    
    Returns:
        dict: 과목별 커리큘럼 개요 정보
    """
    courses = get_all_courses()
    overview = []
    
    for course in courses:
        lessons = get_lessons_by_course(course["id"])
        total_steps = len(lessons)
        # 완료된 스텝 수 계산
        completed_count = sum(
            1 for lesson in lessons if lesson["id"] in _completed_steps
        )
        completion_pct = round((completed_count / total_steps * 100), 1) if total_steps > 0 else 0
        
        overview.append({
            "id": course["id"],
            "title": course["title"],
            "instructor": course["instructor"],
            "description": course["description"],
            "level": course["level"],
            "module_count": total_steps,  # 모듈(강의) 수
            "total_steps": total_steps,
            "completed_steps": completed_count,
            "completion_percentage": completion_pct,
        })
    
    return overview


def get_module_detail(course_id):
    """
    특정 과목의 모듈(강의) 상세 정보를 반환합니다.
    
    Args:
        course_id: 과목 ID
        
    Returns:
        dict: 과목 정보 및 모듈(강의) 목록
    """
    courses = get_all_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    
    if not course:
        return None
    
    lessons = get_lessons_by_course(course_id)
    modules = []
    
    for idx, lesson in enumerate(lessons):
        module = {
            "id": lesson["id"],
            "title": lesson["title"],
            "content": lesson["content"],
            "order_num": lesson["order_num"],
            "duration_min": lesson["duration_min"],
            "is_completed": lesson["id"] in _completed_steps,
            "prev_id": lessons[idx - 1]["id"] if idx > 0 else None,
            "next_id": lessons[idx + 1]["id"] if idx < len(lessons) - 1 else None,
        }
        modules.append(module)
    
    total_steps = len(modules)
    completed_count = sum(1 for m in modules if m["is_completed"])
    completion_pct = round((completed_count / total_steps * 100), 1) if total_steps > 0 else 0
    
    return {
        "course": course,
        "modules": modules,
        "total_steps": total_steps,
        "completed_steps": completed_count,
        "completion_percentage": completion_pct,
    }


def get_step_detail(course_id, step_id):
    """
    개별 스텝(강의)의 상세 정보를 반환합니다.
    
    Args:
        course_id: 과목 ID
        step_id: 스텝(강의) ID
        
    Returns:
        dict: 스텝 상세 정보 (지시문, 코드 예제, 예상 출력, 힌트)
    """
    courses = get_all_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    
    if not course:
        return None
    
    lessons = get_lessons_by_course(course_id)
    step = next((l for l in lessons if l["id"] == step_id), None)
    
    if not step:
        return None
    
    # 이전/다음 스텝 찾기
    current_idx = next(
        (i for i, l in enumerate(lessons) if l["id"] == step_id), -1
    )
    prev_step = lessons[current_idx - 1] if current_idx > 0 else None
    next_step = lessons[current_idx + 1] if current_idx < len(lessons) - 1 else None
    
    # 코드 예제 생성 (강의 내용 기반)
    # 실제 환경에서는 데이터베이스에 저장된 코드를 사용하지만,
    # 여기서는 강의 내용을 기반으로 예제를 생성합니다
    code_example = _generate_code_example(step)
    expected_output = _generate_expected_output(step)
    hints = _generate_hints(step)
    
    return {
        "course": course,
        "step": step,
        "step_id": step_id,
        "code_example": code_example,
        "expected_output": expected_output,
        "hints": hints,
        "is_completed": step_id in _completed_steps,
        "prev_step": prev_step,
        "next_step": next_step,
    }


def _generate_code_example(lesson):
    """강의 내용에 따른 코드 예제를 생성합니다."""
    title = lesson["title"]
    content = lesson["content"]
    
    # 강의 제목과 내용을 기반으로 적절한 코드 예제 반환
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
    
    return examples.get(title, f"# {title}\n# {content}\nprint(\"실습 코드를 작성해보세요.\")")


def _generate_expected_output(lesson):
    """강의에 따른 예상 출력을 생성합니다."""
    title = lesson["title"]
    
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
    """강의에 딞는 힌트 목록을 생성합니다."""
    title = lesson["title"]
    
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
    
    return hints.get(title, ["강의 내용을 잘 읽고 따라해보세요.", "공식 문서를 참고하세요."])

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


@app.route("/progress")
def progress():
    """
    학습 진현 대시보드 - 모든 과목의 진행 상황을 종합하여 표시합니다.
    """
    overview = get_curriculum_overview()
    
    # 전체 통계 계산
    total_steps = sum(c["total_steps"] for c in overview)
    total_completed = sum(c["completed_steps"] for c in overview)
    overall_percentage = round((total_completed / total_steps * 100), 1) if total_steps > 0 else 0
    
    stats = {
        "total_courses": len(overview),
        "total_steps": total_steps,
        "total_completed": total_completed,
        "overall_percentage": overall_percentage,
    }
    
    return render_template("progress.html", overview=overview, stats=stats)


# ============================================================
# 커리큘럼 모듈 기반 헬퍼 함수 (Curriculum Modules helper functions)
# ============================================================

def get_curriculum_overview():
    """
    커리큘럼 모듈을 기반으로 모든 과목의 개요를 반환합니다.
    각 과목별로 모듈 수, 전체 스텝 수, 완료율을 포함합니다.
    
    Returns:
        list[dict]: 과목별 커리큘럼 개요 정보
    """
    from db_helper import get_curriculum_by_course, get_student_progress
    
    courses = get_all_courses()
    overview = []
    
    for course in courses:
        modules = get_curriculum_by_course(course["id"])
        total_steps = sum(len(m.get("steps", [])) for m in modules)
        
        # 완료된 스텝 수 계산
        completed_steps = 0
        for module in modules:
            for step in module.get("steps", []):
                if step["id"] in _completed_steps:
                    completed_steps += 1
        
        completion_pct = round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
        
        overview.append({
            "id": course["id"],
            "title": course["title"],
            "instructor": course["instructor"],
            "description": course["description"],
            "level": course["level"],
            "module_count": len(modules),
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "completion_percentage": completion_pct,
        })
    
    return overview


def get_course_modules(course_id):
    """
    특정 과목의 모듈 목록과 각 모듈의 스텝을 반환합니다.
    
    Args:
        course_id: 과목 ID
        
    Returns:
        dict: 과목 정보 및 모듈(스텝 포함) 목록
    """
    from db_helper import get_curriculum_by_course
    
    courses = get_all_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    
    if not course:
        return None
    
    modules = get_curriculum_by_course(course_id)
    
    total_steps = sum(len(m.get("steps", [])) for m in modules)
    completed_steps = 0
    for module in modules:
        for step in module.get("steps", []):
            if step["id"] in _completed_steps:
                completed_steps += 1
    
    completion_pct = round((completed_steps / total_steps * 100), 1) if total_steps > 0 else 0
    
    return {
        "course": course,
        "modules": modules,
        "total_steps": total_steps,
        "completed_steps": completed_steps,
        "completion_percentage": completion_pct,
    }


def get_module_detail(module_id):
    """
    특정 모듈의 상세 정보(스텝 포함)를 반환합니다.
    
    Args:
        module_id: 모듈 ID
        
    Returns:
        dict: 모듈 정보 및 스텝 목록
    """
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM curriculum_modules WHERE id = ?;",
        (module_id,),
    )
    module = cursor.fetchone()
    
    if not module:
        conn.close()
        return None
    
    module = dict(module)
    
    cursor = conn.execute(
        "SELECT * FROM curriculum_steps WHERE module_id = ? ORDER BY order_num;",
        (module_id,),
    )
    steps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    module["steps"] = steps
    module["step_count"] = len(steps)
    module["course_id"] = module.get("course_id")
    
    return module


def get_step_detail(step_id):
    """
    개별 스텝의 상세 정보를 반환합니다.
    
    Args:
        step_id: 스텝 ID
        
    Returns:
        dict: 스텝 상세 정보 (지시문, 코드 예제, 예상 출력, 힌트 등)
    """
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
    
    if not step:
        conn.close()
        return None
    
    step = dict(step)
    conn.close()
    
    # 코드 예제, 예상 출력, 힌트 가져오기 (DB에서)
    code_example = step.get("code_example", "")
    expected_output = step.get("expected_output", "")
    
    # 힌트는 쉼표로 구분된 문자열 또는 JSON
    hints_raw = step.get("hints", "")
    if hints_raw:
        import json
        try:
            hints = json.loads(hints_raw)
        except (json.JSONDecodeError, TypeError):
            hints = [h.strip() for h in hints_raw.split(",") if h.strip()]
    else:
        hints = ["참고 자료를 확인하세요."]
    
    # 이전/다음 스텝 찾기
    course_id = step["course_id"]
    module_id = step["module_id"]
    
    modules = get_course_modules(course_id)
    prev_step = None
    next_step = None
    current_idx = -1
    
    for module in modules["modules"]:
        for i, s in enumerate(module["steps"]):
            if s["id"] == step_id:
                current_idx = i
                # 이전 스텝
                if i > 0:
                    prev_step = module["steps"][i - 1]
                else:
                    # 이전 모듈의 마지막 스텝
                    mod_idx = next(
                        (j for j, m in enumerate(modules["modules"]) if m["id"] == module_id),
                        -1,
                    )
                    if mod_idx > 0:
                        prev_mod = modules["modules"][mod_idx - 1]
                        if prev_mod["steps"]:
                            prev_step = prev_mod["steps"][-1]
                # 다음 스텝
                if i < len(module["steps"]) - 1:
                    next_step = module["steps"][i + 1]
                else:
                    # 다음 모듈의 첫 번째 스텝
                    mod_idx = next(
                        (j for j, m in enumerate(modules["modules"]) if m["id"] == module_id),
                        -1,
                    )
                    if mod_idx < len(modules["modules"]) - 1:
                        next_mod = modules["modules"][mod_idx + 1]
                        if next_mod["steps"]:
                            next_step = next_mod["steps"][0]
                break
    
    return {
        "step": step,
        "step_id": step_id,
        "course_id": course_id,
        "module_id": module_id,
        "module_title": step["module_title"],
        "code_example": code_example,
        "expected_output": expected_output,
        "hints": hints,
        "is_completed": step_id in _completed_steps,
        "prev_step": prev_step,
        "next_step": next_step,
    }


def get_db_connection():
    """데이터베이스 연결을 반환합니다."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "..", "shared", "db", "edu.db")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# 커리큘럼 모듈 기반 라우트 (Curriculum module-based routes)
# ============================================================

@app.route("/curriculum")
def curriculum():
    """
    커리큘럼 개요 페이지 - 모든 과목의 모듈과 진행 상황을 표시합니다.
    """
    overview = get_curriculum_overview()
    return render_template("curriculum.html", overview=overview)


@app.route("/curriculum/<int:course_id>")
def curriculum_detail(course_id):
    """
    과목 상세 페이지 - 특정 과목의 모듈 목록을 표시합니다.
    """
    detail = get_course_modules(course_id)
    
    if not detail:
        return render_template(
            "curriculum.html",
            overview=get_curriculum_overview(),
            error="과목을 찾을 수 없습니다.",
        )
    
    return render_template("curriculum_detail.html", detail=detail)


@app.route("/curriculum/<int:course_id>/step/<int:step_id>", methods=["GET"])
def curriculum_step(course_id, step_id):
    """
    개별 스텝 페이지 - 강의 내용, 코드 예제, 힌트, 완료 버튼을 표시합니다.
    """
    detail = get_step_detail(step_id)
    
    if not detail or detail["course_id"] != course_id:
        return redirect(url_for("curriculum"))
    
    return render_template("curriculum_step.html", detail=detail)


@app.route("/curriculum/<int:course_id>/step/<int:step_id>/complete", methods=["POST"])
def curriculum_step_complete(course_id, step_id):
    """
    스텝 완료 처리 API 엔드포인트.
    update_student_progress를 호출하여 진행 상황을 저장합니다.
    """
    from db_helper import update_student_progress
    
    # 기본 학생 ID (실제 환경에서는 세션/인증에서 가져옴)
    student_id = request.form.get("student_id", 1)
    
    success = update_student_progress(student_id, step_id, "completed")
    
    if success:
        _completed_steps.add(step_id)
    
    # AJAX 요청인지 확인
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": success, "step_id": step_id, "status": "completed"})
    
    # 일반 폼 제출인 경우 스텝 페이지로 리다이렉트
    return redirect(url_for("curriculum_step", course_id=course_id, step_id=step_id))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
