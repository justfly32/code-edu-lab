#!/usr/bin/env python3
"""
교육용 SQLite 데이터베이스 시드 스크립트
Shared database for code-edu-lab project.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edu.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    course_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    instructor TEXT NOT NULL,
    description TEXT,
    level TEXT CHECK(level IN ('초급', '중급', '고급')),
    student_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TEXT DEFAULT (datetime('now')),
    grade TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    order_num INTEGER NOT NULL,
    duration_min INTEGER DEFAULT 30,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

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

STUDENTS = [
    ("김민수", "minsu.kim@edu.dev"),
    ("이서연", "seoyeon.lee@edu.dev"),
    ("박지훈", "jihoon.park@edu.dev"),
    ("최유나", "yuna.choi@edu.dev"),
    ("정태호", "taeho.jung@edu.dev"),
    ("한소희", "sohee.han@edu.dev"),
    ("오민준", "minjun.oh@edu.dev"),
    ("윤서현", "seohyun.yoon@edu.dev"),
]

COURSES = [
    (
        "Python 기초",
        "박지훈",
        "프로그래밍 입문자를 위한 파이썬 기초 과제입니다. 변수, 조건문, 반복문, 함수 등 기본 문법을 배웁니다.",
        "초급",
    ),
    (
        "Flask 웹개발",
        "이서연",
        "Flask 프레임워크를 활용한 웹 애플리케이션 개발 과제입니다. REST API, 템플릿 렌더링, 데이터베이스 연동을 다룹니다.",
        "중급",
    ),
    (
        "Node.js",
        "최유나",
        "Node.js를 이용한 서버 사이드 개발 과제입니다. Express, 비동기 처리, 모듈 시스템을 학습합니다.",
        "중급",
    ),
    (
        "Streamlit 데이터",
        "정태호",
        "Streamlit을 활용한 데이터 시각화 과제입니다. 데이터프레임 처리, 차트 생성, 인터랙티브 대시보드 제작을 배웁니다.",
        "초급",
    ),
]

LESSONS = [
    # Python 기초 (course_id=1)
    (1, "파이썬 시작하기", "파이썬 설치 및 개발 환경 설정, 첫 번째 프로그램 실행하기", 1, 30),
    (1, "변수와 자료형", "숫자, 문자열, 리스트, 딕셔너리 등 기본 자료형 이해하기", 2, 45),
    (1, "조건문과 반복문", "if문, for문, while문을 활용한 프로그램 흐름 제어", 3, 50),
    (1, "함수 정의하기", "함수 선언, 매개변수, 반환값, 람다 함수 학습", 4, 45),
    # Flask 웹개발 (course_id=2)
    (2, "Flask 소개 및 설치", "Flask 프레임워크 소개, 가상환경 설정 및 기본 앱 구조", 1, 30),
    (2, "라우팅과 뷰 함수", "URL 라우팅, HTTP 메서드 처리, 뷰 함수 작성", 2, 45),
    (2, "템플릿과 폼 처리", "Jinja2 템플릿 엔진, 폼 데이터 처리, 파일 업로드", 3, 50),
    # Node.js (course_id=3)
    (3, "Node.js 기초", "Node.js 런타임 이해, 모듈 시스템, npm 패키지 관리", 1, 35),
    (3, "Express 서버 만들기", "Express 프레임워크, 미들웨어, 라우팅 구성", 2, 50),
    (3, "비동기 처리", "콜백, Promise, async/await 패턴 학습", 3, 45),
    # Streamlit 데이터 (course_id=4)
    (4, "Streamlit 시작하기", "Streamlit 설치 및 기본 앱 구성, 위젯 사용법", 1, 30),
    (4, "데이터 시각화", "Matplotlib, Plotly 연동, 차트 및 그래프 생성", 2, 50),
]

ENROLLMENTS = [
    (1, 1, "A+"),
    (1, 2, "B+"),
    (1, 4, "A"),
    (2, 1, "A"),
    (2, 3, "B"),
    (3, 1, "B+"),
    (3, 2, "A+"),
    (3, 4, "A"),
    (4, 2, "A"),
    (4, 3, "B+"),
    (5, 1, "A+"),
    (5, 4, "A+"),
    (6, 2, "B"),
    (6, 3, "A"),
    (7, 1, "A"),
    (7, 2, "A"),
    (7, 3, "B+"),
    (7, 4, "A"),
    (8, 3, "A+"),
    (8, 4, "B+"),
]

SUBMISSIONS = [
    (1, 1, "print('안녕하세요, 파이썬!')", 100, "잘 작성했습니다!"),
    (1, 2, "name = '김민수'\nage = 25\nprint(f'이름: {name}, 나이: {age}')", 95, "변수 사용이 정확합니다."),
    (1, 3, "for i in range(10):\n    if i % 2 == 0:\n        print(i)", 90, "조건문과 반복문 조합이 좋습니다."),
    (2, 1, "print('Flask 시작하기')", 85, "기본 구조를 잘 따랐습니다."),
    (2, 4, "const express = require('express');\nconst app = express();", 92, "기본 설정이 정확합니다."),
    (3, 1, "print('Hello World')", 100, "완벽합니다!"),
    (3, 2, "x = 10\ny = 20\nprint(x + y)", 98, "정확한 계산입니다."),
    (3, 5, "from flask import Flask\napp = Flask(__name__)", 95, "Flask 앱 생성이 정확합니다."),
    (4, 8, "import streamlit as st\nst.title('내 첫 앱')", 90, "Streamlit 기본 사용법을 잘 따랐습니다."),
    (5, 1, "def greet(name):\n    return f'안녕, {name}!'\n\nprint(greet('태호'))", 100, "함수 정의가 훌륭합니다!"),
    (5, 12, "import pandas as pd\nimport matplotlib.pyplot as plt\n\ndf = pd.DataFrame({'x': [1,2,3], 'y': [4,5,6]})\nplt.plot(df['x'], df['y'])", 88, "데이터 시각화 코드가 좋습니다."),
    (7, 1, "print('종합 과제')", 95, "잘했습니다!"),
    (7, 2, "a = 100\nb = 200\nprint(a * b)", 100, "연산이 정확합니다."),
    (7, 5, "@app.route('/')\ndef home():\n    return 'Hello Flask'", 92, "라우팅이 정확합니다."),
    (7, 9, "app.get('/', (req, res) => {\n    res.send('Hello');\n});", 90, "Express 라우팅이 좋습니다."),
    (7, 12, "st.bar_chart([1,2,3,4,5])", 85, "차트 생성이 정확합니다."),
    (8, 9, "const fs = require('fs');\nfs.readFile('data.txt', 'utf8', (err, data) => {});", 88, "파일 처리가 좋습니다."),
    (8, 11, "import streamlit as st\nst.slider('값 선택', 0, 100)", 92, "위젯 사용이 정확합니다."),
]


def seed_database():
    # Remove existing DB to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"기존 데이터베이스를 삭제했습니다: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create schema
    cursor.executescript(SCHEMA_SQL)
    print("스키마 생성 완료")

    # Insert students
    cursor.executemany(
        "INSERT INTO students (name, email) VALUES (?, ?);",
        STUDENTS,
    )
    print(f"학생 {len(STUDENTS)}명 삽입 완료")

    # Insert courses
    cursor.executemany(
        "INSERT INTO courses (title, instructor, description, level) VALUES (?, ?, ?, ?);",
        COURSES,
    )
    print(f"과목 {len(COURSES)}개 삽입 완료")

    # Insert lessons
    cursor.executemany(
        "INSERT INTO lessons (course_id, title, content, order_num, duration_min) VALUES (?, ?, ?, ?, ?);",
        LESSONS,
    )
    print(f"강의 {len(LESSONS)}개 삽입 완료")

    # Insert enrollments
    cursor.executemany(
        "INSERT INTO enrollments (student_id, course_id, grade) VALUES (?, ?, ?);",
        ENROLLMENTS,
    )
    print(f"수강 신청 {len(ENROLLMENTS)}건 삽입 완료")

    # Insert submissions
    cursor.executemany(
        "INSERT INTO submissions (student_id, lesson_id, code_text, score, feedback) VALUES (?, ?, ?, ?, ?);",
        SUBMISSIONS,
    )
    print(f"제출 {len(SUBMISSIONS)}건 삽입 완료")

    # Update student course_count
    cursor.execute("""
        UPDATE students SET course_count = (
            SELECT COUNT(DISTINCT course_id) FROM enrollments WHERE enrollments.student_id = students.id
        );
    """)

    # Update courses student_count
    cursor.execute("""
        UPDATE courses SET student_count = (
            SELECT COUNT(DISTINCT student_id) FROM enrollments WHERE enrollments.course_id = courses.id
        );
    """)

    conn.commit()

    # Verify
    print("\n--- 데이터 확인 ---")
    for table in ["students", "courses", "lessons", "enrollments", "submissions"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count}건")

    conn.close()
    print(f"\n데이터베이스가 성공적으로 생성되었습니다: {DB_PATH}")


if __name__ == "__main__":
    seed_database()
