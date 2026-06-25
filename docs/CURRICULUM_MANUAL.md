# � Code Edu Lab - 코� 교육 커리큘럼 메뉴얼

> **Code Edu Lab**은 코� 교육을 위한 4개 스택의 대시보드 프로젝트입니다.  
> 하나의 공유 SQLite 데이터베이스를 Python Streamlit, Python Flask, Node.js Express, Next.js에서 각각 접속하여 데이터를 다루는 방법을 배�니다.

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [데이터베이스 스키마](#2-데이터베이스-스키마)
3. [ Python 기초 과정](#3-python-기초-과정-course_id--1)
4. [Flask 웹개발 과정](#4-flask-웹개발-과정-course_id--2)
5. [Node.js 과정](#5-nodejs-과정-course_id--3)
6. [Streamlit 데이터 과정](#6-streamlit-데이터-과정-course_id--4)
7. [API 레퍼런스](#7-api-레퍼런스)
8. [4개 스택 비교: 공통점과 차이점](#8-4개-스택-비교-공통점과-차이점)
9. [과제 제출 가이드](#9-과제-제출-가이드)
10. [진도 관리 시스템](#10-진도-관리-시스템)
11. [부록: 코드 예제 � 트러블슈팅](#11-부록-코드-예제-및-트러블�팅)

---

## 1. 프로젝트 개요

### 아키�처

```
공유 SQLite DB (edu.db)
    ├── Python Streamlit  (포트 8501)  → 인터랙티브 대시보드
    ├── Python Flask      (포트 5000)    → � 대시보드
    ├── Node.js Express   (포트 3001)    → REST API 서버
    └── Next.js           (포트 3000)    → 프론트엔드 (Express API 연동)
```

### 실행 방법

```bash
# 1. DB 초기화
cd shared/db && python3 seed.py && python3 migrate_curriculum.py

# 2. Streamlit
cd python-streamlit && pip install -r requirements.txt
streamlit run app.py --server.port 8501

# 3. Flask
cd python-flask && pip install -r requirements.txt && python3 app.py

# 4. Express
cd node-express && npm install && node server.js

# 5. Next.js
cd node-nextjs && npm install && npm run build && npm run start
```

---

## 2. 데이터베이스 스키마

### �심 테이블 구조

| 테이블 | 용도 | 주요 필드 |
|--------|------|-----------|
| `students` | 학생 정보 | id, name, email, created_at |
| `courses` | 과목 정보 | id, title, instructor, description, level |
| `enrollments` | 수강 신청 | id, student_id, course_id, grade |
| `lessons` | 강의 내용 | id, course_id, title, content, order_num |
| `submissions` | 과제 제출 | id, student_id, lesson_id, code_text, score |
| `curriculum_modules` | 커리큘럼 모� | id, course_id, title, order_num, difficulty |
| `curriculum_steps` | 학습 단계 | id, module_id, instruction, code_example, expected_output |
| `student_progress` | 학습 진도 | id, student_id, step_id, status, completed_at |

### ERD (관계도)

```
courses (1) ──→ (N) curriculum_modules ──→ (N) curriculum_steps
  │
  ├──→ (N) enrollments ←── (N) students
  │
  ├──→ (N) lessons
  │
  └──→ (N) submissions ←── (N) students

student_progress ──→ students (student_id)
student_progress ──→ curriculum_steps (step_id)
```

---

## 3. Python 기초 과정 (course_id = 1)

> **대상 학생**: 김민수, 이서연  
> **난이도**: beginner → intermediate  
> **총 예상 시간**: 125분  
> **DB 조회**: `SELECT * FROM curriculum_modules WHERE course_id = 1;`

### 모듈 1: Python 설치하기 (30분)

파이썬 3.11 설치 및 개발 환경을 설정합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **1.1 Python 설치** | `python --version` | 공식 �사이트에서 다운로드. 'Add Python to PATH' 체크. macOS: `brew install python@3.11` | `Python 3.11.x` |
| **1.2 가상환경** | `python -m venv .venv && source .venv/bin/activate` | 프로젝트별 독립 환경 생성 | `(.venv)` 프롬프트 표시 |
| **1.3 첫 프로그램** | `print('안녕하세요, 파이�!')` | 인터프리터 실행 � 텍스트 출력 | `안�하세요, 파이�!` |

**� 핵심 개념:**
- 인터프리터 언어: 컴파일 없이 �시 실행
- 가상환경: 프로젝트별 패키지 격리
- PATH: 운영체제가 실행 파일을 찾는 경로

---

### 모듈 2: 변수와 자료형 (45분)

파이썬의 기본 자료형(숫자, 문자열, 리스트, 딕셔너리)을 이해합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **2.1 변수와 숫자** | `name = '김민수'\nage = 25\nprint(f'이름: {name}')` | 타입 선언 없이 변수 생성. f-string으로 출력 | `이름: 김민수` |
| **2.2 문자열** | `text.upper()\ntext.split(',')\ntext[0:5]` | �라이싱은 0부터 시작. `start:end` | `안녕하세요` |
| **2.3 리스트/딕�너리** | `fruits.append('포도')\nstudent['name']` | `[]` 리스트, `{}` �셔너리 | `['사과', '바나나', '포도']` |

**💡 �심 개념:**
- 동적 타이핑: 변수 타입을 자동으로 판단
- 시퀀스 자료형: 인�싱, 슬라이싱 지원
- 메서드: `append()`, `upper()`, `split()` 등

**실행 결과:**
```
이름: 김민수, 나이: 25, 키: 175.5
10년 후 나이: 35
AND�하세요, 파이�!
['안녕하세요', ' 파이�!']
```

---

### 모듈 3: 조건문과 반복문 (50분)

if/elif/else 조건문과 for, while 반복문을 사용합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **3.1 if/elif/else** | `if score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'` | 콜론(`:`)과 들여쓰기 필수 | `학점: B` |
| **3.2 for 반복문** | `for i in range(5):\n    print(f'{i}번째')` | `range(n)` = 0~n-1. `enumerate()` = 인덱스+값 | `0번째 반복` ~ `4번째 반복` |
| **3.3 while과 제어** | `while count < 5:\n    if count == 2: continue\n    if count == 4: break` | `continue` 건너�기, `break` �시 �료 | `카운트: 0, 1, 3` |

**� 핵심 개념:**
- 들여쓰기(Indentation) 기반 블록 구조 (Python 독특)
- `range(start, end, step)` 함수
- 반복 제어: `break`, `continue`, `pass`

---

## 4. Flask �개발 과정 (course_id = 2)

> **대상 학생**: 박지훈, 최유진  
> **난이도**: beginner → intermediate  
> **총 예상 시간**: 125분

### 모� 1: Flask 설치 (30분)

Flask 프레임워크 설치와 가상환경 설정, 기본 � 구조를 배�니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **4.1 Flask 설치** | `pip install flask` | 가상환경 활성화 � 설치 | `Successfully installed flask-3.x.x` |
| **4.2 기본 앱** | `app = Flask(__name__)\n@app.route('/')` | `@app.route()` 데코레이터로 URL 매핑 | `Running on http://127.0.0.1:5000` |
| **4.3 의존성 관리** | `pip freeze > requirements.txt` | 패키지 목록 저장/복원 | 의존성 정상 설치 |

**💡 �심 개념:**
- **WSGI**: Web Server Gateway Interface (Python � �준)
- **데코레이터**: 함수를 감싸서 기능 추가
- **라우트**: URL 경로 → 함수 연결
- `debug=True` 개발 모드: 자동 재시작, 에러 상세 �시

---

### 모� 2: 라우팅 (45분)

URL 라우팅과 HTTP 메서드(GET, POST)를 처리하는 뷰 함수를 작성합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **5.1 기본 라우팅** | `@app.route('/user/<username>')` | `<variable>` 동적 경로 | `사용자: 김민수` |
| **5.2 HTTP 메서드** | `@app.route('/login', methods=['GET', 'POST'])` | `request.form`으로 폼 데이터 | POST 시 리다이렉트 |
| **5.3 에러 처리** | `@app.errorhandler(404)` | 에러 코드별 사용자 정의 페이지 | 404 페이지 표시 |

**� 핵심 개념:**
- **REST**: HTTP 메서드 = CRUD (GET, POST, PUT, DELETE)
- **상태 코드**: 200(성공), 301(리다이렉트), 404(없음), 500(서버 에러)
- `url_for('home')`: URL 역방향 생성 (하드코� 방지)
- **리다이렉트**: 브라우저가 다른 URL로 재요청

---

### 모듈 3: 템플릿 렌더링 (50분)

Jinja2 템플릿 엔진을 활용하여 동적 웹 페이지를 생성합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **6.1 Jinja2 템플릿** | `render_template('hello.html', username=name)` | `{{변수}}` 출력, `{%제어문%}` 로직 | 동적 HTML |
| **6.2 제어문/상속** | `{% extends 'base.html' %}\n{% for user in users %}` | 부모 템플릿 상속, 블록 교체 | 사용자 목록 |
| **6.3 �/업로드** | `request.files['file']\nsecure_filename()` | 파일 업로드 + 안전한 파일명 처리 | `업로드 완료!` |

**� 핵심 개념:**
- **SSR**: Server-Side Rendering (서버에서 HTML 생성)
- **템플릿 상속**: `{% extends %}` + `{% block %}`로 레이아웃 재사용
- **보안**: `secure_filename()` 으로 경로 탈취 공격 방지

**실행 결과:**
```
<!-- hello.html -->
<h1>안녕하세요, 김민수!</h1>

<!-- base.html 상속 자식 -->
{% block content %}
  <ul>
  {% for user in users %}
    <li>{{ user.name }}</li>
  {% endfor %}
  </ul>
{% endblock %}
```

---

## 5. Node.js 과정 (course_id = 3)

> **대상 학생**: 정하늘, 김민수, 이서연  
> **난이도**: beginner → advanced  
> **총 예상 시간**: 125분

### 모� 1: Node.js 설치 (30분)

Node.js 런타임 설치와 npm 패키지 관리, 모� 시스템을 이해합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **7.1 Node.js 설치** | `node --version` → `v20.x.x` | LTS 버전 권장. nvm으로 버전 관리 | `v20.x.x` |
| **7.2 npm 패키지** | `npm init -y && npm install express` | `package.json` 생성 + 패키지 설치 | `node_modules/` �더 생성 |
| **7.3 HTTP 서버** | `const http = require('http');\nserver.listen(3000)` | CommonJS 모듈. `require()`로 가져오기 | `서버 실행 중` |

**💡 핵심 개념:**
- **이벤트 기반**: 요청이 오면 �백 함수 실행 ( Non-blocking I/O)
- **CommonJS**: `require()` + `module.exports`
- **npm**: Node Package Manager. Python의 `pip`와 유사
- `nvm`: Node Version Manager. 여러 버전 동시 설치/전환

---

### 모듈 2: Express 기본 (45분)

Express 프레임워크의 기본 구조, 미들웨어, 라우팅을 배웁니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **8.1 기본 �** | `app.get('/', (req, res) => {\n    res.send('ok');\n});` | `get(path, handler)` 라우트 등록 | 브라우저에 'ok' |
| **8.2 미들웨어** | `app.use((req, res, next) => {\n    console.log(req.url);\n    next();\n});` | `next()` 호출 시 다음 미들웨어로 | 콘�에 로그 |
| **8.3 라우터 분리** | `const router = express.Router();\nmodule.exports = router;` | `app.use('/api', router)`로 연결 | `/api/users` 동작 |

**� 핵심 개념:**
- **미들웨어**: 요청-응답 사이클에 접근하는 함수 체인
- `req` (Request): 클라이언트 요청 정보
- `res` (Response): 서버 응답 제어
- **라우터 모듈화**: 기능별로 파일 분리 → 유지보수 용이

---

### 모� 3: REST API 만들기 (50분)

RESTful API 설계와 CRUD 구현, JSON 데이터 처리를 학습합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **9.1 REST 설계** | `GET /api/todos\nPOST /api/todos\nPUT /api/todos/:id\nDELETE /api/todos/:id` | HTTP 메서드 = CRUD | JSON 응답 |
| **9.2 JSON/에러** | `res.status(404).json({ error: '없음' })` | `status()` 상태 코드 설정 | `{"error": "없음"}` |
| **9.3 CORS/DB** | `app.use(cors());\nconst db = new Database('app.db');` | CORS 허용. better-sqlite3 동기 DB | DB 반환 |

**� 핵심 개념:**
- **REST 6원칙**: 클라이언트-서버 분리, 무상태, 캐시 가능, 계층화, 통합 인터�이스, 코드 온 디맨드
- **HTTP 상태 코드**: `200`(OK), `201`(Created), `400`(Bad Request), `404`(Not Found), `500`(Server Error)
- **CORS**: Cross-Origin Resource Sharing — 다른 출처의 리소스 접근 허용
- `better-sqlite3`: 동기식. Python의 `sqlite3`와 동일한 패턴

---

## 6. Streamlit 데이터 과정 (course_id = 4)

> **대상 학생**: 박지�, 최유진, 정하늘  
> **난이도**: beginner → intermediate  
> **총 예상 시간**: 125분

### 모듈 1: Streamlit 설치 (30분)

Streamlit 설치와 기본 앱 구성, 다양한 위젯 사용법을 배웁니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **10.1 설치** | `pip install streamlit` | Python 3.8+ 필요 | `Successfully installed` |
| **10.2 기본 앱** | `st.title('앱')\nst.write('안�')` | `streamlit run app.py` | 웹 앱 �시 |
| **10.3 위�** | `st.text_input('이름')\nst.slider('나이', 0, 100, 25)` | 선언형 UI | 대화형 �포넌트 |

**� 핵심 개념:**
- **선언형**: "화면에 이� 보여줘" 방식 (명령형과 대비)
- **위젯**: 버튼, 슬라이더, 입력창 등 대화형 요소
- **자동 재로딩**: 파일 저장 시 자동으로 브라우저 �신
- `st.session_state`: 세션 간 상태 유지

---

### 모듈 2: 컴포넌트 (45분)

Streamlit의 다양한 컴포넌트(버튼, 슬라이더, 차트)를 활용합니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **11.1 데이터프레임** | `st.dataframe(df)` | 대화형 테이블 (정렬, 스크롤) | 테이블 �시 |
| **11.2 레이아웃** | `col1, col2 = st.columns(2)\nwith col1:\n    st.metric('지표', '100', '+10%')` | �럼 분할 | 2분할 레이아� |
| **11.3 파일 업로드** | `st.file_uploader('CSV', type=['csv'])\nst.download_button('다운로드', data)` | 업로드 → 처리 → 다운로드 | 파일 처리 |

**� 핵심 개념:**
- `st.columns(n)`: 화면을 n분할
- `st.sidebar`: 사이드바 영역
- `st.metric()`: 지표 + 변화율 표시
- `st.expander()`: 접기/�치기 �션

---

### 모� 3: 차트 그리기 (50분)

Matplotlib, Plotly를 연동하여 데이터를 시각화하고 대시보드를 만듭니다.

| 단계 | 명령어/코드 | 설명 | 예상 출력 |
|------|------------|------|-----------|
| **12.1 Matplotlib** | `fig, ax = plt.subplots()\nax.plot(x, y)\nst.pyplot(fig)` | 정적 차트 | 사인 파동 |
| **12.2 Plotly** | `st.plotly_chart(fig, use_container_width=True)` | 인터랙티브 (호버, 줌) | 산점도 |
| **12.3 내장 차트** | `st.line_chart(data)\nst.bar_chart(data)` | 데이터프레임 직접 전달 | 라인 + 바 |

**💡 �심 개념:**
- **정적(Matplotlib)**: PNG로 렌더링, 가�다
- **인터랙티브(Plotly)**: JS 기반, 호버/줌/드래그 가능
- **내장 차트**: 가장 �르지만 커스터마이징 제한적
- `use_container_width=True`: 반응형으로 전체 너비 사용

---

## 7. API 레퍼런스

### Express REST API

| 메서드 | 경로 | 설명 | 응답 예시 |
|--------|------|------|-----------|
| GET | `/api/health` | 서버 상태 | `{"status":"ok","database":"connected"}` |
| GET | `/api/students` | 전체 학생 | `[{"id":1,"name":"김민수"}]` |
| GET | `/api/courses` | 과목+통계 | `[{"id":1,"student_count":2}]` |
| GET | `/api/courses/:id` | 과목 상세 | `{...,"lessons":[...]}` |
| GET | `/api/lessons?course_id=1` | 레슨 목록 | `[{"id":1,"title":"오리엔테이션"}]` |
| GET | `/api/submissions` | 과제 제출물 | `[{"id":1,"code_text":"...","score":95}]` |
| GET | `/api/statistics` | 통계 | `{"total_students":8,"total_courses":4}` |
| POST | `/api/todos` | 생성 | `{"id":1,"title":"할일"}` |

### Next.js 페이지

| 경로 | 파일 | 기능 |
|------|------|------|
| `/` | `app/page.js` | 대시보드 |
| `/students` | `app/students/page.js` | 학생 관리 |
| `/courses` | `app/courses/page.js` | 과목 목록 |
| `/submissions` | `app/submissions/page.js` | 과제 제출 |

### Flask 페이지

| 경로 | 템플릿 | 기능 |
|------|--------|------|
| `/` | `templates/index.html` | 대시보드 |
| `/students` | `templates/students.html` | 학생 관리 |
| `/courses` | `templates/courses.html` | 과목 목록 |

### Streamlit 메뉴

| 메뉴 | 기능 | �포넌트 |
|------|------|-----------|
| 개요 | KPI 카드 + 차트 | `st.metric`, Altair |
| 학생 관리 | 테이블 + 검색 | `st.dataframe`, `st.text_input` |
| 과목 현황 | 과목 카드 | `st.columns`, `st.metric` |
| 강의 내용 | 아코디언 | `st.expander` |
| 과제 제출 | 목록 + 코드 | `st.code`, `st.download_button` |

---

## 8. 4개 스택 비교: 공통점과 차이점

> ⭐ **이 �션이 �심입니다!** � 4개의 다른 스택을 사용하는지, 각각의 특징은 무엇인지 비교합니다.

### 8.1 공통점 (모든 스택이 함께하는 것)

| 공통점 | 설명 |
|--------|------|
| **같은 DB** | `shared/db/edu.db` SQLite 파일을 모두 사용 |
| **같은 데이터** | students, courses, curriculum_steps 등 동일한 테이블 구조 |
| **같은 목적** | 코딩 교육 + 학습 현황 관리 + 대시보드 제공 |
| **같은 학습 내용** | 커리큘럼 36단계가 모든 스택에 동일하게 표시 |
| **같은 인증 개념** | 학생별 진도 추적, 과제 제출, 점수 평가 |

### 8.2 차이점 (왜 4개가 필요한가?)

| 비교 항목 | Streamlit | Flask | Express | Next.js |
|-----------|-----------|-------|---------|---------|
| **언어** | Python | Python | JavaScript | JavaScript |
| **패러다임** | 선언형 UI | 서버 �더링(SSR) | REST API | �스택 프론트엔드 |
| **역할** | 데이터 분석 대시보드 | 웹 서버 + 템플릿 | API 서버 (백엔드) | 프론트엔드 (클라이언트) |
| **출력** | 인터랙티브 차트 | �성된 HTML 페이지 | JSON 데이터 | 동적 웹 앱 |
| **데이터 �름** | 직접 DB 접속 | 직접 DB 접속 | 직접 DB 접속 | → Express API 호출 |
| **러� 커브** | ⭐ �움 | ⭐⭐ 보통 | ⭐⭐ 보통 | ⭐⭐⭐ 어려움 |
| **속도 개발** | 매우 빠름 | 빠름 | 보통 | 느림 (빌드 필요) |
| **프로덕션 배포** | ❌ 제한적 | ✅ Flask �으로 | ✅ Node.js 서버로 | ✅ 도커/Vercel |

### 8.3 각 스택 선택 가이드

```
어떤 것을 만들고 싶으신가요?

    �─────────────────────────────────────────────────────┐
    │ "데이터를 빠르게 분석하고 �어요"                      │
    │ → Streamlit 선택!                                    │
    │   • 프로토타이핑에 최적                               │
    │   • 5분 만에 대시보드 �성 가능                       │
    │   • 데이터 사이언스 팀에 적합                          │
    └─────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────┐
    │ "� 서비스를 만들고 싶어요"                           │
    │ → Flask 선택!                                        │
    │   • 서버에서 HTML을 �더링                            │
    │   • 템플릿으로 페이지 구성                             │
    │   • 파이썬 개발자에게 자연스러운 선택                    │
    └─────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────┐
    │ "모바일/프론트엔드 앱에 � API가 필요해요"              │
    │ → Express 선택!                                      │
    │   • JSON으로 데이터 제공                              │
    │   • React, Vue, 모바일 �에서 호출                    │
    │   • 백엔드 API 서버의 표�                             │
    └─────────────────────────────────────────────────────┘

    �─────────────────────────────────────────────────────┐
    │ "현대적인 웹 �을 만들고 �어요"                        │
    │ → Next.js 선택!                                      │
    │   • 서버 �더링 + 클라이언트 렌더링 �합               │
    │   • SEO 최적화, �른 로딩                            │
    │   • �스택 가장 �전한 프레임워크                       │
    └─────────────────────────────────────────────────────┘
```

### 8.4 기술 스택 비교�

| 항목 | Streamlit | Flask | Express | Next.js |
|------|-----------|-------|---------|---------|
| **설치 크기** | ~50MB | ~5MB | ~10MB (+packages) | ~100MB (+packages) |
| **의존성 수** | 많음 | 적음 | 적음 | �음 |
| **서버 필요** | ✅ (자체 내장) | ✅ (Werkzeug) | ✅ (Node.js) | ✅ (Node.js) |
| **배포 방법** | `streamlit run` | `flask run` / Gunicorn | `node server.js` | `npm run start` / Docker |
| **테스트** | 어려움 | pytest 사용 가능 | Jest, Supertest | Jest, Cypress |
| **DB 접근** | sqlite3 직접 | sqlite3 직접 | better-sqlite3 직접 | API 호출 |
| **동시 처리** | 단일 스레드 | 단일 (Gunicorn으로 확장) | 이벤트 루프 | Node.js 기반 |
| **실시간** | ❌ (�링) | ❌ | ✅ (Socket.IO 가능) | ✅ (SSR, ISR) |
| **SSG/SSR** | ❌ | SSR (템플릿) | ❌ | SSG + SSR |
| **SEO** | ❌ | ✅ | ❌ | ✅ |
| **모바일 �** | ❌ | ❌ | ✅ (API로 연동) | ✅ (PWA 가능) |

### 8.5 � 4개 모두 사용하는가? (교육적 목적)

```
                    �────────────────────────────�
                    │    DB (SQLite)             │
                    │    같은 데이터              │
                    └─────────────�──────────────┘
                                  │
                    ┌─────────────┼─────────────�
                    │             │             │
              ┌─────�─────┐ ┌─────┴─────� ┌────�─────┐
              │  Streamlit │ │   Flask   │ │  Express │
              │  (분석)    │ │  (웹서버)  │ │  (API)   │
              └───────────┘ └───────────┘ └────�─────┘
                                               │
                                        ┌──────┴──────┐
                                        │   Next.js   │
                                        │ (프론트엔드) │
                                        └─────────────┘
```

**학습 순서 (권장):**

1. **1일차: Streamlit** → 가장 �고 빠르게 결과를 �으로 확인
2. **2일차: Flask** → 웹의 기본 (서버-클라이언트), 템플릿, HTTP 이해
3. **3일차: Express** → JavaScript 백엔드, REST API, 비동기 처리
4. **4일차: Next.js** → 현대적 프론트엔드, SSR, �스택 완성

**각 스택을 배우면 �는 것:**

| 스택 | 배우는 것 |
|------|-----------|
| Streamlit | Python 데이터 시각화, 대시보드 설계, EDA |
| Flask | HTTP 프로토콜, MVC 패턴, 템플릿 엔진, REST |
| Express | Node.js 비동기, API 설계, 미들�어 체인 |
| Next.js | React 컴포넌트, SSR/SSG, 라우팅, 상태 관리 |

---

## 9. 과제 제출 가이드

### 워크플로우

```
1. 학생  2. 과목  3. 모듈  4. 단계 학습  5. 코드 제출  6. 평가  7. 다음 단계
```

### 채점 기�

| 항목 | 배점 | 평가 |
|------|------|------|
| 코드 정확성 | 40점 | 문법, 로직 구현 |
| 가독성 | 20점 | 주석, 변수명, 들여쓰기 |
| 결과 일치 | 30점 | 예상 출력 일치 |
| 창의성 | 10점 | 추가 기능 |

---

## 10. 진도 관리 시스템

### 진도 데이터

```json
{
  "student_id": 1,
  "step_id": 3,
  "status": "completed",
  "completed_at": "2025-01-15 10:30:00",
  "attempts": 2
}
```

### 진도율

```
진도율 = (완료 단계 / 전체 36단계) × 100
```

### 인증 기준

| 등급 | 조건 |
|------|------|
| Bronze | 1개 과목 50%+ |
| Silver | 2개 이상 50%+ |
| Gold | 전체 80%+ |
| Master | 전체 100% |

---

## 11. 부록

### A. 코드 예제 모음

#### Python - 파일 처리
```python
with open('data.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
```

#### Flask - REST API
```python
@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    new_todo = Todo.create(data)
    return jsonify(new_todo), 201
```

#### Express - 미들웨어
```javascript
app.use(express.json());
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`);
    next();
});
```

#### Next.js - Server Component
```jsx
async function Page() {
    const data = await fetch('http://localhost:3001/api/todos');
    const todos = await data.json();
    return <div>{todos.map(t => <p key={t.id}>{t.title}</p>)}</div>;
}
```

### B. 트러블슈팅

| 문제 | 원인 | 해결 |
|------|------|------|
| `EADDRINUSE` | 포트 중복 | `kill -9 $(lsof -t -i:PORT)` |
| `MODULE_NOT_FOUND` | 패키지 미설치 | `pip install` / `npm install` |
| `DB not found` | 시드 미실행 | `python3 shared/db/seed.py` |
| `CORS error` | CORS 미설정 | Flask-CORS, Express cors() |
| 한글 �짐 | 인코� 미설정 | `encoding='utf-8'` |

### C. 명령어 치트시트

```bash
# 로� 서버 상태 확인
curl http://localhost:3001/api/health  # Express
curl http://localhost:5000/             # Flask
curl http://localhost:8501/_stcore/health  # Streamlit
curl http://localhost:3000/             # Next.js

# DB 확인
sqlite3 shared/db/edu.db "SELECT COUNT(*) FROM curriculum_steps;"
sqlite3 shared/db/edu.db ".schema curriculum_steps"

# Cloudflare 터널
grep trycloudflare /tmp/cf-*.log | tail -4
```

---

*마지막 업데이트: 2026-06-25*  
*작성자: Code Edu Lab*  
*라이선스: MIT — 교육 목적 자유 사용*
