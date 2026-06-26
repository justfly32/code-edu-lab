#!/usr/bin/env python3
"""
=============================================================================
📚 교육용 SQLite 데이터베이스 시드(Seed) 스크립트 — 완전 주석 버전
=============================================================================

[모듈 개요]
이 스크립트는 code-edu-lab 프로젝트의 학습 관리 시스템(LMS)을 위한
SQLite 데이터베이스를 처음부터 생성하고, 예제 데이터를 채워넣는(Seeding)
역할을 합니다.

[전체 흐름 (Flow)]
1. 기존 데이터베이스 파일(edu.db)이 있으면 삭제 → 완전히 새로운 상태에서 시작
2. SQLite 연결 및 외래 키(PRAGMA foreign_keys) 활성화
3. CREATE TABLE 문을 실행하여 5개 테이블(students, courses, enrollments, lessons, submissions) 생성
4. 각 테이블에 예제 데이터 INSERT (학생 8명, 과목 4개, 강의 12개, 수강신청 20건, 제출18건)
5. 집계 UPDATE 쿼리로 students.course_count와 courses.student_count 값을 계산하여 갱신
6. 변경사항 COMMIT 및 각 테이블 건수 확인 (VERIFY)
7. 연결 종료 및 완료 메시지 출력

[대상 독자]
- SQLite / 관계형 데이터베이스를 처음 배우는 학생
- Python sqlite3 모듈을 공부하는 개발자
- SQL CREATE TABLE, INSERT, UPDATE, 서브쿼리 등을 실습하는 교육생

[핵심 학습 포인트]
- SQLite 데이터 타입과 제약조건 (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, DEFAULT)
- AUTOINCREMENT의 의미와 사용 이유
- datetime('now') 함수로 생성 시각 자동 기록
- executemany()로 여러 행을 한 번에 INSERT
- 서브쿼리(Subquery)를 활용한 집계 UPDATE
- PRAGMA foreign_keys의 역할

데이터베이스 파일 위치: shared/db/edu.db (이 파일과 같은 디렉토리)
"""

import sqlite3
import os

# =========================================================================
# 📍 데이터베이스 파일 경로 설정
# =========================================================================
# __file__: 이 스크립트 파일(seed.py)의 절대 경로
# os.path.dirname(): 부모 디렉토리 경로 추출
# os.path.abspath(): 상대 경로를 절대 경로로 변환
# os.path.join(): OS에 맞는 경로 구분자로 결합
# 결과: ~/projects/code-edu-lab/shared/db/edu.db
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edu.db")

# =========================================================================
# 📐 데이터베이스 스키마 (테이블 구조) 정의
# =========================================================================
# executescript()로 한 번에 여러 CREATE TABLE 문을 실행합니다.
# 각 테이블마다 상세한 교육용 주석이 포함되어 있습니다.
SCHEMA_SQL = """
-- ---------------------------------------------------------------------
-- 📋 students 테이블 -- 학생 정보 저장
-- ---------------------------------------------------------------------
-- 이 테이블은 시스템에 등록된 학생들의 개인정보와 학습 현황을 저장합니다.
-- 각 학생은 고유한 ID로 식별되며, 이메일은 중복될 수 없습니다.
--
-- 컬럼 설명:
--   id           INTEGER  : 고유 식별자 (자동 증가, PRIMARY KEY)
--                            👉 PRIMARY KEY: 각 행을 유일하게 식별하는 기본 키
--                            👉 AUTOINCREMENT: 새 행 추가 시 자동으로 1씩 증가
--                               (id 값을 직접 지정하지 않아도 됨)
--   name         TEXT     : 학생 이름 (NOT NULL -- 반드시 값이 있어야 함)
--   email        TEXT     : 이메일 주소 (UNIQUE + NOT NULL)
--                            👉 UNIQUE: 중복 값을 허용하지 않음 (같은 이메일로
--                               두 명이 가입할 수 없음)
--   created_at   TEXT     : 가입 일시 (DEFAULT = datetime('now'))
--                            👉 datetime('now'): SQLite 내장 함수로, 현재 UTC
--                               시각을 'YYYY-MM-DD HH:MM:SS' 형식의 문자열로 반환
--                            👉 DEFAULT: 값을 생략하면 자동으로 현재 시각 입력
--   course_count INTEGER  : 수강 중인 과목 수 (기본값 0)
--                            (나중에 UPDATE 서브쿼리로 자동 계산됨)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    course_count INTEGER DEFAULT 0
);

/*
-----------------------------------------------------------------------
📋 courses 테이블 — 과목(강좌) 정보 저장
-----------------------------------------------------------------------
교육 기관에서 제공하는 과목들의 정보를 저장합니다.
각 과목은 제목, 강사, 설명, 난이도 레벨을 가집니다.

컬럼 설명:
  id             INTEGER  : 고유 식별자 (PRIMARY KEY, AUTOINCREMENT)
  title          TEXT     : 과목 제목 (NOT NULL)
  instructor     TEXT     : 강사 이름 (NOT NULL)
  description    TEXT     : 과목 설명 (NULL 허용 — 생략 가능)
  level          TEXT     : 난이도 (초급/중급/고급 중 하나만 허용)
                             👉 CHECK(level IN ('초급', '중급', '고급')):
                                이 컬럼에 입력될 수 있는 값을 제한하는 제약조건
                                '초급', '중급', '고급' 외의 값이 들어오면 오류 발생
  student_count INTEGER  : 수강 중인 학생 수 (기본값 0)
                             (나중에 UPDATE 서브쿼리로 자동 계산됨)
-----------------------------------------------------------------------
*/
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    instructor TEXT NOT NULL,
    description TEXT,
    level TEXT CHECK(level IN ('초급', '중급', '고급')),
    student_count INTEGER DEFAULT 0
);

/*
-----------------------------------------------------------------------
📋 enrollments 테이블 — 수강 신청(등록) 정보 저장
-----------------------------------------------------------------------
학생이 어떤 과목을 수강 신청했는지 저장하는 연결 테이블입니다.
students 테이블과 courses 테이블 사이의 '다대다(N:M)' 관계를 구현합니다.
→ 한 학생이 여러 과목을 수강할 수 있고, 한 과목에 여러 학생이 등록 가능

컬럼 설명:
  id           INTEGER  : 고유 식별자 (PRIMARY KEY, AUTOINCREMENT)
  student_id   INTEGER  : 학생 ID (NOT NULL, FOREIGN KEY)
                           👉 FOREIGN KEY: 다른 테이블의 PRIMARY KEY를 참조
                              student_id는 students(id)를 참조
                              → 이 학생이 실제로 존재하는지 데이터베이스가 검증
  course_id    INTEGER  : 과목 ID (NOT NULL, FOREIGN KEY)
                           👉 FOREIGN KEY: courses(id)를 참조
                              → 이 과목이 실제로 존재하는지 검증
  enrolled_at  TEXT     : 수강 신청 일시 (DEFAULT = datetime('now'))
  grade        TEXT     : 최종 성적 (NULL 허용 — 아직 성적 미부여 가능)
                           👉 NULL: "값이 없음"을 의미 (0이나 ''과 다름)

외래 키 제약조건의 효과:
  - 존재하지 않는 학생 ID로 수강신청을 넣으면 오류 발생
  - 한 학생이 삭제되면 그 학생의 수강신청 기록도 함께 처리 고려 필요
    (현재는 ON DELETE CASCADE 등이 없어 별도 처리 필요)
-----------------------------------------------------------------------
*/
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TEXT DEFAULT (datetime('now')),
    grade TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

/*
-----------------------------------------------------------------------
📋 lessons 테이블 — 강의(레슨) 정보 저장
-----------------------------------------------------------------------
각 과목(courses) 안에 포함된 개별 강의 단위입니다.
한 과목은 여러 개의 강의(레슨)로 구성됩니다 (1:N 관계).

컬럼 설명:
  id            INTEGER  : 고유 식별자 (PRIMARY KEY, AUTOINCREMENT)
  course_id     INTEGER  : 소속 과목 ID (NOT NULL, FOREIGN KEY)
                            👉 courses(id)를 참조 → 이 강의가 어떤 과목
                               소속인지 지정
  title         TEXT     : 강의 제목 (NOT NULL)
  content       TEXT     : 강의 내용/설명 (NULL 허용)
  order_num     INTEGER  : 과목 내에서의 강의 순서 (NOT NULL)
                            👉 1, 2, 3, ... 순서로 표시 순서 결정
  duration_min  INTEGER  : 예상 소요 시간(분) (DEFAULT 30)

참고: order_num은 과목 내에서 유일해야 논리적으로 맞지만,
      현재 스키마에는 UNIQUE(course_id, order_num) 제약이 없습니다.
      (교육용 실습 과제로留给 학생들이 직접 추가해볼 수 있음)
-----------------------------------------------------------------------
*/
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    order_num INTEGER NOT NULL,
    duration_min INTEGER DEFAULT 30,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

/*
-----------------------------------------------------------------------
📋 submissions 테이블 — 과제 제출 정보 저장
-----------------------------------------------------------------------
학생이 특정 강의(레슨)에 대해 제출한 과제 코드와 평가 결과를 저장합니다.
각 제출은 한 학생이 한 강의에 대해 제출한 내용입니다.

컬럼 설명:
  id            INTEGER  : 고유 식별자 (PRIMARY KEY, AUTOINCREMENT)
  student_id    INTEGER  : 제출한 학생 ID (NOT NULL, FOREIGN KEY)
                            👉 students(id) 참조
  lesson_id     INTEGER  : 대상 강의 ID (NOT NULL, FOREIGN KEY)
                            👉 lessons(id) 참조
  code_text     TEXT     : 제출한 소스 코드 (NULL 허용 — 텍스트 과제도 가능)
  score         REAL     : 평가 점수 (DEFAULT 0, 실수형)
                            👉 REAL: SQLite의 부동소수점 타입
                               (0.0 ~ 100.0 범위 예상)
  submitted_at  TEXT     : 제출 일시 (DEFAULT = datetime('now'))
  feedback      TEXT     : 피드백/코멘트 (NULL 허용)

외래 키 관계:
  submissions.student_id → students.id
  submissions.lesson_id  → lessons.id
  → 즉, 존재하지 않는 학생이나 강의에 대해 제출할 수 없음
-----------------------------------------------------------------------
*/
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    code_text TEXT,
    score REAL DEFAULT 0,
    submitted_at TEXT DEFAULT (datetime('now')),
    feedback TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);
"""

# =========================================================================
# 👨‍🎓 학생 데이터 (STUDENTS)
# =========================================================================
# 각 튜플은 (이름, 이메일) 순서입니다.
# students 테이블의 INSERT 문: INSERT INTO students (name, email) VALUES (?, ?)
# id, created_at, course_count는 자동 생성되므로 VALUES에 포함하지 않음
STUDENTS = [
    ("김민수", "minsu.kim@edu.dev"),    # 학생 1: Python 기초, Flask, Streamlit 수강
    ("이서연", "seoyeon.lee@edu.dev"),  # 학생 2: Python 기초, Node.js 수강
    ("박지훈", "jihoon.park@edu.dev"),  # 학생 3: Python 기초, Flask, Streamlit 수강
    ("최유나", "yuna.choi@edu.dev"),    # 학생 4: Flask, Node.js 수강
    ("정태호", "taeho.jung@edu.dev"),   # 학생 5: Python 기초, Streamlit 수강
    ("한소희", "sohee.han@edu.dev"),    # 학생 6: Flask, Node.js 수강
    ("오민준", "minjun.oh@edu.dev"),    # 학생 7: 전과목 수강 (가장 활동적인 학생)
    ("윤서현", "seohyun.yoon@edu.dev"), # 학생 8: Node.js, Streamlit 수강
]

# =========================================================================
# 📚 과목 데이터 (COURSES)
# =========================================================================
# 각 튜플은 (제목, 강사, 설명, 난이도) 순서입니다.
# courses 테이블의 INSERT 문: INSERT INTO courses (title, instructor, description, level) VALUES (?, ?, ?, ?)
# id, student_count는 자동 생성
COURSES = [
    (
        "Python 기초",           # 과목 1: title
        "박지훈",                 # instructor
        "프로그래밍 입문자를 위한 파이썬 기초 과제입니다. 변수, 조건문, 반복문, 함수 등 기본 문법을 배웁니다.",
        "초급",                   # level (CHECK 제약으로 '초급'만 허용)
    ),
    (
        "Flask 웹개발",           # 과목 2: title
        "이서연",                 # instructor
        "Flask 프레임워크를 활용한 웹 애플리케이션 개발 과제입니다. REST API, 템플릿 렌더링, 데이터베이스 연동을 다룹니다.",
        "중급",                   # level
    ),
    (
        "Node.js",                # 과목 3: title
        "최유나",                 # instructor
        "Node.js를 이용한 서버 사이드 개발 과제입니다. Express, 비동기 처리, 모듈 시스템을 학습합니다.",
        "중급",                   # level
    ),
    (
        "Streamlit 데이터",       # 과목 4: title
        "정태호",                 # instructor
        "Streamlit을 활용한 데이터 시각화 과제입니다. 데이터프레임 처리, 차트 생성, 인터랙티브 대시보드 제작을 배웁니다.",
        "초급",                   # level
    ),
]

# =========================================================================
# 📖 강의(레슨) 데이터 (LESSONS)
# =========================================================================
# 각 튜플은 (course_id, title, content, order_num, duration_min) 순서입니다.
# lessons 테이블의 INSERT 문:
#   INSERT INTO lessons (course_id, title, content, order_num, duration_min) VALUES (?, ?, ?, ?, ?)
#
# course_id: 이 강의가 속한 과목의 ID (1=Python 기초, 2=Flask, 3=Node.js, 4=Streamlit)
# order_num: 과목 내에서의 학습 순서 (1부터 시작)
# duration_min: 예상 학습 시간(분)
LESSONS = [
    # ----- 과목 1: Python 기초 (course_id=1) -----
    # 총 4개 강의, 30~50분 소요
    (1, "파이썬 시작하기", "파이썬 설치 및 개발 환경 설정, 첫 번째 프로그램 실행하기", 1, 30),
    (1, "변수와 자료형", "숫자, 문자열, 리스트, 딕셔너리 등 기본 자료형 이해하기", 2, 45),
    (1, "조건문과 반복문", "if문, for문, while문을 활용한 프로그램 흐름 제어", 3, 50),
    (1, "함수 정의하기", "함수 선언, 매개변수, 반환값, 람다 함수 학습", 4, 45),

    # ----- 과목 2: Flask 웹개발 (course_id=2) -----
    # 총 3개 강의
    (2, "Flask 소개 및 설치", "Flask 프레임워크 소개, 가상환경 설정 및 기본 앱 구조", 1, 30),
    (2, "라우팅과 뷰 함수", "URL 라우팅, HTTP 메서드 처리, 뷰 함수 작성", 2, 45),
    (2, "템플릿과 폼 처리", "Jinja2 템플릿 엔진, 폼 데이터 처리, 파일 업로드", 3, 50),

    # ----- 과목 3: Node.js (course_id=3) -----
    # 총 3개 강의
    (3, "Node.js 기초", "Node.js 런타임 이해, 모듈 시스템, npm 패키지 관리", 1, 35),
    (3, "Express 서버 만들기", "Express 프레임워크, 미들웨어, 라우팅 구성", 2, 50),
    (3, "비동기 처리", "콜백, Promise, async/await 패턴 학습", 3, 45),

    # ----- 과목 4: Streamlit 데이터 (course_id=4) -----
    # 총 2개 강의
    (4, "Streamlit 시작하기", "Streamlit 설치 및 기본 앱 구성, 위젯 사용법", 1, 30),
    (4, "데이터 시각화", "Matplotlib, Plotly 연동, 차트 및 그래프 생성", 2, 50),
]

# =========================================================================
# 📝 수강 신청 데이터 (ENROLLMENTS)
# =========================================================================
# 각 튜플은 (student_id, course_id, grade) 순서입니다.
# enrollments 테이블의 INSERT 문:
#   INSERT INTO enrollments (student_id, course_id, grade) VALUES (?, ?, ?)
# enrolled_at은 DEFAULT(datetime('now'))로 자동 생성
#
# 데이터 분포 설명:
# - 학생 1(김민수): Python(1), Flask(2), Streamlit(4) — 3과목 수강
# - 학생 7(오민준): 전 과목(1,2,3,4) — 4과목 수강 (가장 많음)
# - 학생 8(윤서현): Node.js(3), Streamlit(4) — 2과목 수강
# - 성적 분포: A+, A, B+, B (A 학점 위주로 분포)
ENROLLMENTS = [
    # (student_id, course_id, grade)
    (1, 1, "A+"),   # 김민수 → Python 기초, 성적 A+
    (1, 2, "B+"),   # 김민수 → Flask 웹개발, 성적 B+
    (1, 4, "A"),    # 김민수 → Streamlit 데이터, 성적 A
    (2, 1, "A"),    # 이서연 → Python 기초
    (2, 3, "B"),    # 이서연 → Node.js
    (3, 1, "B+"),   # 박지훈 → Python 기초
    (3, 2, "A+"),   # 박지훈 → Flask 웹개발
    (3, 4, "A"),    # 박지훈 → Streamlit
    (4, 2, "A"),    # 최유나 → Flask 웹개발
    (4, 3, "B+"),   # 최유나 → Node.js
    (5, 1, "A+"),   # 정태호 → Python 기초
    (5, 4, "A+"),   # 정태호 → Streamlit
    (6, 2, "B"),    # 한소희 → Flask 웹개발
    (6, 3, "A"),    # 한소희 → Node.js
    (7, 1, "A"),    # 오민준 → Python 기초
    (7, 2, "A"),    # 오민준 → Flask 웹개발
    (7, 3, "B+"),   # 오민준 → Node.js
    (7, 4, "A"),    # 오민준 → Streamlit
    (8, 3, "A+"),   # 윤서현 → Node.js
    (8, 4, "B+"),   # 윤서현 → Streamlit
]

# =========================================================================
# 💻 과제 제출 데이터 (SUBMISSIONS)
# =========================================================================
# 각 튜플은 (student_id, lesson_id, code_text, score, feedback) 순서입니다.
# submissions 테이블의 INSERT 문:
#   INSERT INTO submissions (student_id, lesson_id, code_text, score, feedback) VALUES (?, ?, ?, ?, ?)
# submitted_at은 DEFAULT(datetime('now'))로 자동 생성
#
# 데이터 분포:
# - 학생들이 수강하는 과목의 강의(레슨)에 대해 제출한 과제 코드
# - score: 0~100점 (완벽한 코드는 100점)
# - feedback: 교사의 코멘트 (한글 피드백)
SUBMISSIONS = [
    # 학생 1 (김민수)의 제출
    (1, 1, "print('안녕하세요, 파이썬!')", 100, "잘 작성했습니다!"),
    (1, 2, "name = '김민수'\nage = 25\nprint(f'이름: {name}, 나이: {age}')", 95, "변수 사용이 정확합니다."),
    (1, 3, "for i in range(10):\n    if i % 2 == 0:\n        print(i)", 90, "조건문과 반복문 조합이 좋습니다."),

    # 학생 2 (이서연)의 제출
    (2, 1, "print('Flask 시작하기')", 85, "기본 구조를 잘 따랐습니다."),
    (2, 4, "const express = require('express');\nconst app = express();", 92, "기본 설정이 정확합니다."),

    # 학생 3 (박지훈)의 제출
    (3, 1, "print('Hello World')", 100, "완벽합니다!"),
    (3, 2, "x = 10\ny = 20\nprint(x + y)", 98, "정확한 계산입니다."),
    (3, 5, "from flask import Flask\napp = Flask(__name__)", 95, "Flask 앱 생성이 정확합니다."),

    # 학생 4 (최유나)의 제출
    (4, 8, "import streamlit as st\nst.title('내 첫 앱')", 90, "Streamlit 기본 사용법을 잘 따랐습니다."),

    # 학생 5 (정태호)의 제출
    (5, 1, "def greet(name):\n    return f'안녕, {name}!'\n\nprint(greet('태호'))", 100, "함수 정의가 훌륭합니다!"),
    (5, 12, "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndf = pd.DataFrame({'x': [1,2,3], 'y': [4,5,6]})\nplt.plot(df['x'], df['y'])", 88, "데이터 시각화 코드가 좋습니다."),

    # 학생 7 (오민준, 가장 활동적)의 제출
    (7, 1, "print('종합 과제')", 95, "잘했습니다!"),
    (7, 2, "a = 100\nb = 200\nprint(a * b)", 100, "연산이 정확합니다."),
    (7, 5, "@app.route('/')\ndef home():\n    return 'Hello Flask'", 92, "라우팅이 정확합니다."),
    (7, 9, "app.get('/', (req, res) => {\n    res.send('Hello');\n});", 90, "Express 라우팅이 좋습니다."),
    (7, 12, "st.bar_chart([1,2,3,4,5])", 85, "차트 생성이 정확합니다."),

    # 학생 8 (윤서현)의 제출
    (8, 9, "const fs = require('fs');\nfs.readFile('data.txt', 'utf8', (err, data) => {});", 88, "파일 처리가 좋습니다."),
    (8, 11, "import streamlit as st\nst.slider('값 선택', 0, 100)", 92, "위젯 사용이 정확합니다."),
]


# =========================================================================
# 🚀 seed_database() — 메인 시딩 함수
# =========================================================================
# 이 함수가 하는 일:
#   1. 기존 DB 파일 삭제 (완전 초기화)
#   2. 새 데이터베이스 파일 생성 및 연결
#   3. 외래 키 제약조건 활성화 (PRAGMA)
#   4. 스키마(SQL CREATE TABLE) 실행
#   5. 5개 테이블에 예제 데이터 INSERT
#   6. 서브쿼리로 집계 컬럼 UPDATE
#   7. 변경사항 COMMIT
#   8. 각 테이블 건수 출력하여 검증
#   9. 연결 종료
def seed_database():
    """
    데이터베이스를 처음부터 생성하고 시드 데이터를 채웁니다.

    동작 순서 (Step-by-step):
    1. 기존 DB 파일 삭제 → 매번 동일한 상태에서 시작
    2. SQLite 연결 및 커서 생성
    3. PRAGMA로 외래 키 제약조건 활성화
    4. CREATE TABLE 5개 실행 (students, courses, enrollments, lessons, submissions)
    5. INSERT: students(8명), courses(4개), lessons(12개), enrollments(20건), submissions(18건)
    6. UPDATE 서브쿼리: students.course_count와 courses.student_count 계산
    7. 변경사항 저장 (commit)
    8. 각 테이블의 행(row) 수를 출력하여 검증
    9. 연결 종료

    Returns:
        None (직접 DB 파일을 생성/수정함)
    """
    # ------------------------------------------------------------------
    # STEP 1: 기존 데이터베이스 파일 삭제
    # ------------------------------------------------------------------
    # os.path.exists(DB_PATH): DB 파일이 이미 존재하는지 확인
    # 존재한다면 os.remove()로 삭제 → '깨끗한 상태'에서 다시 시작
    # 이렇게 하는 이유: seed 스크립트는 '항상 동일한 초기 데이터'를
    # 보장해야 하므로, 기존 데이터가 있으면 모두 지우고 새로 만듭니다.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"기존 데이터베이스를 삭제했습니다: {DB_PATH}")

    # ------------------------------------------------------------------
    # STEP 2: SQLite 데이터베이스 연결
    # ------------------------------------------------------------------
    # sqlite3.connect(DB_PATH): 지정된 경로에 SQLite DB 파일 생성 및 연결
    # 파일이 없으면 자동으로 새 파일 생성
    conn = sqlite3.connect(DB_PATH)

    # cursor = conn.cursor(): SQL 문을 실행할 수 있는 '커서' 객체 생성
    # 커서는 "SQL 실행을 위한 핸들러"라고 생각하면 됩니다.
    # cursor.execute(): 단일 SQL 실행
    # cursor.executemany(): 같은 SQL을 여러 데이터로 반복 실행
    # cursor.executescript(): 여러 SQL 문을 한 번에 실행 (세미콜론으로 구분)
    cursor = conn.cursor()

    # ------------------------------------------------------------------
    # STEP 3: 외래 키(FOREIGN KEY) 제약조건 활성화
    # ------------------------------------------------------------------
    # PRAGMA: SQLite의 '설정' 명령어. 데이터베이스 동작 방식을 제어합니다.
    #
    # PRAGMA foreign_keys = ON 의 의미:
    #   SQLite는 기본적으로 FOREIGN KEY 제약조건을 '무시'합니다.
    #   (하위 호환성 및 성능 이유로 OFF가 기본값)
    #   이 PRAGMA를 ON으로 설정해야 FOREIGN KEY 제약이 실제로 적용됩니다.
    #
    # ON으로 설정하면:
    #   - 존재하지 않는 student_id로 enrollments에 INSERT 시도 → 오류 발생
    #   - 존재하지 않는 course_id로 lessons에 INSERT 시도 → 오류 발생
    #   - 데이터 무결성(Integrity)이 보장됨
    #
    # 참고: PRAGMA는 연결(connection) 단위 설정이므로,
    #       연결을 새로 만들 때마다 다시 설정해야 합니다.
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ------------------------------------------------------------------
    # STEP 4: 스키마(CREATE TABLE) 실행
    # ------------------------------------------------------------------
    # executescript(): 여러 SQL 문을 한 번에 실행 (세미콜론(;)으로 구분)
    # 위에서 정의한 SCHEMA_SQL 문자열 전체를 실행하여 5개 테이블 생성
    #
    # CREATE TABLE IF NOT EXISTS:
    #   테이블이 이미 존재하면 생성하지 않고 넘어감
    #   (이 스크립트는 기존 DB를 삭제하므로 항상 새로 생성됨)
    cursor.executescript(SCHEMA_SQL)
    print("스키마 생성 완료")

    # ------------------------------------------------------------------
    # STEP 5-1: 학생 데이터 INSERT
    # ------------------------------------------------------------------
    # executemany( sql, 데이터_리스트 ) 의 동작 방식:
    #   - 첫 번째 인자: 실행할 SQL 문 (물음표 ?는 '플레이스홀더'라고 함)
    #   - 두 번째 인자: (값1, 값2, ...) 튜플의 리스트
    #   - SQL을 여러 번 실행하지 않고, 내부적으로 최적화하여 한 번에 처리
    #   - ? 플레이스홀더: SQL 인젝션 방지 및 데이터 타입 자동 변환
    #
    # INSERT INTO students (name, email) VALUES (?, ?)
    #   → STUDENTS 리스트의 각 튜플(이름, 이메일)을 순서대로 name, email에 매핑
    #   → id: AUTOINCREMENT로 자동 생성
    #   → created_at: DEFAULT(datetime('now'))로 현재 시간 자동 입력
    #   → course_count: DEFAULT 0으로 자동 입력
    cursor.executemany(
        "INSERT INTO students (name, email) VALUES (?, ?);",
        STUDENTS,
    )
    print(f"학생 {len(STUDENTS)}명 삽입 완료")

    # ------------------------------------------------------------------
    # STEP 5-2: 과목 데이터 INSERT
    # ------------------------------------------------------------------
    # INSERT INTO courses (title, instructor, description, level) VALUES (?, ?, ?, ?)
    # COURSES의 각 튜플(제목, 강사, 설명, 난이도)을 4개 컬럼에 매핑
    # level 컬럼은 '초급', '중급', '고급'만 허용 (CHECK 제약)
    cursor.executemany(
        "INSERT INTO courses (title, instructor, description, level) VALUES (?, ?, ?, ?);",
        COURSES,
    )
    print(f"과목 {len(COURSES)}개 삽입 완료")

    # ------------------------------------------------------------------
    # STEP 5-3: 강의(레슨) 데이터 INSERT
    # ------------------------------------------------------------------
    # INSERT INTO lessons (course_id, title, content, order_num, duration_min) VALUES (?, ?, ?, ?, ?)
    # LESSONS의 각 튜플(과목ID, 제목, 내용, 순서, 소요시간)을 5개 컬럼에 매핑
    # course_id는 courses 테이블의 id를 참조하는 FOREIGN KEY
    cursor.executemany(
        "INSERT INTO lessons (course_id, title, content, order_num, duration_min) VALUES (?, ?, ?, ?, ?);",
        LESSONS,
    )
    print(f"강의 {len(LESSONS)}개 삽입 완료")

    # ------------------------------------------------------------------
    # STEP 5-4: 수강 신청 데이터 INSERT
    # ------------------------------------------------------------------
    # INSERT INTO enrollments (student_id, course_id, grade) VALUES (?, ?, ?)
    # ENROLLMENTS의 각 튜플(학생ID, 과목ID, 성적)을 3개 컬럼에 매핑
    # enrolled_at은 DEFAULT(datetime('now'))로 자동 생성
    # student_id와 course_id는 각각 FOREIGN KEY 제약이 적용됨
    cursor.executemany(
        "INSERT INTO enrollments (student_id, course_id, grade) VALUES (?, ?, ?);",
        ENROLLMENTS,
    )
    print(f"수강 신청 {len(ENROLLMENTS)}건 삽입 완료")

    # ------------------------------------------------------------------
    # STEP 5-5: 과제 제출 데이터 INSERT
    # ------------------------------------------------------------------
    # INSERT INTO submissions (student_id, lesson_id, code_text, score, feedback) VALUES (?, ?, ?, ?, ?)
    # SUBMISSIONS의 각 튜플(학생ID, 강의ID, 코드, 점수, 피드백)을 5개 컬럼에 매핑
    cursor.executemany(
        "INSERT INTO submissions (student_id, lesson_id, code_text, score, feedback) VALUES (?, ?, ?, ?, ?);",
        SUBMISSIONS,
    )
    print(f"제출 {len(SUBMISSIONS)}건 삽입 완료")

    # ------------------------------------------------------------------
    # STEP 6-1: students 테이블의 course_count UPDATE (서브쿼리 사용)
    # ------------------------------------------------------------------
    # 👇 아래 SQL을 이해해봅시다:
    #
    #   UPDATE students SET course_count = (
    #       SELECT COUNT(DISTINCT course_id)
    #       FROM enrollments
    #       WHERE enrollments.student_id = students.id
    #   );
    #
    # [해석]
    #   - UPDATE students: students 테이블의 모든 행을 갱신
    #   - SET course_count = (서브쿼리): course_count 컬럼을 서브쿼리 결과로 설정
    #
    # [서브쿼리(Subquery)란?]
    #   - SQL 문 안에 포함된 또 다른 SQL 문
    #   - 바깥 쿼리(메인 쿼리)의 각 행에 대해 안쪽 쿼리가 실행됨
    #   - 여기서는 각 학생(students.id)마다 수강한 과목 수를 계산
    #
    # [COUNT(DISTINCT course_id)]
    #   - COUNT: 행의 개수를 세는 집계 함수
    #   - DISTINCT: 중복을 제거 (한 학생이 같은 과목을 여러 번 신청해도 1번만 카운트)
    #   - 결과: 각 학생이 신청한 '서로 다른 과목'의 개수
    #
    # [실행 과정 예시 - 학생 1(김민수)]
    #   1. enrollments에서 student_id = 1인 행 조회
    #      → (1,1), (1,2), (1,4) → 3개 행
    #   2. DISTINCT course_id → 1, 2, 4 → 3개
    #   3. COUNT → 3
    #   4. students 테이블의 id=1 행의 course_count를 3으로 설정
    cursor.execute("""
        UPDATE students SET course_count = (
            SELECT COUNT(DISTINCT course_id) FROM enrollments WHERE enrollments.student_id = students.id
        );
    """)
    print("학생별 수강 과목 수 업데이트 완료")

    # ------------------------------------------------------------------
    # STEP 6-2: courses 테이블의 student_count UPDATE (서브쿼리 사용)
    # ------------------------------------------------------------------
    # 👇 아래 SQL을 이해해봅시다:
    #
    #   UPDATE courses SET student_count = (
    #       SELECT COUNT(DISTINCT student_id)
    #       FROM enrollments
    #       WHERE enrollments.course_id = courses.id
    #   );
    #
    # [해석]
    #   - 각 과목(courses.id)마다 수강 신청한 학생 수를 계산
    #   - COUNT(DISTINCT student_id): 한 학생이 같은 과목을 중복 신청해도 1명으로 카운트
    #
    # [실행 과정 예시 - 과목 1(Python 기초)]
    #   1. enrollments에서 course_id = 1인 행 조회
    #      → (1,1), (2,1), (3,1), (5,1), (7,1) → 5개 행
    #   2. DISTINCT student_id → 1, 2, 3, 5, 7 → 5명
    #   3. COUNT → 5
    #   4. courses 테이블의 id=1 행의 student_count를 5로 설정
    cursor.execute("""
        UPDATE courses SET student_count = (
            SELECT COUNT(DISTINCT student_id) FROM enrollments WHERE enrollments.course_id = courses.id
        );
    """)
    print("과목별 수강생 수 업데이트 완료")

    # ------------------------------------------------------------------
    # STEP 7: 변경사항 저장 (COMMIT)
    # ------------------------------------------------------------------
    # commit(): 지금까지의 모든 INSERT, UPDATE 변경사항을
    # 데이터베이스 파일에 '영구 저장'합니다.
    #
    # 💡 commit()을 호출하기 전에는 변경사항이 메모리에만 있음!
    #   - 연결이 끊어지면 (conn.close()) 모든 변경사항 손실
    #   - 트랜잭션(Transaction) 단위: commit()까지가 '하나의 작업 단위'
    #   - 에러 발생 시 rollback()으로 되돌릴 수 있음
    conn.commit()

    # ------------------------------------------------------------------
    # STEP 8: 데이터 검증 (Verify)
    # ------------------------------------------------------------------
    # 각 테이블의 전체 행(row) 수를 COUNT(*)로 조회하여 출력
    # 의도한 대로 데이터가 삽입되었는지 확인하는 과정
    # (SELECT COUNT(*) FROM table: 테이블의 전체 행 개수 반환)
    print("\n--- 데이터 확인 ---")
    for table in ["students", "courses", "lessons", "enrollments", "submissions"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]  # fetchone(): 결과의 첫 번째 행 반환 → 튜플의 첫 값
        print(f"  {table}: {count}건")

    # ------------------------------------------------------------------
    # STEP 9: 연결 종료
    # ------------------------------------------------------------------
    # 데이터베이스 연결을 닫아 리소스를 반환합니다.
    # close() 후에는 더 이상 SQL 문을 실행할 수 없습니다.
    conn.close()

    # 완료 메시지 출력
    print(f"\n데이터베이스가 성공적으로 생성되었습니다: {DB_PATH}")


# =========================================================================
# 🏁 프로그램 진입점 (Entry Point)
# =========================================================================
# if __name__ == "__main__": 의 의미:
#   Python 파일은 다른 파일에서 import 하여 사용할 수도 있고,
#   직접 실행(python seed.py)할 수도 있습니다.
#
#   __name__은 모듈의 이름을 저장하는 특별한 변수입니다.
#   - 직접 실행 시: __name__ == "__main__"
#   - import 시: __name__ == "seed" (파일명)
#
#   따라서 이 블록은 'python seed.py'로 직접 실행할 때만 동작합니다.
#   import seed 로 사용할 때는 seed_database()가 자동 실행되지 않음
#   → 모듈로서 유연하게 사용 가능 (함수만 제공, 실행은 선택)
if __name__ == "__main__":
    seed_database()
