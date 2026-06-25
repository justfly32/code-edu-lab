# 🎓 Code Edu Lab

> 코딩 교육용 대시보드 프로젝트 — 4개 스택으로 동일한 DB를 다루는 방법을 배웁니다.

## 📚 프로젝트 소개

이 프로젝트는 **로컬 데이터베이스에 접속하여 대시보드를 만드는 방법**을 교육하기 위해 설계되었습니다.
하나의 **공유 SQLite DB** (`shared/db/edu.db`)를 4가지 다른 스택에서 각각 접속하여 데이터를 가져옵니다.

```
학생/과목/강의/과제 데이터 → SQLite DB
         ├── Python Streamlit  → 대시보드 (포트 8501)
         ├── Python Flask     → 대시보드 (포트 5000)
         ├── Node.js Express  → REST API (포트 3001)
         └── Next.js          → 프론트엔드 (포트 3000) ← Express API 연동
```

## 🏗️ 아키텍처

```
code-edu-lab/
├── shared/db/              ← 공유 SQLite DB + 헬퍼
│   ├── seed.py             ← DB 시드 (초기 데이터 생성)
│   ├── db_helper.py        ← Python용 DB 헬퍼 함수
│   └── edu.db              ← 실제 DB 파일
│
├── python-streamlit/       ← Streamlit 대시보드
│   ├── app.py              ← 메인 앱 (5개 페이지)
│   └── requirements.txt
│
├── python-flask/           ← Flask 대시보드
│   ├── app.py              ← 메인 앱 (5개 라우트)
│   ├── templates/          ← Jinja2 템플릿
│   └── requirements.txt
│
├── node-express/           ← Express REST API
│   ├── server.js           ← API 서버
│   └── package.json
│
├── node-nextjs/            ← Next.js Standalone 프론트엔드
│   ├── app/                ← App Router (4개 페이지)
│   ├── components/         ← 재사용 컴포넌트
│   ├── lib/api.js          ← API 호출 함수
│   └── package.json
│
└── README.md
```

## 🗄️ DB 스키마

| 테이블 | 필드 | 설명 |
|--------|------|------|
| `students` | id, name, email, created_at, course_count | 학생 정보 |
| `courses` | id, title, instructor, description, level, student_count | 과목 정보 |
| `enrollments` | id, student_id, course_id, enrolled_at, grade | 수강 신청 |
| `lessons` | id, course_id, title, content, order_num, duration_min | 강의 내용 |
| `submissions` | id, student_id, lesson_id, code_text, score, submitted_at, feedback | 과제 제출 |

## 🚀 빠른 시작

### 1. DB 초기화 (시드 실행)

```bash
cd ~/projects/code-edu-lab/shared/db
python3 seed.py
```

### 2. Python Streamlit

```bash
cd ~/projects/code-edu-lab/python-streamlit
pip3 install -r requirements.txt
streamlit run app.py --server.port 8501
# → http://localhost:8501
```

### 3. Python Flask

```bash
cd ~/projects/code-edu-lab/python-flask
pip3 install -r requirements.txt
python3 app.py
# → http://localhost:5000
```

### 4. Node.js Express API

```bash
cd ~/projects/code-edu-lab/node-express
npm install
node server.js
# → http://localhost:3001/api/health
```

### 5. Next.js 프론트엔드

```bash
cd ~/projects/code-edu-lab/node-nextjs
npm install
npm run build && npm run start
# → http://localhost:3000
# Express API가 http://localhost:3001 에서 실행 중이어야 함
```

## 📖 각 스택 학습 포인트

### Python Streamlit
- `sys.path`로 공유 모듈 임포트
- `st.sidebar` 네비게이션
- `st.columns` KPI 카드 레이아웃
- Altair 차트 시각화
- 세션 상태 관리

### Python Flask
- `sys.path` + `import db_helper`
- Jinja2 템플릿 렌더링
- Chart.js CDN 연동 (서버 사이드 렌더링)
- 라우트 분리 (`/students`, `/courses` 등)
- 검색 필터링 (query parameter)

### Node.js Express
- `better-sqlite3` 동기식 DB 접속
- Express 미들웨어 (CORS, JSON 파싱)
- RESTful API 엔드포인트 설계
- 파라미터 바인딩 (SQL 인젝션 방지)
- 에러 핸들링 미들웨어

### Next.js Standalone
- App Router 구조
- 서버/클라이언트 컴포넌트 분리
- `fetch()`로 Express API 호출
- `output: 'standalone'` 빌드 설정
- Chart.js 클라이언트 렌더링

## 🎯 교육 목표

이 프로젝트를 통해 다음을 배울 수 있습니다:

1. **DB 연결 패턴** — 같은 DB를 다양한 언어/프레임워크에서 접속하는 방법
2. **대시보드 설계** — KPI 카드, 차트, 테이블 구성
3. **API 설계** — RESTful 엔드포인트와 프론트엔드 연동
4. **프레임워크 비교** — Streamlit vs Flask vs Express vs Next.js
5. **코드 구조화** — 헬퍼 모듈, 컴포넌트, 템플릿 분리

## 📝 커리큘럼 제안

### 1일차: Python + DB 기초
- `seed.py` 실행하며 스키마 이해
- `db_helper.py` 읽으며 SQL 쿼리 파악
- Streamlit 앱 실행하며 대시보드 체험

### 2일차: Flask 웹 서버
- Flask 앱 구조 이해
- 템플릿 + Chart.js 연동 원리
- 검색/필터링 로직 따라쓰기

### 3일차: Node.js API
- Express 라우팅 패턴
- `better-sqlite3` vs Python `sqlite3` 비교
- REST API 엔드포인트 설계 연습

### 4일차: Next.js 프론트엔드
- App Router vs Pages Router
- 서버/클라이언트 컴포넌트 경계
- API 연동 패턴 연습

### 5일차: 확장 과제
- 새 테이블 추가 (예: `assignments`, `attendance`)
- 새 차트 유형 추가 (예: radar, doughnut)
- 새 페이지 추가 (예: 과목 상세)
- Docker 컨테이너화

## 🔧 요구사항

- **Python**: 3.10+ (streamlit, flask, pandas, altair)
- **Node.js**: 18+ (next, react, express, better-sqlite3)
- **OS**: macOS / Linux

## 📸 스크린샷

| Streamlit | Flask |
|-----------|-------|
| 5개 사이드바 페이지 | Jinja2 템플릿 기반 |
| Altair 차트 | Chart.js 차트 |

| Express API | Next.js |
|-------------|---------|
| REST API 7개 엔드포인트 | Standalone 빌드 |
| better-sqlite3 | App Router |

## 📄 라이선스

MIT — 교육 목적으로 자유롭게 사용하세요.
