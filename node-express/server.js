/**
 * ============================================================
 * 코드 교육 실험실 (Code Education Lab) - Express REST API
 * ============================================================
 *
 * 📚 학습 목표:
 *   이 파일은 Node.js + Express + better-sqlite3를 사용하여
 *   RESTful API 서버를 구축하는 방법을 교육하기 위해 만들어졌습니다.
 *   모든 코드에 상세한 한글 주석이 포함되어 있습니다.
 *
 * 주요 학습 내용:
 *   1. Node.js 모듈 시스템 (require() 함수)
 *   2. Express 웹 프레임워크로 서버 만들기
 *   3. better-sqlite3로 데이터베이스에 동기적으로 접근하기
 *   4. 미들웨어 (CORS, JSON 파싱, 로깅)의 개념과 사용법
 *   5. RESTful API 엔드포인트 설계 원칙
 *   6. SQL 쿼리 (SELECT, JOIN, GROUP BY, ORDER BY, WHERE)
 *   7. HTTP 상태 코드와 응답 형식
 *   8. try-catch 에러 처리 패턴
 */

// ============================================================
// 1. 모듈 불러오기 (require) - Node.js 모듈 시스템
// ============================================================
// 📌 require() 함수는 Node.js에서 다른 파일이나 패키지를 불러올 때 사용합니다.
//    Node.js는 CommonJS 모듈 시스템을 사용하며, require()가 그 핵심입니다.
//    npm으로 설치한 패키지(express, cors, better-sqlite3)는
//    node_modules/ 폴더에서 자동으로 찾아집니다.
//    직접 만든 파일은 './경로' 형식으로 불러옵니다.
//
// 📌 구조 분해 할당: const { Router } = require('express')처럼
//    필요한 기능만 골라서 가져올 수도 있습니다.

const express = require('express');
  // Express 웹 프레임워크 — Node.js에서 가장 널리 쓰이는 HTTP 서버 라이브러리
  // 미들웨어 기반 아키텍처로, 요청(request)과 응답(response)을 처리합니다.
  // 반환값: express() 함수 자체를 담고 있는 객체

const cors = require('cors');
  // CORS 미들웨어 패키지
  // Cross-Origin Resource Sharing: 다른 출처(도메인/포트)의 요청을 허용
  // 출처(Origin) = 프로토콜 + 도메인 + 포트 (예: http://localhost:3000)

const Database = require('better-sqlite3');
  // better-sqlite3: SQLite3의 동기(synchronous) 방식 Node.js 드라이버
  // 📌 교육적 장점: async/await 없이 직관적으로 DB 코드를 작성할 수 있음
  //    일반 DB 드라이버(mysql2, pg)는 비동기라서 Promise/then/async 필요
  //    better-sqlite3는 결과가 바로 반환되므로 초보자에게 이해하기 쉬움

const path = require('path');
  // Node.js 내장 모듈 — 파일/디렉토리 경로를 조작하는 유틸리티
  // path.join(), path.resolve() 등으로 OS별 경로 구분자(\ vs /) 처리

const fs = require('fs');
  // Node.js 내장 모듈 — File System, 파일 읽기/쓰기/존재 확인 등
  // fs.existsSync(): 동기 방식으로 파일 존재 여부 확인 (Sync 접미사 = 동기)

// ============================================================
// 2. Express 앱 인스턴스 생성
// ============================================================
// 📌 express()는 Express 애플리케이션(앱) 인스턴스를 생성하는 팩토리 함수입니다.
//    팩토리 함수 = new 키워드 없이 객체를 생성해주는 함수
//    이 app 객체가 우리 서버의 모든 기능을 담당합니다:
//      - 라우트 등록: app.get(), app.post(), app.put(), app.delete()
//      - 미들웨어 등록: app.use()
//      - 서버 시작: app.listen(포트, 콜백)
//    Express는 내부적으로 HTTP 모듈을 래핑(wrapping)하여 사용합니다.
const app = express();
const PORT = 3001;
  // 서버가 실행될 포트 번호
  // 3000번은 React 개발 서버가 기본 사용하므로 3001번 사용

// ============================================================
// 3. 데이터베이스 경로 및 시드 확인 (Seed Check)
// ============================================================
// 📌 __dirname: 현재 이 파일(server.js)이 위치한 디렉토리의 절대 경로
//    path.resolve(): 여러 경로 조각을 합쳐 절대 경로로 변환
//    '../shared/db/edu.db': 상위 디렉토리의 shared/db/ 폴더에 있는 DB 파일
const DB_PATH = path.resolve(__dirname, '../shared/db/edu.db');

// 📌 fs.existsSync(): 파일이 존재하는지 동기적으로 확인
//    서버 시작 전에 DB 파일이 없으면 진행할 수 없으므로 조기 종료(early exit)
if (!fs.existsSync(DB_PATH)) {
  // process.exit(1): 프로세스를 종료하고 종료 코드 1(=실패) 반환
  // 종료 코드 0 = 정상, 1 이상 = 에러 (셸 스크립트에서 활용 가능)
  console.error(`❌ 데이터베이스 파일을 찾을 수 없습니다: ${DB_PATH}`);
  console.error('   먼저 seed.py를 실행하여 데이터베이스를 초기화하세요.');
  process.exit(1);
}

// 📌 better-sqlite3 데이터베이스 연결
//    new Database(경로, 옵션): SQLite DB 파일을 열거나 생성
//    { verbose: console.log }: 실행되는 모든 SQL 쿼리를 콘솔에 출력
//    ⭐ 교육용으로 매우 유용 — 학생들이 어떤 쿼리가 실행되는지 실시간 관찰 가능
const db = new Database(DB_PATH, {
  verbose: console.log
});

// 📌 PRAGMA: SQLite의 설정 명령어
//    WAL(Write-Ahead Logging) 모드: 동시 읽기/쓰기 성능 향상
//    기본 모드(rollback journal)보다 읽기 성능이 좋아 교육용 실습에 적합
db.pragma('journal_mode = WAL');

console.log(`✅ 데이터베이스 연결 완료: ${DB_PATH}`);

// ============================================================
// 4. 미들웨어 설정 (Middleware)
// ============================================================
// 📌 미들웨어(Middleware)란?
//    Express에서 요청(req)이 라우트 핸들러에 도달하기 전에
//    거쳐가는 함수들의 파이프라인입니다.
//    미들웨어는 요청 객체를 수정하거나, 응답을 보내거나,
//    다음 미들웨어(next())로 제어를 넘길 수 있습니다.
//    "양파 껍질" 패턴(Onion model) — 요청은 바깥→안쪽, 응답은 안쪽→바깥쪽으로 통과
//
// 📌 app.use(미들웨어)로 등록하며, 등록된 순서대로 실행됩니다.

// ----------------------------------------------------------
// 4-1. CORS 미들웨어
// ----------------------------------------------------------
// 📌 CORS = Cross-Origin Resource Sharing (교차 출처 리소스 공유)
//    브라우저의 Same-Origin Policy(SOP, 동일 출처 정책)를 우회하기 위한 표준
//
// 📌 SOP란?
//    "보안상의 이유로, 출처(Origin)가 다른 웹 페이지의 리소스 요청을 차단한다"
//    출처 = 프로토콜(http/https) + 도메인(localhost) + 포트(3000)
//    예: http://localhost:3000 (React) → http://localhost:3001 (Express)
//    → 포트가 다르므로 SOP 위반! CORS 설정이 없으면 브라우저가 차단
//
// 📌 cors() 미들웨어는 응답 헤더에 'Access-Control-Allow-Origin: *'를 추가
//    '*'(와일드카드) = 모든 출처 허용 (교육 환경에서는 문제 없음)
//    실제 서비스에서는 특정 출처만 허용하는 것을 권장
app.use(cors());

// ----------------------------------------------------------
// 4-2. JSON 본문 파싱 미들웨어
// ----------------------------------------------------------
// 📌 express.json()은 요청 본문(request body)을 JSON 형식에서
//    JavaScript 객체로 자동 변환해줍니다.
//    클라이언트가 POST/PUT으로 JSON 데이터를 보내면,
//    req.body에서 해당 데이터를 사용할 수 있게 됩니다.
//
// 📌 이전에는 body-parser라는 별도 패키지가 필요했지만,
//    Express 4.16.0+부터 express.json()이 내장되었습니다.
//    body-parser의 json()과 urlencoded() 기능을 포함합니다.
//
// 📌 동작 방식:
//    1. Content-Type: application/json 헤더 확인
//    2. 요청 본문(raw bytes)을 읽어서 버퍼에 저장
//    3. JSON.parse()로 JavaScript 객체로 변환
//    4. req.body에 할당 → 다음 핸들러에서 접근 가능
app.use(express.json());

// ----------------------------------------------------------
// 4-3. 요청 로깅 미들웨어 (사용자 정의 미들웨어)
// ----------------------------------------------------------
// 📌 직접 만든 미들웨어 함수의 구조:
//    function(req, res, next) { ... }
//    - req: 요청 객체 (클라이언트의 요청 정보)
//    - res: 응답 객체 (클라이언트에게 보낼 응답)
//    - next: 다음 미들웨어/라우트로 제어를 넘기는 함수
//      (❗ next()를 호출하지 않으면 요청이 계속 대기 상태)
//
// 📌 이 미들웨어는 모든 HTTP 요청을 콘솔에 기록
//    디버깅 및 학습 목적으로 어떤 요청이 들어오는지 확인
app.use((req, res, next) => {
  console.log(`📨 ${req.method} ${req.url} - ${new Date().toISOString()}`);
  // req.method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
  // req.url: 요청 경로 (/api/students 등)
  // new Date().toISOString(): ISO 8601 형식의 현재 시간

  next();  // ⭐ next() 호출 — 다음 미들웨어 or 라우트 핸들러로 진행
});

// ============================================================
// 5. API 라우트 정의 (Routes)
// ============================================================
// 📌 RESTful API 설계 원칙:
//    GET    /api/resource      → 리소스 목록 조회 (Read)
//    GET    /api/resource/:id  → 특정 리소스 조회 (Read)
//    POST   /api/resource      → 새 리소스 생성 (Create)
//    PUT    /api/resource/:id  → 리소스 수정 (Update)
//    DELETE /api/resource/:id  → 리소스 삭제 (Delete)
//    (CRUD: Create-Read-Update-Delete)
//
// 📌 URL은 명사형 복수형으로, 동사는 사용하지 않음
//    좋은 예: GET /api/students
//    나쁜 예: GET /api/getStudents (동사 사용)
//
// 📌 응답 형식: 일관된 JSON 구조
//    {
//      success: true/false,  // 요청 성공 여부
//      data: ...,            // 실제 데이터
//      count: ...,           // (목록의 경우) 개수
//      error: ...            // (실패 시) 에러 메시지
//    }

// ----------------------------------------------------------
// 5-1. GET /api/health — 서버 상태 확인 (Health Check)
// ----------------------------------------------------------
// 📌 app.get(경로, 핸들러): GET 요청에 대한 라우트 등록
//    1번째 인자: URL 경로 ('/api/health')
//    2번째 인자: 요청 처리 함수 (req, res) => { ... }
//
// 📌 Health Check 엔드포인트:
//    서버가 정상 실행 중인지 확인하는 가장 기본적인 API
//    로드 밸런서, 모니터링 시스템, CI/CD 파이프라인에서 사용
//    복잡한 로직 없이 단순히 "I'm alive" 신호를 보냄
app.get('/api/health', (req, res) => {
  // 📌 res.json(): JSON 형식의 응답을 클라이언트에 전송
  //    Express가 자동으로 Content-Type: application/json 헤더 설정
  //    객체를 JSON.stringify()로 변환하여 응답
  //
  // 📌 res.json() vs res.status().json():
  //    res.json() = HTTP 200 상태 코드가 기본 (OK)
  //    res.status(코드).json() = 원하는 상태 코드 지정
  //    아래는 200 OK가 기본이므로 res.json() 사용
  res.json({
    status: 'ok',
    message: '서버가 정상 실행 중입니다',
    port: PORT,
    database: 'connected',
    timestamp: new Date().toISOString()
  });
  // ⭐ 응답을 보내면 요청-응답 사이클이 종료됩니다.
  //    res.json() 호출 후에는 더 이상 응답을 보낼 수 없습니다.
});

// ----------------------------------------------------------
// 5-2. GET /api/students — 전체 학생 목록 조회
// ----------------------------------------------------------
// 📌 RESTful 원칙: GET + 복수형 명사 = 리소스 목록 조회
//    HTTP 상태 코드 200 = OK (요청 성공)
app.get('/api/students', (req, res) => {
  // 📌 try-catch 에러 처리 패턴:
  //    try { ... } 블록 안에서 에러가 발생하면
  //    catch(err) { ... } 블록이 실행되어 에러를 처리
  //    이 패턴으로 서버가 비정상 종료되는 것을 방지
  try {
    // ⭐ ===========================================================
    // ⭐ better-sqlite3의 세 가지 주요 메서드:
    // ⭐ ===========================================================
    // ⭐ 1. db.prepare(SQL).all(파라미터...) — 모든 결과 행을 배열로 반환
    // ⭐    SELECT 결과가 0개면 빈 배열 [] 반환
    // ⭐    용례: 목록 조회 (여러 행)
    // ⭐
    // ⭐ 2. db.prepare(SQL).get(파라미터...) — 첫 번째 결과 행만 객체로 반환
    // ⭐    결과가 없으면 undefined 반환
    // ⭐    용례: 상세 조회 (한 행)
    // ⭐
    // ⭐ 3. db.prepare(SQL).run(파라미터...) — 쿼리 실행만 (결과 행 없음)
    // ⭐    { changes: number, lastInsertRowid: number } 객체 반환
    // ⭐    용례: INSERT, UPDATE, DELETE (데이터 변경)
    // ⭐
    // ⭐ 📌 동기 방식의 장점:
    // ⭐    - 코드가 순차적으로 실행되어 이해하기 쉬움
    // ⭐    - async/await, Promise, then() 몰라도 사용 가능
    // ⭐    - 에러는 그냥 try-catch로 잡으면 됨
    // ⭐    - 교육 초보자에게 이상적인 접근 방식
    // ⭐
    // ⭐ 📌 SQL 파라미터 바인딩:
    // ⭐    ? 자리에 값을 전달하면 SQL 인젝션 공격을 방지
    // ⭐    내부적으로 값이 이스케이프(escape)되어 처리됨
    // ⭐    예: db.prepare('SELECT * FROM users WHERE id = ?').get(userId)

    // 📌 SQL 쿼리: SELECT * FROM students ORDER BY created_at DESC
    //    SELECT *      : 모든 컬럼(*)을 선택
    //    FROM students : students 테이블에서
    //    ORDER BY created_at DESC : created_at 컬럼 기준 내림차순 정렬
    //      (DESC = Descending, 최신 데이터가 먼저 옴)
    //      (ASC = Ascending, 오래된 데이터가 먼저 옴 — 생략 시 기본값)
    const students = db.prepare(
      'SELECT * FROM students ORDER BY created_at DESC'
    ).all();  // all() → 배열 반환

    // 📌 HTTP 상태 코드 200 (OK):
    //    요청이 성공적으로 처리되었음을 의미
    //    Express의 res.json()은 기본으로 200을 사용
    res.json({
      success: true,
      count: students.length,  // 배열 길이 = 학생 수
      data: students           // 실제 학생 데이터 배열
    });
  } catch (err) {
    // 📌 HTTP 상태 코드 500 (Internal Server Error):
    //    서버 내부에서 처리할 수 없는 오류가 발생했을 때 사용
    //    클라이언트는 이 응답을 받으면 재시도하거나 관리자에게 알림
    //
    // 📌 res.status(500).json():
    //    res.status()로 상태 코드 설정 후 .json()으로 응답 전송
    //    이렇게 체이닝(chaining)하여 상태 코드와 응답 본문을 함께 설정
    res.status(500).json({
      success: false,
      error: err.message  // err.message: JavaScript Error 객체의 설명 문자열
    });
  }
});

// ----------------------------------------------------------
// 5-3. GET /api/courses — 전체 강의 목록 (통계 포함)
// ----------------------------------------------------------
// 📌 이 엔드포인트는 단순 목록 조회를 넘어 JOIN과 GROUP BY를 사용한
//    집계(aggregation) 쿼리를 보여줍니다.
app.get('/api/courses', (req, res) => {
  try {
    // 📌 고급 SQL 쿼리 분석:
    //
    //    SELECT 절: 조회할 컬럼 지정
    //      c.id, c.title, ... — courses 테이블(c 별칭)의 기본 컬럼
    //      COUNT(DISTINCT e.id) — enrollments에서 고유한 id 개수 (수강생 수)
    //      COUNT(DISTINCT l.id) — lessons에서 고유한 id 개수 (레슨 수)
    //
    //    FROM courses c : courses 테이블에 c라는 별칭(alias) 부여
    //
    //    LEFT JOIN enrollments e ON c.id = e.course_id
    //      LEFT JOIN: 왼쪽 테이블(courses)의 모든 행을 유지하면서
    //                 오른쪽 테이블(enrollments)과 매칭
    //      ⭐ INNER JOIN과의 차이점:
    //        INNER JOIN: 양쪽 테이블에 모두 데이터가 있는 경우만 반환
    //        LEFT JOIN: 왼쪽 테이블은 모두 반환, 오른쪽이 없으면 NULL
    //        → 수강생이 없는 강의도 목록에 포함시키려면 LEFT JOIN 필요
    //
    //    GROUP BY c.id : c.id가 같은 행끼리 그룹화하여 COUNT 집계
    //      GROUP BY 없이 COUNT를 사용하면 전체가 하나의 그룹으로 집계됨
    //      GROUP BY가 있으면 각 그룹별로 COUNT 계산
    //
    //    ORDER BY c.id : 강의 ID 순으로 정렬
    const courses = db.prepare(`
      SELECT
        c.id,
        c.title,
        c.instructor,
        c.description,
        c.level,
        c.student_count,
        COUNT(DISTINCT e.id) as enrollment_count,
        COUNT(DISTINCT l.id) as lesson_count
      FROM courses c
      LEFT JOIN enrollments e ON c.id = e.course_id
      LEFT JOIN lessons l ON c.id = l.course_id
      GROUP BY c.id
      ORDER BY c.id
    `).all();

    res.json({
      success: true,
      count: courses.length,
      data: courses
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ----------------------------------------------------------
// 5-4. GET /api/courses/:id — 강의 상세 정보
// ----------------------------------------------------------
// 📌 :id는 URL 파라미터(동적 세그먼트)
//    실제 URL: /api/courses/1, /api/courses/42 등
//    req.params.id로 접근 가능 (Express가 자동 파싱)
//    🎯 RESTful 원칙: 특정 리소스 조회는 경로에 식별자(:id) 포함
app.get('/api/courses/:id', (req, res) => {
  try {
    // 📌 req.params: URL 경로의 동적 파라미터를 담은 객체
    //    예: /api/courses/3 → req.params = { id: '3' }
    //    URL 파라미터는 항상 문자열(string)이므로 숫자로 변환 필요
    const courseId = parseInt(req.params.id);

    // 📌 isNaN(): 전달된 값이 NaN(Not-a-Number)인지 확인
    //    숫자가 아닌 값(ID에 문자 포함)이 들어오면 400 Bad Request
    if (isNaN(courseId)) {
      // HTTP 400 (Bad Request): 클라이언트의 요청이 잘못됨
      // 클라이언트 측 오류 — 요청 형식이나 파라미터가 유효하지 않음
      return res.status(400).json({
        success: false,
        error: '유효한 강의 ID를 입력하세요'
      });
      // ⭐ return을 사용하는 이유:
      //   res.json() 호출 후에도 함수 실행이 계속되는 것을 방지
      //   return으로 함수를 즉시 종료
    }

    // ---- 1) 강의 기본 정보 조회 ----
    // 📌 .get(): 단일 행을 객체로 반환
    //    ?에 courseId가 바인딩됨 (SQL 인젝션 방지)
    //    결과가 없으면 undefined 반환
    const course = db.prepare(
      'SELECT * FROM courses WHERE id = ?'
      // WHERE id = ? : 조건절 — id가 ? 값과 일치하는 행만 필터링
    ).get(courseId);

    // 📌 !course: course가 undefined이면 (결과 없음) true
    //    즉, 해당 ID의 강의가 DB에 없는 경우
    if (!course) {
      // HTTP 404 (Not Found): 요청한 리소스를 찾을 수 없음
      // 클라이언트가 존재하지 않는 ID로 조회한 경우
      return res.status(404).json({
        success: false,
        error: '강의를 찾을 수 없습니다'
      });
    }

    // ---- 2) 해당 강의의 레슨 목록 조회 ----
    // 📌 WHERE course_id = ? : 특정 강의에 속한 레슨만 필터링
    //    ORDER BY order_num ASC : 순서 번호 오름차순 정렬 (1, 2, 3...)
    const lessons = db.prepare(
      'SELECT * FROM lessons WHERE course_id = ? ORDER BY order_num ASC'
    ).all(courseId);

    // ---- 3) 해당 강의의 수강생 목록 조회 (JOIN) ----
    // 📌 다중 테이블 JOIN:
    //    enrollments e JOIN students s ON e.student_id = s.id
    //    enrollments 테이블(e)과 students 테이블(s)을
    //    e.student_id = s.id 조건으로 연결
    //    결과: 수강 정보와 학생 정보를 한 번에 조회
    const enrollments = db.prepare(`
      SELECT
        e.id as enrollment_id,
        e.enrolled_at,
        e.grade,
        s.id as student_id,
        s.name as student_name,
        s.email as student_email
      FROM enrollments e
      JOIN students s ON e.student_id = s.id
      WHERE e.course_id = ?
      ORDER BY e.enrolled_at DESC
    `).all(courseId);

    // 📌 하나의 응답에 여러 관련 데이터를 묶어서 반환
    //    이렇게 하면 클라이언트가 여러 번 요청할 필요가 없음 (N+1 문제 방지)
    res.json({
      success: true,
      data: {
        course,      // 강의 기본 정보 (객체)
        lessons,     // 레슨 목록 (배열)
        enrollments  // 수강생 목록 (배열)
      }
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ----------------------------------------------------------
// 5-5. GET /api/lessons — 전체 레슨 목록 (필터링 가능)
// ----------------------------------------------------------
// 📌 쿼리 파라미터(Query String): URL에서 ? 뒤에 오는 key=value 쌍
//    예: /api/lessons?course_id=1
//    req.query.course_id로 접근 (Express가 자동 파싱)
//    🎯 RESTful 원칙: 필터링/정렬/페이지네이션은 쿼리 파라미터로 처리
app.get('/api/lessons', (req, res) => {
  try {
    // 📌 구조 분해 할당: req.query에서 course_id 속성 추출
    //    req.query = { course_id: '1' } → const { course_id } = req.query
    const { course_id } = req.query;

    let sql = 'SELECT * FROM lessons';
    let params = [];

    // 📌 동적 쿼리 생성 패턴:
    //    조건에 따라 WHERE 절을 동적으로 추가
    //    course_id 쿼리 파라미터가 있으면 특정 강의의 레슨만 조회
    //    없으면 모든 레슨을 조회
    if (course_id) {
      sql += ' WHERE course_id = ?';
      // parseInt(): 문자열을 정수로 변환
      // 쿼리 파라미터는 항상 문자열로 전달되므로 숫자 변환
      params.push(parseInt(course_id));
    }

    sql += ' ORDER BY course_id, order_num ASC';
    // course_id 먼저, 같은 course_id 내에서는 order_num 순으로 정렬

    // 📌 스프레드 연산자 (...params):
    //    params 배열의 요소를 개별 인자로 펼쳐서 전달
    //    params = [1] → .all(1) 과 동일
    const lessons = db.prepare(sql).all(...params);

    res.json({
      success: true,
      count: lessons.length,
      filter: course_id ? { course_id: parseInt(course_id) } : null,
      data: lessons
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ----------------------------------------------------------
// 5-6. GET /api/submissions — 제출물 목록 (연관 정보 포함)
// ----------------------------------------------------------
// 📌 이 엔드포인트는 4개의 테이블을 JOIN하여
//    제출물과 관련된 모든 정보를 한 번에 조회합니다.
//    ⭐ 다중 JOIN의 실제 예시를 교육용으로 보여줍니다.
app.get('/api/submissions', (req, res) => {
  try {
    // 📌 다중 JOIN (4개 테이블):
    //
    //    submissions s             : 제출물 (기준 테이블)
    //    JOIN students st          : 학생 정보 연결
    //    JOIN lessons l            : 레슨 정보 연결
    //    JOIN courses c            : 강의 정보 연결 (레슨→강의)
    //
    //    연결 순서:
    //    submissions.student_id → students.id
    //    submissions.lesson_id  → lessons.id
    //    lessons.course_id      → courses.id
    //
    //    결과 한 행에: 제출물 + 학생이름 + 레슨제목 + 강의제목
    const submissions = db.prepare(`
      SELECT
        s.id,
        s.code_text,
        s.score,
        s.submitted_at,
        s.feedback,
        st.id as student_id,
        st.name as student_name,
        st.email as student_email,
        l.id as lesson_id,
        l.title as lesson_title,
        l.order_num,
        c.id as course_id,
        c.title as course_title
      FROM submissions s
      JOIN students st ON s.student_id = st.id
      JOIN lessons l ON s.lesson_id = l.id
      JOIN courses c ON l.course_id = c.id
      ORDER BY s.submitted_at DESC
      -- ORDER BY + DESC: 최근 제출물이 먼저 나오도록 정렬
    `).all();

    res.json({
      success: true,
      count: submissions.length,
      data: submissions
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ----------------------------------------------------------
// 5-7. GET /api/statistics — 대시보드 통계
// ----------------------------------------------------------
// 📌 여러 집계 쿼리를 조합하여 대시보드에 표시할 통계 데이터 생성
//    하나의 엔드포인트에서 여러 쿼리 결과를 모아서 반환
app.get('/api/statistics', (req, res) => {
  try {
    // 📌 COUNT(*) : 테이블의 전체 행 수를 집계하는 SQL 집계 함수
    //    결과: { count: 숫자 } 형태의 객체
    //    📌 AS count: 컬럼명에 별칭(alias) 부여
    //      결과 객체에서 count 키로 접근 가능
    const studentCount = db.prepare(
      'SELECT COUNT(*) as count FROM students'
    ).get();  // .get() → 단일 객체 반환 (예: { count: 42 })

    const courseCount = db.prepare(
      'SELECT COUNT(*) as count FROM courses'
    ).get();

    const lessonCount = db.prepare(
      'SELECT COUNT(*) as count FROM lessons'
    ).get();

    const enrollmentCount = db.prepare(
      'SELECT COUNT(*) as count FROM enrollments'
    ).get();

    const submissionCount = db.prepare(
      'SELECT COUNT(*) as count FROM submissions'
    ).get();

    // 📌 AVG(score) : score 컬럼의 평균값을 계산하는 집계 함수
    //    SQLite에서 AVG()는 실수(float) 반환
    const avgScore = db.prepare(
      'SELECT AVG(score) as average FROM submissions'
    ).get();

    // 📌 강의별 수강생 수 (차트 데이터용)
    //    LEFT JOIN + GROUP BY + COUNT + ORDER BY의 조합
    //    차트(막대 그래프 등)에 표시할 데이터로 적합
    const coursePopularity = db.prepare(`
      SELECT
        c.title,
        c.instructor,
        COUNT(e.id) as student_count
      FROM courses c
      LEFT JOIN enrollments e ON c.id = e.course_id
      GROUP BY c.id
      ORDER BY student_count DESC  -- 수강생 많은 순으로 정렬
    `).all();

    // 📌 레벨별 강의 수 (GROUP BY 단일 컬럼)
    //    level 별로 몇 개의 강의가 있는지 집계
    const levelDistribution = db.prepare(`
      SELECT level, COUNT(*) as count
      FROM courses
      GROUP BY level  -- level 컬럼 값이 같은 행끼리 그룹화
    `).all();

    // 📌 통합 통계 응답
    //    여러 쿼리 결과를 하나의 JSON 객체로 조합
    res.json({
      success: true,
      data: {
        overview: {
          totalStudents: studentCount.count,
          totalCourses: courseCount.count,
          totalLessons: lessonCount.count,
          totalEnrollments: enrollmentCount.count,
          totalSubmissions: submissionCount.count,
          averageScore: avgScore.average
            ? Math.round(avgScore.average * 100) / 100
            : 0  // 평균이 null(제출물 없음)이면 0 반환
        },
        coursePopularity,
        levelDistribution
      }
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ============================================================
// 6. 커리큘럼 API — 학습 가이드 및 진도 관리
// ============================================================
// 📌 커리큘럼(Curriculum) 시스템은 교육 콘텐츠를 모듈 단위로
//    구성하고, 각 모듈 안에 세부 단계(Step)를 포함하는 계층 구조입니다.
//
//    Courses (강의)
//      └── Curriculum Modules (커리큘럼 모듈) — curriculum_modules 테이블
//            └── Curriculum Steps (학습 단계) — curriculum_steps 테이블
//                  └── Student Progress (학생 진도) — student_progress 테이블
//
//    이 구조는 "학습 경로(Learning Path)"를 설계할 때 자주 사용되는 패턴입니다.

// ============================================================
// 6-1. GET /api/curriculum — 전체 커리큘럼 조회 (코스별 그룹화)
// ============================================================
// 📌 RESTful 설계: /api/curriculum (단수형 — 하나의 시스템/맥락)
//    전체 커리큘럼을 코스(course)별로 그룹화하여 반환
//
// 📌 이 엔드포인트는 두 단계로 데이터를 조회합니다:
//    1단계: 모든 모듈을 JOIN으로 조회
//    2단계: 각 모듈별로 스텝을 개별 조회 (루프)
app.get('/api/curriculum', (req, res) => {
  try {
    // ── 1단계: 모든 커리큘럼 모듈 조회 ──
    // 📌 SQL 분석:
    //    SELECT cm.*  : curriculum_modules의 모든 컬럼
    //    JOIN courses c ON cm.course_id = c.id
    //      → 모듈이 속한 강의의 제목을 가져오기 위해 JOIN
    //    ORDER BY cm.course_id, cm.order_num
    //      → 가장 바깥쪽 정렬: 강의별로, 각 강의 내에서는 순서대로
    const modules = db.prepare(`
      SELECT cm.id, cm.course_id, cm.title, cm.description, cm.order_num,
             cm.estimated_minutes, cm.difficulty, c.title as course_title
      FROM curriculum_modules cm
      JOIN courses c ON cm.course_id = c.id
      ORDER BY cm.course_id, cm.order_num
    `).all();

    // ── 2단계: 모듈을 코스별로 그룹화 ──
    // 📌 객체를 key-value 저장소로 사용하여 그룹화
    //    courses = { '1': { id: 1, title: '...', modules: [...] }, ... }
    const courses = {};

    // 📌 for...of 루프: 배열의 각 요소를 순회
    //    각 모듈을 해당 코스의 modules 배열에 추가
    for (const m of modules) {
      // 처음 보는 course_id면 새 항목 생성
      if (!courses[m.course_id]) {
        courses[m.course_id] = {
          id: m.course_id,
          title: m.course_title,
          modules: []  // 이 코스의 모듈들을 담을 빈 배열
        };
      }

      // ── 2b: 각 모듈의 세부 단계(Step) 조회 ──
      // 📌 루프 안에서 추가 쿼리 실행 (N+1 쿼리 패턴):
      //    모듈 개수만큼 추가 SELECT 실행
      //    단점: 모듈이 많으면 쿼리 수가 늘어남
      //    장점: 코드가 단순하고 이해하기 쉬움 (교육용 예제에 적합)
      //
      // 📌 WHERE module_id = ? : 특정 모듈의 스텝만 필터링
      //    ORDER BY order_num : 순서대로 정렬
      const steps = db.prepare(
        'SELECT id, title, order_num FROM curriculum_steps WHERE module_id = ? ORDER BY order_num'
      ).all(m.id);  // 현재 모듈의 ID를 파라미터로 전달

      // 모듈 객체에 step_count(개수)와 steps(배열)를 추가
      // 📌 스프레드 연산자: { ...m } — m 객체의 모든 속성을 복사
      //    m 객체에 step_count, steps 속성을 추가한 새 객체 생성
      courses[m.course_id].modules.push({
        ...m,              // 모듈의 모든 원래 속성 복사
        step_count: steps.length,  // 포함된 스텝 개수
        steps              // 스텝 배열
      });
    }

    // 📌 Object.values(): 객체의 값들만 배열로 반환
    //    courses = { '1': {...}, '2': {...} } →
    //    [{id:1,...}, {id:2,...}]
    res.json({ success: true, courses: Object.values(courses) });
  } catch (err) {
    // HTTP 500: 서버 내부 오류
    res.status(500).json({ success: false, error: err.message });
  }
});

// ============================================================
// 6-2. GET /api/curriculum/:courseId — 특정 강의의 커리큘럼
// ============================================================
// 📌 RESTful 설계: /api/curriculum/:courseId
//    특정 강의에 속한 모든 커리큘럼 모듈과 그 스텝을 조회
//    :courseId — URL 파라미터로 강의 ID 지정
app.get('/api/curriculum/:courseId', (req, res) => {
  try {
    // 📌 WHERE cm.course_id = ?로 특정 강의만 필터링
    //    req.params.courseId: URL에서 추출한 강의 ID
    const modules = db.prepare(`
      SELECT cm.*, c.title as course_title
      FROM curriculum_modules cm
      JOIN courses c ON cm.course_id = c.id
      WHERE cm.course_id = ?
      ORDER BY cm.order_num
    `).all(req.params.courseId);

    // 📌 각 모듈에 대해 스텝(단계) 목록을 추가로 조회
    //    for...of: 배열의 각 요소를 순회하는 반복문
    for (const m of modules) {
      // m.steps에 직접 속성을 동적으로 추가
      // m 객체에 steps 배열을 새로 할당
      m.steps = db.prepare(
        'SELECT * FROM curriculum_steps WHERE module_id = ? ORDER BY order_num'
      ).all(m.id);
      // 📌 .all() — 여러 행을 배열로 반환
      //    module_id가 m.id와 일치하는 모든 스텝 조회
    }

    res.json({ success: true, modules });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ============================================================
// 6-3. GET /api/curriculum/:courseId/step/:stepId — 특정 스텝 상세
// ============================================================
// 📌 RESTful 설계: 계층적 경로로 리소스 관계 표현
//    curriculum → course → step
//    /api/curriculum/:courseId/step/:stepId
//    URL에서 courseId와 stepId 두 개의 파라미터를 추출
//
// 📌 이 엔드포인트의 특별한 점:
//    - 이전(prev) / 다음(next) 스텝 정보도 함께 반환
//    - 학습자가 순서대로 이동할 수 있도록 네비게이션 지원
app.get('/api/curriculum/:courseId/step/:stepId', (req, res) => {
  try {
    // ── 1) 특정 스텝 조회 ──
    // 📌 .get() — 단일 객체 반환 (결과 없으면 undefined)
    //    WHERE id = ? AND course_id = ? — 두 조건 동시 만족
    //    두 개의 ?에 각각 stepId, courseId가 순서대로 바인딩
    const step = db.prepare(
      'SELECT * FROM curriculum_steps WHERE id = ? AND course_id = ?'
    ).get(req.params.stepId, req.params.courseId);

    // 📌 스텝이 없으면 404 Not Found
    if (!step) {
      // HTTP 404: 리소스가 존재하지 않음
      return res.status(404).json({
        success: false,
        error: 'Step not found'
      });
    }

    // ── 2) 모듈 정보 조회 (스텝이 속한 모듈의 제목) ──
    // 📌 curriculum_steps의 module_id를 통해 curriculum_modules 조회
    //    ?. (옵셔널 체이닝): moduleInfo가 null/undefined면
    //    전체 표현식이 undefined 반환 (에러 방지)
    const moduleInfo = db.prepare(
      'SELECT title as module_title FROM curriculum_modules WHERE id = ?'
    ).get(step.module_id);

    // ── 3) 이전 스텝 조회 ──
    // 📌 같은 모듈 내에서 order_num이 현재보다 작은(=앞 순서) 스텝 중
    //    가장 최근(가장 큰 order_num) 것을 1개만 조회
    //    ORDER BY order_num DESC: 큰 순서부터 (내림차순)
    //    LIMIT 1: 하나만 가져오기
    const prev = db.prepare(
      'SELECT id FROM curriculum_steps WHERE module_id = ? AND order_num < ? ORDER BY order_num DESC LIMIT 1'
    ).get(step.module_id, step.order_num);

    // ── 4) 다음 스텝 조회 ──
    // 📌 같은 모듈 내에서 order_num이 현재보다 큰(=뒤 순서) 스텝 중
    //    가장 첫 번째 것을 1개만 조회
    //    ORDER BY order_num ASC: 작은 순서부터 (오름차순)
    //    LIMIT 1: 하나만 가져오기
    const next = db.prepare(
      'SELECT id FROM curriculum_steps WHERE module_id = ? AND order_num > ? ORDER BY order_num ASC LIMIT 1'
    ).get(step.module_id, step.order_num);

    // ── 5) 응답 조합 ──
    // 📌 스프레드 연산자로 step 객체를 펼치고 추가 정보 포함
    //    module_title: 모듈 제목 (옵셔널 체이닝으로 null-safe 접근)
    //    course_id: URL 파라미터에서 직접 전달
    //    prev_id / next_id: 이전/다음 스텝 ID (없으면 null)
    res.json({
      success: true,
      step: {
        ...step,
        module_title: moduleInfo?.module_title,
        course_id: req.params.courseId
      },
      prev_id: prev?.id || null,  // 없으면 null
      next_id: next?.id || null   // 없으면 null
    });
    // 📌 ?. (optional chaining): 속성 접근 전에 null/undefined 확인
    //    || (nullish coalescing 대신 OR 연산자): null/undefined 시 대체값
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// ============================================================
// 6-4. POST /api/curriculum/:courseId/step/:stepId/complete — 스텝 완료
// ============================================================
// 📌 RESTful 설계: 동작(action)은 POST로 표현
//    /complete — 리소스에 대한 동작을 경로에 포함
//    (완전한 RESTful에서는 PATCH /api/progress/{id} 방식도 가능)
//
// 📌 POST 메서드의 의미:
//    - 새로운 리소스 생성 (Create)
//    - 또는 특정 동작 실행 (Action)
//    여기서는 "스텝 완료"라는 동작을 실행
app.post('/api/curriculum/:courseId/step/:stepId/complete', (req, res) => {
  try {
    // ── 1) 요청 데이터 추출 ──
    // 📌 req.body: express.json() 미들웨어가 파싱한 요청 본문
    //    POST 요청의 JSON 본문에서 student_id 추출
    //    || {}: req.body가 undefined/null일 때 에러 방지 (기본값)
    //    📌 구조 분해 할당 + 기본값: { student_id = 1 }
    //      student_id 값이 없으면 기본값 1 사용
    const { student_id = 1 } = req.body || {};
    const stepId = req.params.stepId;

    // ── 2) 기존 진행 상황 확인 ──
    // 📌 .get(): 조건에 맞는 단일 행 조회
    //    이미 완료한 적이 있는 스텝인지 확인
    //    WHERE student_id = ? AND step_id = ? — 두 조건 모두 일치
    const existing = db.prepare(
      'SELECT * FROM student_progress WHERE student_id = ? AND step_id = ?'
    ).get(student_id, stepId);

    if (existing) {
      // ── 3a) 기존 기록이 있으면 UPDATE ──
      // 📌 .run(): INSERT/UPDATE/DELETE 등 데이터 변경 쿼리 실행
      //    UPDATE: 기존 행의 값을 변경
      //    SET status = 'completed' : 상태를 '완료'로 변경
      //    SET completed_at = datetime('now') : 현재 시간 기록
      //    SET attempts = attempts + 1 : 시도 횟수 1 증가
      //    📌 datetime('now') : SQLite 내장 함수 — 현재 UTC 시간 반환
      //      SQLite에는 JavaScript의 Date 객체 대신 SQL 함수 사용
      db.prepare(`
        UPDATE student_progress
        SET status = 'completed',
            completed_at = datetime('now'),
            attempts = attempts + 1
        WHERE student_id = ? AND step_id = ?
      `).run(student_id, stepId);
    } else {
      // ── 3b) 기존 기록이 없으면 INSERT ──
      // 📌 INSERT INTO: 새 행을 테이블에 추가
      //    VALUES (?, ?, 'completed', datetime('now'))
      //    student_id, step_id, status='completed', 현재 시간
      //    📌 .run()의 반환값:
      //      { changes: 1, lastInsertRowid: 새 행의 ID }
      db.prepare(`
        INSERT INTO student_progress (student_id, step_id, status, completed_at)
        VALUES (?, ?, 'completed', datetime('now'))
      `).run(student_id, stepId);
    }

    // ── 4) 성공 응답 ──
    // 📌 HTTP 201 (Created):
    //    POST 요청으로 새 리소스가 성공적으로 생성되었을 때 사용
    //    하지만 여기서는 업데이트도 함께 처리하므로 200 OK도 적합
    //    교육용으로 간결하게 res.json() (=200 OK) 사용
    res.json({
      success: true,
      message: '단계 완료 처리되었습니다',
      student_id: parseInt(student_id),
      step_id: parseInt(stepId)
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ============================================================
// 6-5. GET /api/progress/:studentId — 특정 학생의 진도 현황
// ============================================================
// 📌 RESTful 설계: /api/progress/:studentId
//    학생별 학습 진도와 전체 진행률을 조회
//
// 📌 이 엔드포인트는 다음 정보를 제공합니다:
//    1. 각 스텝의 완료 현황 (언제, 몇 번 시도)
//    2. 전체 스텝 수
//    3. 완료한 스텝 수
//    4. 진행률 퍼센트
app.get('/api/progress/:studentId', (req, res) => {
  try {
    // ── 1) 학생의 진행 상세 내역 조회 ──
    // 📌 다중 JOIN (3개 테이블):
    //    student_progress sp (진행 상황)
    //    JOIN curriculum_steps cs (스텝 정보 - 제목)
    //    JOIN curriculum_modules cm (모듈 정보 - 제목 + course_id)
    //
    //    SELECT sp.* : student_progress의 모든 컬럼
    //    cs.title as step_title : 스텝 제목
    //    cm.title as module_title : 모듈 제목
    //    cm.course_id : 강의 ID
    const progress = db.prepare(`
      SELECT sp.*, cs.title as step_title, cm.title as module_title, cm.course_id
      FROM student_progress sp
      JOIN curriculum_steps cs ON sp.step_id = cs.id
      JOIN curriculum_modules cm ON cs.module_id = cm.id
      WHERE sp.student_id = ?
      ORDER BY sp.completed_at DESC
    `).all(req.params.studentId);

    // ── 2) 전체 스텝 수 조회 ──
    // 📌 COUNT(*) : curriculum_steps 테이블의 전체 행 수
    //    모든 학생이 동일한 전체 스텝 수를 가짐
    const total = db.prepare(
      'SELECT COUNT(*) as cnt FROM curriculum_steps'
    ).get();

    // ── 3) 완료한 스텝 수 조회 ──
    // 📌 WHERE + AND: 여러 조건 결합
    //    student_id = ? AND status = 'completed'
    //    특정 학생의 완료된 항목만 필터링
    const completed = db.prepare(
      "SELECT COUNT(*) as cnt FROM student_progress WHERE student_id = ? AND status = 'completed'"
    ).get(req.params.studentId);

    // ── 4) 진행률 계산 ──
    // 📌 삼항 연산자: 조건 ? 참일때값 : 거짓일때값
    //    total.cnt > 0 ? 계산 : 0
    //    0으로 나누기 방지 (division by zero)
    const percentage = total.cnt > 0
      ? Math.round((completed.cnt / total.cnt) * 100)
      : 0;
    // Math.round(): 소수점 반올림

    res.json({
      success: true,
      progress,             // 상세 진행 내역 배열
      total_steps: total.cnt,      // 전체 스텝 수
      completed_steps: completed.cnt, // 완료한 스텝 수
      percentage            // 진행률 (0~100)
    });
  } catch (err) {
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ============================================================
// 7. 서버 시작 (Server Startup)
// ============================================================
// 📌 app.listen(포트, 콜백함수):
//    Express 서버를 지정된 포트에서 시작합니다.
//    내부적으로 Node.js의 http.createServer()를 호출합니다.
//    서버가 성공적으로 시작되면 콜백 함수가 실행됩니다.
//
// 📌 비동기 동작:
//    listen()은 비동기 함수입니다. 서버가 실제로 시작되면
//    콜백이 호출됩니다. (but better-sqlite3 덕분에 여기서는
//    async/await을 사용하지 않아도 됩니다)
app.listen(PORT, () => {
  console.log('');
  console.log('🚀 ======================================');
  console.log(`   코드 교육 실험실 API 서버 시작!`);
  console.log(`   서버 주소: http://localhost:${PORT}`);
  console.log(`   건강 확인: http://localhost:${PORT}/api/health`);
  console.log('==========================================');
  console.log('');
  console.log('📚 사용 가능한 엔드포인트:');
  console.log('   GET /api/health       - 서버 상태 확인');
  console.log('   GET /api/students     - 전체 학생 목록');
  console.log('   GET /api/courses      - 전체 강의 목록 (통계 포함)');
  console.log('   GET /api/courses/:id  - 강의 상세 (레슨+수강생)');
  console.log('   GET /api/lessons      - 레슨 목록 (?course_id=1)');
  console.log('   GET /api/submissions  - 제출물 목록');
  console.log('   GET /api/statistics   - 대시보드 통계');
  console.log('   GET /api/curriculum   - 전체 커리큘럼');
  console.log('   GET /api/curriculum/:courseId   - 강의별 커리큘럼');
  console.log('   GET /api/curriculum/:courseId/step/:stepId  - 스텝 상세');
  console.log('   POST /api/curriculum/:courseId/step/:stepId/complete  - 스텝 완료');
  console.log('   GET /api/progress/:studentId  - 진도 현황');
  console.log('');
});

// ============================================================
// 8. 서버 종료 처리 (Graceful Shutdown)
// ============================================================
// 📌 process.on('SIGINT', 콜백):
//    Node.js 프로세스가 SIGINT 시그널을 받으면 실행됩니다.
//    SIGINT는 터미널에서 Ctrl+C를 누를 때 발생하는 시그널입니다.
//
// 📌 graceful shutdown의 중요성:
//    DB 연결을 안전하게 닫지 않으면 데이터 손상 가능성
//    특히 WAL 모드에서는 정상 종료가 중요
//
// 📌 process.exit(0): 정상 종료 (종료 코드 0)
//    종료 코드 0 = 성공, 0이 아니면 실패를 의미
process.on('SIGINT', () => {
  console.log('\n👋 서버를 종료합니다...');
  db.close();  // 데이터베이스 연결 안전하게 해제
  console.log('✅ 데이터베이스 연결이 해제되었습니다.');
  process.exit(0);
});

// ============================================================
// 📖 HTTP 상태 코드 요약 (학습 참고)
// ============================================================
// 200 OK           — 요청 성공 (GET, PUT)
// 201 Created      — 리소스 생성 성공 (POST)
// 400 Bad Request  — 클라이언트 요청 오류 (잘못된 파라미터 등)
// 404 Not Found    — 요청한 리소스 없음
// 500 Internal Server Error — 서버 내부 오류 (try-catch로 처리)
//
// 📖 SQL 쿼리 절 요약 (학습 참고):
// SELECT  — 조회할 컬럼 지정 (AS로 별칭 가능)
// FROM    — 데이터를 가져올 테이블 지정
// JOIN    — 다른 테이블과 연결 (INNER: 교집합, LEFT: 왼쪽 기준 전체)
// WHERE   — 조건 필터링 (?로 파라미터 바인딩)
// GROUP BY — 행을 그룹화하여 집계 (COUNT, AVG, SUM 등과 함께 사용)
// HAVING  — GROUP BY 후 조건 필터링 (WHERE는 GROUP BY 전)
// ORDER BY — 결과 정렬 (ASC: 오름차순, DESC: 내림차순)
// LIMIT   — 결과 개수 제한
//
// 📖 better-sqlite3 메서드 요약:
// .all()  — 모든 결과 행을 배열로 반환 (목록 조회)
// .get()  — 첫 번째 결과 행을 객체로 반환 (상세 조회)
// .run()  — 쿼리 실행, { changes, lastInsertRowid } 반환 (변경)
