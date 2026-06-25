#!/usr/bin/env python3
"""
교육용 SQLite 데이터베이스 마이그레이션 스크립트
- curriculum_modules, curriculum_steps, student_progress 테이블 추가
- 4개 과목의 시드 데이터 삽입
"""

import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edu.db")

MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS curriculum_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    order_num INTEGER NOT NULL,
    estimated_minutes INTEGER DEFAULT 30,
    difficulty TEXT CHECK(difficulty IN ('beginner', 'intermediate', 'advanced')),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS curriculum_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    instruction TEXT,
    code_example TEXT,
    expected_output TEXT,
    hints TEXT,
    check_query TEXT,
    check_description TEXT,
    order_num INTEGER NOT NULL,
    FOREIGN KEY (module_id) REFERENCES curriculum_modules(id)
);

CREATE TABLE IF NOT EXISTS student_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    step_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
    completed_at TEXT,
    attempts INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (step_id) REFERENCES curriculum_steps(id)
);
"""

# Seed data: curriculum_modules
# (course_id, title, description, order_num, estimated_minutes, difficulty)
CURRICULUM_MODULES = [
    # Python 기초 (course_id=1)
    (1, "1. Python 설치하기", "파이썬 3.11 설치 및 개발 환경을 설정합니다. 터미널 사용법과 가상환경 생성을 배웁니다.", 1, 30, "beginner"),
    (1, "2. 변수와 자료형", "파이썬의 기본 자료형(숫자, 문자열, 리스트, 딕셔너리)을 이해하고 변수를 다룹니다.", 2, 45, "beginner"),
    (1, "3. 조건문과 반복문", "if/elif/else 조건문과 for, while 반복문을 사용하여 프로그램 흐름을 제어합니다.", 3, 50, "intermediate"),
    # Flask 웹개발 (course_id=2)
    (2, "1. Flask 설치", "Flask 프레임워크 설치와 가상환경 설정, 기본 앱 구조를 배웁니다.", 1, 30, "beginner"),
    (2, "2. 라우팅", "URL 라우팅과 HTTP 메서드(GET, POST)를 처리하는 뷰 함수를 작성합니다.", 2, 45, "intermediate"),
    (2, "3. 템플릿 렌더링", "Jinja2 템플릿 엔진을 활용하여 동적 웹 페이지를 생성합니다.", 3, 50, "intermediate"),
    # Node.js (course_id=3)
    (3, "1. Node.js 설치", "Node.js 런타임 설치와 npm 패키지 관리, 모듈 시스템을 이해합니다.", 1, 30, "beginner"),
    (3, "2. Express 기본", "Express 프레임워크의 기본 구조, 미들웨어, 라우팅을 배웁니다.", 2, 45, "intermediate"),
    (3, "3. REST API 만들기", "RESTful API 설계와 CRUD 구현, JSON 데이터 처리를 학습합니다.", 3, 50, "advanced"),
    # Streamlit 데이터 (course_id=4)
    (4, "1. Streamlit 설치", "Streamlit 설치와 기본 앱 구성, 다양한 위젯 사용법을 배웁니다.", 1, 30, "beginner"),
    (4, "2. 컴포넌트", "Streamlit의 다양한 컴포넌트(버튼, 슬라이더, 차트)를 활용합니다.", 2, 45, "intermediate"),
    (4, "3. 차트 그리기", "Matplotlib, Plotly를 연동하여 데이터를 시각화하고 대시보드를 만듭니다.", 3, 50, "intermediate"),
]

# Seed data: curriculum_steps
# (module_id, title, instruction, code_example, expected_output, hints, check_query, check_description, order_num)
CURRICULUM_STEPS = [
    # === Python 기초 - Module 1: Python 설치하기 ===
    (
        1, "1.1 Python 3.11 설치",
        "파이썬 공식 웹사이트(python.org)에서 Python 3.11을 다운로드하여 설치합니다. 설치 시 'Add Python to PATH' 옵션을 반드시 체크하세요. Windows에서는 설치 관리자에서, macOS에서는 brew install python@3.11 명령어를 사용할 수 있습니다.",
        "python --version",
        "Python 3.11.x",
        json.dumps(["터미널에서 python --version 명령어로 확인하세요", "PATH 환경변수를 확인하세요", "py --version 도 시도해보세요"]),
        "SELECT 1;",
        "파이썬이 정상적으로 설치되었는지 확인합니다.",
        1
    ),
    (
        1, "1.2 가상환경 생성",
        "프로젝트별로 독립된 파이썬 환경을 만들기 위해 가상환경을 생성합니다. python -m venv .venv 명령어로 가상환경을 만들고, source .venv/bin/activate (macOS) 또는 .venv\\Scripts\\activate (Windows)로 활성화합니다.",
        "python -m venv .venv\nsource .venv/bin/activate",
        "(.venv) 프롬프트가 표시됩니다",
        json.dumps([".venv 폴더가 생성되었는지 확인하세요", "activate 스크립트 경로를 확인하세요", "which python 으로 가상환경 파이썬인지 확인하세요"]),
        "SELECT 1;",
        "가상환경이 활성화되었는지 확인합니다.",
        2
    ),
    (
        1, "1.3 첫 번째 프로그램 실행",
        "터미널에서 파이썬 인터프리터를 실행하고 첫 번째 프로그램을 작성합니다. print() 함수를 사용하여 화면에 텍스트를 출력해봅니다.",
        "print('안녕하세요, 파이썬!')\nprint('내 첫 번째 프로그램입니다.')",
        "안녕하세요, 파이썬!\n내 첫 번째 프로그램입니다.",
        json.dumps(["print() 함수 안에 작은따옴표 또는 큰따옴표를 사용하세요", "괄호를 빠뜨리지 마세요", "세미콜론은 필요 없습니다"]),
        "SELECT 1;",
        "print() 함수로 텍스트가 정상 출력되는지 확인합니다.",
        3
    ),
    # === Python 기초 - Module 2: 변수와 자료형 ===
    (
        2, "2.1 변수와 숫자",
        "파이썬에서 변수를 선언하고 숫자 연산을 수행합니다. 파이썬은 타입 선언 없이 변수를 생성할 수 있습니다. 정수(int), 실수(float) 등 숫자형을 사용한 기본 연산을 연습합니다.",
        "name = '김민수'\nage = 25\nheight = 175.5\n\nprint(f'이름: {name}')\nprint(f'나이: {age}')\nprint(f'키: {height}')\nprint(f'10년 후 나이: {age + 10}')",
        "이름: 김민수\n나이: 25\n키: 175.5\n10년 후 나이: 35",
        json.dumps(["f-string을 사용하면 변수를 문자열 안에 삽입할 수 있습니다", "파이썬은 변수 타입을 자동으로 판단합니다", "사칙연산: +, -, *, /, //, %, **"]),
        "SELECT 1;",
        "변수에 저장된 값이 올바르게 출력되는지 확인합니다.",
        1
    ),
    (
        2, "2.2 문자열 다루기",
        "문자열(String)은 텍스트 데이터를 다루는 기본 자료형입니다. 문자열 슬라이싱, 포맷팅, 주요 메서드(upper, lower, split, join 등)를 연습합니다.",
        "text = '안녕하세요, 파이썬!'\n\nprint(text.upper())\nprint(text.lower())\nprint(text.split(','))\nprint(f'문자열 길이: {len(text)}')\nprint(text[0:5])",
        "안녕하세요, 파이썬!\n안녕하세요, 파이썬!\n['안녕하세요', ' 파이썬!']\n문자열 길이: 12\n안녕하세요",
        json.dumps(["인덱싱은 0부터 시작합니다", "슬라이싱은 text[start:end] 형식입니다", "upper(), lower()는 대소문자 변환입니다"]),
        "SELECT 1;",
        "문자열 메서드가 올바르게 동작하는지 확인합니다.",
        2
    ),
    (
        2, "2.3 리스트와 딕셔너리",
        "리스트(list)는 순서가 있는 데이터 집합이고, 딕셔너리(dict)는 키-값 쌍으로 데이터를 저장합니다. 데이터 추가, 삭제, 조회 등 기본 연산을 연습합니다.",
        "fruits = ['사과', '바나나', '오렌지']\nfruits.append('포도')\n\nstudent = {\n    'name': '김민수',\n    'age': 25,\n    'major': '컴퓨터공학'\n}\n\nprint(f'과일 목록: {fruits}')\nprint(f'학생 이름: {student[\"name\"]}')\nprint(f'전공: {student[\"major\"]}')",
        "과일 목록: ['사과', '바나나', '오렌지', '포도']\n학생 이름: 김민수\n전공: 컴퓨터공학",
        json.dumps(["리스트는 []로 생성하고 딕셔너리는 {}로 생성합니다", "append()로 요소를 추가합니다", "딕셔너리는 dict[key]로 값에 접근합니다"]),
        "SELECT 1;",
        "리스트와 딕셔너리 조작이 올바르게 동작하는지 확인합니다.",
        3
    ),
    # === Python 기초 - Module 3: 조건문과 반복문 ===
    (
        3, "3.1 if/elif/else 조건문",
        "조건문을 사용하여 프로그램의 실행 흐름을 제어합니다. if, elif, else 키워드를 사용하며, 비교 연산자와 논리 연산자를 결합하여 복잡한 조건을 만들 수 있습니다.",
        "score = 85\n\nif score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'\nelif score >= 70:\n    grade = 'C'\nelse:\n    grade = 'F'\n\nprint(f'점수: {score}, 학점: {grade}')",
        "점수: 85, 학점: B",
        json.dumps(["콜론(:)을 빠뜨리지 마세요", "들여쓰기(indentation)가 매우 중요합니다", "elif는 여러 개 사용 가능합니다"]),
        "SELECT 1;",
        "조건문이 올바르게 분기되는지 확인합니다.",
        1
    ),
    (
        3, "3.2 for 반복문",
        "for 반복문은 시퀀스(리스트, 문자열, range 등)의 요소를 순회합니다. range() 함수와 enumerate() 함수를 함께 사용하는 방법을 배웁니다.",
        "for i in range(5):\n    print(f'{i}번째 반복')\n\nprint('---')\n\nfruits = ['사과', '바나나', '오렌지']\nfor idx, fruit in enumerate(fruits, 1):\n    print(f'{idx}. {fruit}')",
        "0번째 반복\n1번째 반복\n2번째 반복\n3번째 반복\n4번째 반복\n---\n1. 사과\n2. 바나나\n3. 오렌지",
        json.dumps(["range(n)은 0부터 n-1까지 생성합니다", "enumerate()는 인덱스와 값을 함께 반환합니다", "for 루프 안에서도 들여쓰기를 유지하세요"]),
        "SELECT 1;",
        "for 반복문이 올바르게 순회하는지 확인합니다.",
        2
    ),
    (
        3, "3.3 while 반복문과 제어",
        "while 반복문은 조건이 참인 동안 계속 반복합니다. break와 continue를 사용하여 반복문을 제어하는 방법을 배웁니다.",
        "count = 0\nwhile count < 5:\n    if count == 2:\n        count += 1\n        continue\n    if count == 4:\n        break\n    print(f'카운트: {count}')\n    count += 1\n\nprint('반복 종료')",
        "카운트: 0\n카운트: 1\n카운트: 3\n반복 종료",
        json.dumps(["while 문은 종료 조건이 있어야 합니다", "break는 반복문을 즉시 종료합니다", "continue는 현재 반복을 건너뜁니다"]),
        "SELECT 1;",
        "while 반복문과 break/continue가 올바르게 동작하는지 확인합니다.",
        3
    ),
    # === Flask 웹개발 - Module 1: Flask 설치 ===
    (
        4, "4.1 Flask 설치",
        "Flask 프레임워크를 설치합니다. 먼저 가상환경을 생성하고 활성화한 후 pip install flask 명령어로 Flask를 설치합니다.",
        "pip install flask",
        "Successfully installed flask-3.x.x ...",
        json.dumps(["가상환경을 먼저 활성화하세요", "pip 최신 버전으로 업그레이드: pip install --upgrade pip", "pip list로 설치 확인 가능합니다"]),
        "SELECT 1;",
        "Flask가 정상적으로 설치되었는지 확인합니다.",
        1
    ),
    (
        4, "4.2 기본 Flask 앱 만들기",
        "가장 기본적인 Flask 애플리케이션을 만듭니다. Flask 클래스로 앱 인스턴스를 생성하고, 라우트 데코레이터로 URL을 매핑합니다.",
        "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return '안녕하세요, Flask!'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
        " * Running on http://127.0.0.1:5000",
        json.dumps(["Flask(__name__)으로 앱을 생성합니다", "@app.route('/') 데코레이터로 URL을 연결합니다", "debug=True로 설정하면 자동 재시작됩니다"]),
        "SELECT 1;",
        "Flask 앱이 정상적으로 실행되는지 확인합니다.",
        2
    ),
    (
        4, "4.3 가상환경 설정 파일 관리",
        "프로젝트의 의존성을 관리하기 위해 requirements.txt 파일을 생성하고 사용하는 방법을 배웁니다.",
        "pip freeze > requirements.txt\npip install -r requirements.txt",
        "의존성이 정상적으로 설치됩니다",
        json.dumps(["requirements.txt에 패키지 목록이 저장됩니다", "다른 환경에서도 동일한 패키지를 설치할 수 있습니다", ".gitignore에 가상환경 폴더를 추가하세요"]),
        "SELECT 1;",
        "requirements.txt가 올바르게 생성되었는지 확인합니다.",
        3
    ),
    # === Flask 웹개발 - Module 2: 라우팅 ===
    (
        5, "5.1 기본 URL 라우팅",
        "Flask에서 URL 경로를 뷰 함수에 연결하는 기본 라우팅 방법을 배웁니다. 정적 경로와 동적 경로(변수 사용)를 모두 다룹니다.",
        "@app.route('/')\ndef home():\n    return '홈페이지'\n\n@app.route('/about')\ndef about():\n    return '소개 페이지'\n\n@app.route('/user/<username>')\ndef show_user(username):\n    return f'사용자: {username}'",
        "브라우저에서 /user/김민수 접속 시: 사용자: 김민수",
        json.dumps(["<variable> 형식으로 동적 경로를 정의합니다", "기본적으로 GET 메서드만 처리합니다", "url_for()로 URL을 생성할 수 있습니다"]),
        "SELECT 1;",
        "라우팅이 올바르게 동작하는지 확인합니다.",
        1
    ),
    (
        5, "5.2 HTTP 메서드 처리",
        "GET과 POST 메서드를 구분하여 처리하는 방법을 배웁니다. 폼 데이터를 처리하고 리다이렉트하는 방법을 연습합니다.",
        "from flask import request, redirect, url_for\n\n@app.route('/login', methods=['GET', 'POST'])\ndef login():\n    if request.method == 'POST':\n        username = request.form['username']\n        return redirect(url_for('home'))\n    return '''\n    <form method='POST'>\n        <input type='text' name='username'>\n        <button type='submit'>로그인</button>\n    </form>\n    '''",
        "POST 요청 시 리다이렉트됨",
        json.dumps(["methods 파라미터로 허용할 HTTP 메서드를 지정합니다", "request.form으로 폼 데이터를 가져옵니다", "redirect()와 url_for()를 함께 사용합니다"]),
        "SELECT 1;",
        "GET/POST 메서드가 올바르게 처리되는지 확인합니다.",
        2
    ),
    (
        5, "5.3 에러 처리",
        "HTTP 에러(404, 500 등)에 대한 사용자 정의 에러 페이지를 만드는 방법을 배웁니다.",
        "from flask import render_template\n\n@app.errorhandler(404)\ndef not_found(error):\n    return render_template('404.html'), 404\n\n@app.errorhandler(500)\ndef server_error(error):\n    return render_template('500.html'), 500",
        "404 에러 발생 시 사용자 정의 페이지 표시",
        json.dumps(["@app.errorhandler(코드) 데코레이터를 사용합니다", "에러 코드를 반환해야 합니다", "템플릿 파일을 templates/ 폴더에 저장하세요"]),
        "SELECT 1;",
        "에러 핸들러가 올바르게 동작하는지 확인합니다.",
        3
    ),
    # === Flask 웹개발 - Module 3: 템플릿 렌더링 ===
    (
        6, "6.1 Jinja2 템플릿 기본",
        "Jinja2 템플릿 엔진을 사용하여 동적 HTML 페이지를 생성합니다. render_template() 함수로 템플릿을 로드하고 변수를 전달합니다.",
        "from flask import render_template\n\n@app.route('/hello/<name>')\ndef hello(name):\n    return render_template('hello.html', username=name)",
        "templates/hello.html: <h1>안녕하세요, {{ username }}!</h1>",
        json.dumps(["templates/ 폴더에 HTML 파일을 저장하세요", "{{ 변수 }} 로 변수를 출력합니다", "{% 제어문 %} 로 로직을 처리합니다"]),
        "SELECT 1;",
        "템플릿이 올바르게 렌더링되는지 확인합니다.",
        1
    ),
    (
        6, "6.2 템플릿 제어문",
        "Jinja2에서 조건문(if)과 반복문(for)을 사용하는 방법을 배웁니다. 템플릿 상속(template inheritance)도 알아봅니다.",
        "{% extends 'base.html' %}\n\n{% block content %}\n{% if users %}\n    <ul>\n    {% for user in users %}\n        <li>{{ user.name }}</li>\n    {% endfor %}\n    </ul>\n{% else %}\n    <p>사용자가 없습니다.</p>\n{% endif %}\n{% endblock %}",
        "사용자 목록이 렌더링되거나 '사용자가 없습니다' 표시",
        json.dumps(["{% extends %}로 부모 템플릿을 상속합니다", "{% block %}으로 교체 가능한 영역을 정의합니다", "{% for item in items %} 형식으로 반복합니다"]),
        "SELECT 1;",
        "템플릿 제어문이 올바르게 동작하는지 확인합니다.",
        2
    ),
    (
        6, "6.3 폼 처리와 파일 업로드",
        "HTML 폼에서 데이터를 받고 파일을 업로드하는 방법을 배웁니다. request.files로 업로드된 파일을 처리합니다.",
        "from flask import request\nfrom werkzeug.utils import secure_filename\n\n@app.route('/upload', methods=['GET', 'POST'])\ndef upload():\n    if request.method == 'POST':\n        file = request.files['file']\n        if file:\n            filename = secure_filename(file.filename)\n            file.save(f'uploads/{filename}')\n            return '업로드 완료!'\n    return render_template('upload.html')",
        "파일이 업로드되고 '업로드 완료!' 메시지 표시",
        json.dumps(["enctype='multipart/form-data'를 설정하세요", "secure_filename()으로 파일명을 안전하게 처리하세요", "업로드 폴더를 미리 생성하세요"]),
        "SELECT 1;",
        "파일 업로드가 올바르게 처리되는지 확인합니다.",
        3
    ),
    # === Node.js - Module 1: Node.js 설치 ===
    (
        7, "7.1 Node.js 설치",
        "Node.js 공식 웹사이트에서 LTS 버전을 다운로드하여 설치합니다. 또는 nvm(Node Version Manager)을 사용하여 여러 버전을 관리할 수 있습니다.",
        "node --version\nnpm --version",
        "v20.x.x\n10.x.x",
        json.dumps(["LTS 버전을 권장합니다", "nvm use 20 으로 버전 전환 가능", "node -v 로 버전 확인"]),
        "SELECT 1;",
        "Node.js가 정상적으로 설치되었는지 확인합니다.",
        1
    ),
    (
        7, "7.2 npm과 패키지 관리",
        "npm(Node Package Manager)을 사용하여 패키지를 설치하고 관리합니다. package.json 파일을 생성하고 의존성을 관리하는 방법을 배웁니다.",
        "npm init -y\nnpm install express",
        "package.json이 생성되고 node_modules에 패키지 설치",
        json.dumps(["npm init -y 로 기본 package.json 생성", "npm install 패키지명 으로 설치", "package.json의 dependencies에 자동 기록됩니다"]),
        "SELECT 1;",
        "npm 패키지가 정상적으로 설치되었는지 확인합니다.",
        2
    ),
    (
        7, "7.3 첫 번째 서버 실행",
        "Node.js로 간단한 HTTP 서버를 만들고 실행합니다. http 모듈을 사용하여 기본 서버를 구성합니다.",
        "const http = require('http');\n\nconst server = http.createServer((req, res) => {\n    res.writeHead(200, { 'Content-Type': 'text/plain' });\n    res.end('안녕하세요, Node.js!');\n});\n\nserver.listen(3000, () => {\n    console.log('서버 실행 중: http://localhost:3000');\n});",
        "서버 실행 중: http://localhost:3000",
        json.dumps(["require()로 모듈을 가져옵니다", "createServer()로 서버를 생성합니다", "listen(포트, 콜백)으로 서버를 시작합니다"]),
        "SELECT 1;",
        "Node.js 서버가 정상적으로 실행되는지 확인합니다.",
        3
    ),
    # === Node.js - Module 2: Express 기본 ===
    (
        8, "8.1 Express 설치와 기본 앱",
        "Express 프레임워크를 설치하고 기본 애플리케이션을 만듭니다. Express는 Node.js에서 가장 널리 사용되는 웹 프레임워크입니다.",
        "const express = require('express');\nconst app = express();\n\napp.get('/', (req, res) => {\n    res.send('Express 시작하기');\n});\n\napp.listen(3000, () => {\n    console.log('Express 서버 실행 중');\n});",
        "Express 서버 실행 중",
        json.dumps(["npm install express 로 설치", "app.get(path, handler)로 GET 라우트 등록", "req(요청), res(응답) 객체를 사용합니다"]),
        "SELECT 1;",
        "Express 앱이 정상적으로 실행되는지 확인합니다.",
        1
    ),
    (
        8, "8.2 미들웨어 사용",
        "Express 미들웨어는 요청-응답 사이클에 접근할 수 있는 함수입니다. 로깅, 본문 파싱, CORS 처리 등 다양한 미들웨어를 사용합니다.",
        "const express = require('express');\nconst app = express();\n\n// 로깅 미들웨어\napp.use((req, res, next) => {\n    console.log(`${req.method} ${req.url}`);\n    next();\n});\n\n// JSON 파싱\napp.use(express.json());\n\napp.post('/data', (req, res) => {\n    res.json({ received: req.body });\n});",
        "콘솔에 요청 로그가 출력됨",
        json.dumps(["app.use()로 미들웨어를 등록합니다", "next()를 호출해야 다음 미들웨어로 넘어갑니다", "express.json()으로 JSON 본문을 파싱합니다"]),
        "SELECT 1;",
        "미들웨어가 올바르게 동작하는지 확인합니다.",
        2
    ),
    (
        8, "8.3 라우터 분리",
        "라우터를 모듈화하여 코드를 깔끔하게 관리합니다. express.Router()를 사용하여 관련 라우트를 그룹화합니다.",
        "const express = require('express');\nconst router = express.Router();\n\nrouter.get('/users', (req, res) => {\n    res.json([{ id: 1, name: '김민수' }]);\n});\n\nrouter.post('/users', (req, res) => {\n    res.status(201).json({ message: '사용자 생성 완료' });\n});\n\nmodule.exports = router;",
        "/api/users 경로로 요청 처리",
        json.dumps(["express.Router()로 라우터를 생성합니다", "모듈 마지막에 module.exports = router", "메인 앱에서 app.use('/api', router)로 연결합니다"]),
        "SELECT 1;",
        "라우터가 올바르게 분리되었는지 확인합니다.",
        3
    ),
    # === Node.js - Module 3: REST API 만들기 ===
    (
        9, "9.1 REST API 설계",
        "RESTful API의 기본 원칙과 HTTP 메서드(GET, POST, PUT, DELETE)를 활용한 CRUD API를 설계합니다.",
        "// GET    /api/todos - 목록 조회\n// POST   /api/todos - 생성\n// PUT    /api/todos/:id - 수정\n// DELETE /api/todos/:id - 삭제\n\napp.get('/api/todos', (req, res) => {\n    res.json(todos);\n});\n\napp.post('/api/todos', (req, res) => {\n    const newTodo = { id: Date.now(), ...req.body };\n    todos.push(newTodo);\n    res.status(201).json(newTodo);\n});",
        "RESTful API 엔드포인트가 응답함",
        json.dumps(["GET은 조회, POST는 생성에 사용합니다", "적절한 HTTP 상태 코드를 반환합니다", "리소스명은 복수형 명사를 사용합니다"]),
        "SELECT 1;",
        "REST API가 올바르게 설계되었는지 확인합니다.",
        1
    ),
    (
        9, "9.2 JSON 응답과 에러 처리",
        "API에서 JSON 형식으로 응답하고, 에러를 적절히 처리하는 방법을 배웁니다.",
        "app.get('/api/todos/:id', (req, res) => {\n    const todo = todos.find(t => t.id === parseInt(req.params.id));\n    if (!todo) {\n        return res.status(404).json({ error: '찾을 수 없습니다' });\n    }\n    res.json(todo);\n});\n\n// 전역 에러 핸들러\napp.use((err, req, res, next) => {\n    res.status(500).json({ error: err.message });\n});",
        "404 또는 200과 JSON 응답",
        json.dumps(["res.json()으로 JSON 응답을 보냅니다", "res.status(코드)로 HTTP 상태 코드를 설정합니다", "에러 핸들러는 4개의 파라미터를 받습니다"]),
        "SELECT 1;",
        "JSON 응답과 에러 처리가 올바른지 확인합니다.",
        2
    ),
    (
        9, "9.3 CORS와 데이터베이스 연동",
        "CORS(Cross-Origin Resource Sharing)를 설정하고, SQLite 데이터베이스와 연동하는 방법을 배웁니다.",
        "const cors = require('cors');\nconst Database = require('better-sqlite3');\n\napp.use(cors());\n\nconst db = new Database('app.db');\n\napp.get('/api/todos', (req, res) => {\n    const todos = db.prepare('SELECT * FROM todos').all();\n    res.json(todos);\n});",
        "CORS가 설정되고 DB 데이터가 반환됨",
        json.dumps(["npm install cors 로 CORS 패키지 설치", "better-sqlite3로 SQLite 사용", "cors() 미들웨어를 전체 앱에 적용"]),
        "SELECT 1;",
        "CORS와 DB 연동이 올바르게 동작하는지 확인합니다.",
        3
    ),
    # === Streamlit 데이터 - Module 1: Streamlit 설치 ===
    (
        10, "10.1 Streamlit 설치",
        "Streamlit을 설치합니다. pip install streamlit 명령어로 설치하며, 가상환경 내에서 실행하는 것을 권장합니다.",
        "pip install streamlit",
        "Successfully installed streamlit-1.x.x ...",
        json.dumps(["파이썬 3.8 이상이 필요합니다", "가상환경을 사용하세요", "streamlit --version 으로 확인"]),
        "SELECT 1;",
        "Streamlit이 정상적으로 설치되었는지 확인합니다.",
        1
    ),
    (
        10, "10.2 기본 앱 만들기",
        "가장 기본적인 Streamlit 앱을 만들고 실행합니다. st.title(), st.write() 등 기본 함수를 사용합니다.",
        "import streamlit as st\n\nst.title('내 첫 Streamlit 앱')\nst.write('안녕하세요! 이것은 제 첫 번째 앱입니다.')\n\nif st.button('인사하기'):\n    st.write('반갑습니다! 🎉')",
        "웹 브라우저에 앱이 표시됨",
        json.dumps(["streamlit run app.py 로 실행", "st.title()로 제목 설정", "st.write()로 텍스트 출력"]),
        "SELECT 1;",
        "Streamlit 앱이 정상적으로 실행되는지 확인합니다.",
        2
    ),
    (
        10, "10.3 위젯 사용법",
        "Streamlit의 다양한 위젯(버튼, 슬라이더, 텍스트 입력, 셀렉트 박스)을 사용하는 방법을 배웁니다.",
        "import streamlit as st\n\nname = st.text_input('이름을 입력하세요')\nage = st.slider('나이를 선택하세요', 0, 100, 25)\ncolor = st.selectbox('좋아하는 색상', ['빨강', '파랑', '초록'])\n\nst.write(f'{name}님은 {age}살이고, {color}을 좋아합니다.')",
        "위젯 값에 따라 출력이 변경됨",
        json.dumps(["st.text_input()로 텍스트 입력", "st.slider(라벨, 최소, 최대, 기본값)", "st.selectbox()로 선택 목록 생성"]),
        "SELECT 1;",
        "위젯이 올바르게 동작하는지 확인합니다.",
        3
    ),
    # === Streamlit 데이터 - Module 2: 컴포넌트 ===
    (
        11, "11.1 데이터프레임 표시",
        "Pandas 데이터프레임을 Streamlit에 표시합니다. st.dataframe()과 st.table()을 사용하여 데이터를 시각화합니다.",
        "import streamlit as st\nimport pandas as pd\n\ndf = pd.DataFrame({\n    '이름': ['김민수', '이서연', '박지훈'],\n    '나이': [25, 23, 27],\n    '점수': [95, 88, 92]\n})\n\nst.dataframe(df)\nst.table(df)",
        "데이터프레임이 대화형으로 표시됨",
        json.dumps(["st.dataframe()은 대화형, st.table()은 정적 테이블", "pandas로 데이터프레임 생성", "st.dataframe(df.style.highlight_max())로 강조 가능"]),
        "SELECT 1;",
        "데이터프레임이 올바르게 표시되는지 확인합니다.",
        1
    ),
    (
        11, "11.2 사이드바와 레이아웃",
        "사이드바를 추가하고 컬럼 레이아웃을 구성하여 앱의 레이아웃을 개선합니다.",
        "import streamlit as st\n\n# 사이드바\nwith st.sidebar:\n    st.title('설정')\n    option = st.selectbox('옵션 선택', ['A', 'B', 'C'])\n\n# 메인 영역 컬럼 분할\ncol1, col2 = st.columns(2)\n\nwith col1:\n    st.metric('방문자 수', '1,234', '+10%')\n\nwith col2:\n    st.metric('매출', '₩5,000,000', '+25%')",
        "사이드바와 2개 컬럼이 표시됨",
        json.dumps(["st.sidebar에 위젯을 배치", "st.columns(n)으로 n분할", "st.metric()으로 지표 표시"]),
        "SELECT 1;",
        "레이아웃이 올바르게 구성되었는지 확인합니다.",
        2
    ),
    (
        11, "11.3 파일 업로드와 다운로드",
        "사용자가 파일을 업로드하고 처리한 후 결과를 다운로드할 수 있는 기능을 구현합니다.",
        "import streamlit as st\nimport pandas as pd\n\nuploaded_file = st.file_uploader('CSV 파일을 업로드하세요', type=['csv'])\n\nif uploaded_file:\n    df = pd.read_csv(uploaded_file)\n    st.dataframe(df)\n    \n    csv = df.to_csv(index=False).encode('utf-8')\n    st.download_button('다운로드', csv, 'result.csv', 'text/csv')",
        "파일 업로드 후 데이터 표시 및 다운로드 가능",
        json.dumps(["st.file_uploader()로 파일 업로드", "pandas로 CSV 처리", "st.download_button()으로 다운로드 제공"]),
        "SELECT 1;",
        "파일 업로드/다운로드가 올바르게 동작하는지 확인합니다.",
        3
    ),
    # === Streamlit 데이터 - Module 3: 차트 그리기 ===
    (
        12, "12.1 Matplotlib 차트",
        "Matplotlib으로 차트를 그리고 Streamlit에 표시합니다. st.pyplot()로 Matplotlib 그래프를 렌더링합니다.",
        "import streamlit as st\nimport matplotlib.pyplot as plt\nimport numpy as np\n\nx = np.linspace(0, 10, 100)\ny = np.sin(x)\n\nfig, ax = plt.subplots()\nax.plot(x, y, label='sin(x)')\nax.set_title('사인 파동')\nax.legend()\n\nst.pyplot(fig)",
        "사인 파동 그래프가 표시됨",
        json.dumps(["plt.subplots()로 그래프 생성", "st.pyplot(fig)로 Streamlit에 표시", "한글 폰트 설정이 필요할 수 있습니다"]),
        "SELECT 1;",
        "Matplotlib 차트가 올바르게 렌더링되는지 확인합니다.",
        1
    ),
    (
        12, "12.2 Plotly 인터랙티브 차트",
        "Plotly를 사용하여 인터랙티브한 차트를 만듭니다. st.plotly_chart()로 Plotly 그래프를 표시합니다.",
        "import streamlit as st\nimport plotly.express as px\n\ndf = px.data.gapminder().query('year == 2007')\nfig = px.scatter(df, x='gdpPercap', y='lifeExp',\n                 size='pop', color='continent',\n                 hover_name='country', log_x=True,\n                 title='GDP vs 기대수명')\n\nst.plotly_chart(fig, use_container_width=True)",
        "인터랙티브 산점도가 표시됨",
        json.dumps(["pip install plotly 로 설치", "st.plotly_chart()로 렌더링", "use_container_width=True로 전체 너비 사용"]),
        "SELECT 1;",
        "Plotly 차트가 올바르게 렌더링되는지 확인합니다.",
        2
    ),
    (
        12, "12.3 Streamlit 내장 차트",
        "Streamlit에 내장된 간단한 차트 함수를 사용합니다. st.line_chart, st.bar_chart, st.area_chart 등을 활용합니다.",
        "import streamlit as st\nimport pandas as pd\nimport numpy as np\n\nchart_data = pd.DataFrame(\n    np.random.randn(20, 3),\n    columns=['A', 'B', 'C']\n)\n\nst.line_chart(chart_data)\nst.bar_chart(chart_data)\nst.area_chart(chart_data)",
        "라인, 바, 에어리어 차트가 표시됨",
        json.dumps(["st.line_chart(data)로 라인 차트", "st.bar_chart(data)로 바 차트", "데이터프레임을 직접 전달하면 자동 범례 생성"]),
        "SELECT 1;",
        "내장 차트가 올바르게 표시되는지 확인합니다.",
        3
    ),
]

# Sample student_progress data
# (student_id, step_id, status, completed_at, attempts)
STUDENT_PROGRESS = [
    (1, 1, 'completed', '2025-01-15 10:30:00', 1),
    (1, 2, 'completed', '2025-01-15 11:00:00', 2),
    (1, 3, 'in_progress', None, 1),
    (2, 1, 'completed', '2025-01-16 09:00:00', 1),
    (2, 2, 'not_started', None, 0),
    (3, 7, 'completed', '2025-01-17 14:00:00', 1),
    (3, 8, 'in_progress', None, 2),
    (4, 10, 'completed', '2025-01-18 10:00:00', 1),
    (5, 4, 'completed', '2025-01-19 11:00:00', 1),
    (5, 5, 'completed', '2025-01-19 11:30:00', 1),
    (5, 6, 'in_progress', None, 1),
]


def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create new tables
    cursor.executescript(MIGRATION_SQL)
    print("✅ 테이블 생성 완료: curriculum_modules, curriculum_steps, student_progress")

    # Insert curriculum modules
    cursor.executemany(
        "INSERT INTO curriculum_modules (course_id, title, description, order_num, estimated_minutes, difficulty) VALUES (?, ?, ?, ?, ?, ?);",
        CURRICULUM_MODULES,
    )
    print(f"✅ 모듈 {len(CURRICULUM_MODULES)}개 삽입 완료")

    # Insert curriculum steps
    cursor.executemany(
        "INSERT INTO curriculum_steps (module_id, title, instruction, code_example, expected_output, hints, check_query, check_description, order_num) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
        CURRICULUM_STEPS,
    )
    print(f"✅ 스텝 {len(CURRICULUM_STEPS)}개 삽입 완료")

    # Insert student progress
    cursor.executemany(
        "INSERT INTO student_progress (student_id, step_id, status, completed_at, attempts) VALUES (?, ?, ?, ?, ?);",
        STUDENT_PROGRESS,
    )
    print(f"✅ 학생 진행 {len(STUDENT_PROGRESS)}건 삽입 완료")

    conn.commit()

    # Verify
    print("\n--- 데이터 확인 ---")
    for table in ["curriculum_modules", "curriculum_steps", "student_progress"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count}건")

    # Verify modules per course
    print("\n--- 과목별 모듈 수 ---")
    cursor.execute("""
        SELECT c.title, COUNT(cm.id) as module_count
        FROM courses c
        LEFT JOIN curriculum_modules cm ON c.id = cm.course_id
        GROUP BY c.id
        ORDER BY c.id;
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}개 모듈")

    # Verify steps per module
    print("\n--- 모듈별 스텝 수 ---")
    cursor.execute("""
        SELECT cm.title, COUNT(cs.id) as step_count
        FROM curriculum_modules cm
        LEFT JOIN curriculum_steps cs ON cm.id = cs.module_id
        GROUP BY cm.id
        ORDER BY cm.id;
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}개 스텝")

    conn.close()
    print(f"\n✅ 마이그레이션 완료: {DB_PATH}")


if __name__ == "__main__":
    run_migration()
