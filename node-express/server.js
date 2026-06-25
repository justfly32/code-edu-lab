/**
 * ============================================================
 * 코드 교육 실험실 (Code Education Lab) - Express REST API
 * ============================================================
 *
 * 이 서버는 Express.js와 better-sqlite3를 사용하여
 * 학생, 강의, 레슨, 제출물 데이터를 제공하는 REST API입니다.
 *
 * Express 라우팅: 클라이언트 요청을 처리할 엔드포인트를 정의
 * 미들웨어: 요청을 가로채서 전처리하는 함수 (CORS, JSON 파싱 등)
 * SQL 쿼리: better-sqlite3로 동기적으로 데이터베이스에 접근
 */

const express = require('express');   // Express 웹 프레임워크 - HTTP 서버 구축
const cors = require('cors');         // CORS 미들웨어 - 다른 출처의 허용
const Database = require('better-sqlite3'); // SQLite 동기 드라이버 - 교육용으로 적합
const path = require('path');         // 경로 처리 유틸리티
const fs = require('fs');             // 파일 시스템 - DB 파일 존재 확인용

// ============================================================
// 앱 및 포트 설정
// ============================================================
const app = express();  // Express 애플리케이션 인스턴스 생성
const PORT = 3001;      // 서버 포트 번호

// ============================================================
// 데이터베이스 경로 및 시드 확인 (Seed Check)
// ============================================================
// 공유 SQLite 데이터베이스 경로 설정
const DB_PATH = path.resolve(__dirname, '../code-edu-lab/shared/db/edu.db');

// 서버 시작 시 DB 파일 존재 여부 확인
// 파일이 없으면 에러 메시지를 출력하고 서버를 종료합니다
if (!fs.existsSync(DB_PATH)) {
  console.error(`❌ 데이터베이스 파일을 찾을 수 없습니다: ${DB_PATH}`);
  console.error('   먼저 seed.py를 실행하여 데이터베이스를 초기화하세요.');
  process.exit(1); // 프로세스 종료 (코드 1 = 에러)
}

// better-sqlite3 데이터베이스 인스턴스 생성
// verbose 모드로 쿼리 로깅 (교육용 - 학생들이 쿼리를 확인할 수 있음)
const db = new Database(DB_PATH, {
  verbose: console.log // 모든 SQL 쿼리를 콘솔에 출력 (학습 목적)
});

// WAL 모드 활성성 - 읽기 성능 향상
db.pragma('journal_mode = WAL');

console.log(`✅ 데이터베이스 연결 완료: ${DB_PATH}`);

// ============================================================
// 미들웨어 설정 (Middleware)
// ============================================================
// CORS 미들웨어: 모든 출처에서의 요청을 허용
// 교육 환경에서 프론트엔드(React, Vue 등)와 연동하기 위해 사용
app.use(cors());

// JSON 미들웨어: 요청 본문을 자동으로 파싱
// Express 4.16+ 내장 기능 (body-parser 불필요)
app.use(express.json());

// 요청 로깅 미들웨어: 모든 HTTP 요청을 콘솔에 기록
// 디버깅 및 학습 목적으로 유용
app.use((req, res, next) => {
  console.log(`📨 ${req.method} ${req.url} - ${new Date().toISOString()}`);
  next(); // 다음 미들웨어로 제어를 넘김
});

// ============================================================
// API 라우트 정의 (Routes)
// ============================================================

// ----------------------------------------------------------
// GET /api/health - 상태 확인 (Health Check)
// 서버가 정상적으로 실행 중인지 확인하는 엔드포인트
// ----------------------------------------------------------
app.get('/api/health', (req, res) => {
  // JSON 응답: 서버 상태, 포트, DB 연결 상태
  res.json({
    status: 'ok',                    // 서버 상태
    message: '서버가 정상 실행 중입니다', // 상태 메시지 (한국어)
    port: PORT,                      // 서버 포트
    database: 'connected',           // DB 연결 상태
    timestamp: new Date().toISOString() // 현재 시간
  });
});

// ----------------------------------------------------------
// GET /api/students - 전체 학생 목록 조회
// SQL: SELECT * FROM students ORDER BY created_at DESC
// ----------------------------------------------------------
app.get('/api/students', (req, res) => {
  try {
    // better-sqlite3의 all() 메서드: 모든 결과를 배열로 반환 (동기)
    // ORDER BY created_at DESC: 최근 가입한 학생부터 정렬
    const students = db.prepare(
      'SELECT * FROM students ORDER BY created_at DESC'
    ).all();

    // JSON 응답: 학생 목록과 총 수
    res.json({
      success: true,          // 요청 성공 여부
      count: students.length, // 반환된 학생 수
      data: students          // 학생 데이터 배열
    });
  } catch (err) {
    // 에러 처리: 500 상태 코드와 에러 메시지 반환
    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ----------------------------------------------------------
// GET /api/courses - 전체 강의 목록 (통계 포함)
// SQL: 강의별 학생 수, 레슨 수를 JOIN으로 집계
// ----------------------------------------------------------
app.get('/api/courses', (req, res) => {
  try {
    // 강의 기본 정보 + 통계 (수강생 수, 레슨 수)
    // LEFT JOIN: 수강생이나 레슨이 없는 강의도 포함
    // COUNT(DISTINCT ...): 중복 제거하여 정확한 수 계산
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
// GET /api/courses/:id - 강의 상세 정보
// 특정 강의의 레슨 목록과 수강생 정보를 함께 반환
// URL 파라미터: :id = 강의 ID
// ----------------------------------------------------------
app.get('/api/courses/:id', (req, res) => {
  try {
    const courseId = parseInt(req.params.id); // URL에서 ID 추출

    // 숫자가 아닌 경우 400 에러 반환
    if (isNaN(courseId)) {
      return res.status(400).json({
        success: false,
        error: '유효한 강의 ID를 입력하세요'
      });
    }

    // 1) 강의 기본 정보 조회
    const course = db.prepare(
      'SELECT * FROM courses WHERE id = ?'
    ).get(courseId); // get(): 단일 행 반환

    // 강의가 없으면 404 에러
    if (!course) {
      return res.status(404).json({
        success: false,
        error: '강의를 찾을 수 없습니다'
      });
    }

    // 2) 해당 강의의 레슨 목록 조회 (순서대로 정렬)
    const lessons = db.prepare(
      'SELECT * FROM lessons WHERE course_id = ? ORDER BY order_num ASC'
    ).all(courseId);

    // 3) 해당 강의의 수강생 목록 조회 (JOIN으로  학생 정보 포함)
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

    // 통합된 응답 반환
    res.json({
      success: true,
      data: {
        course,      // 강의 기본 정보
        lessons,     // 레슨 목록
        enrollments  // 수강생 목록
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
// GET /api/lessons - 전체 레슨 목록
// 쿼리 파라미터: ?course_id=1 (특정 강의의 레슨만 필터링)
// ----------------------------------------------------------
app.get('/api/lessons', (req, res) => {
  try {
    const { course_id } = req.query; // 쿼리 파라미터 추출

    let sql = 'SELECT * FROM lessons';
    let params = [];

    // course_id가 있으면 WHERE 조건 추가 (동적 쿼리 생성)
    if (course_id) {
      sql += ' WHERE course_id = ?';
      params.push(parseInt(course_id));
    }

    sql += ' ORDER BY course_id, order_num ASC'; // 강의별, 순서별 정렬

    // better-sqlite3의 prepare + all: 파라미터 바인딩으로 SQL 인젝션 방지
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
// GET /api/submissions - 제출물 목록 (학생/강의 정보 포함)
// JOIN을 통해 학생 이름, 강의 제목, 레슨 제목을 함께 반환
// ----------------------------------------------------------
app.get('/api/submissions', (req, res) => {
  try {
    // 다중 JOIN: submissions → students, lessons → courses
    // 제출물과 관련된 모든 정보를 한 번에 가져옴
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
// GET /api/statistics - 대시보드 통계
// 전체 현황을 집계하여 대시보드에 표시할 데이터 제공
// ----------------------------------------------------------
app.get('/api/statistics', (req, res) => {
  try {
    // 1) 전체 학생 수 집계
    const studentCount = db.prepare(
      'SELECT COUNT(*) as count FROM students'
    ).get();

    // 2) 전체 강의 수 집계
    const courseCount = db.prepare(
      'SELECT COUNT(*) as count FROM courses'
    ).get();

    // 3) 전체 레슨 수 집계
    const lessonCount = db.prepare(
      'SELECT COUNT(*) as count FROM lessons'
    ).get();

    // 4) 전체 수강 신청 수 집계
    const enrollmentCount = db.prepare(
      'SELECT COUNT(*) as count FROM enrollments'
    ).get();

    // 5) 전체 제출물 수 집계
    const submissionCount = db.prepare(
      'SELECT COUNT(*) as count FROM submissions'
    ).get();

    // 6) 평균 점수 집계 (AVG 함수 사용)
    const avgScore = db.prepare(
      'SELECT AVG(score) as average FROM submissions'
    ).get();

    // 7) 강의별 수강생 수 (차트 데이터용)
    const coursePopularity = db.prepare(`
      SELECT
        c.title,
        c.instructor,
        COUNT(e.id) as student_count
      FROM courses c
      LEFT JOIN enrollments e ON c.id = e.course_id
      GROUP BY c.id
      ORDER BY student_count DESC
    `).all();

    // 8) 레벨별 강의 수
    const levelDistribution = db.prepare(`
      SELECT level, COUNT(*) as count
      FROM courses
      GROUP BY level
    `).all();

    // 통합 통계 응답
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
            : 0
        },
        coursePopularity,  // 강의별 인기도
        levelDistribution  // 레벨별 분포
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
// 서버 시작
// ============================================================
// Express 서버를 지정된 포트에서 시작
// 시작 완료 시 콘솔에 메시지 출력
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
  console.log('');
});

// ============================================================
// 정리 작업: 서버 종료 시 DB 연결 해제
// ============================================================
// SIGINT (Ctrl+C) 시그널을 받으면 실행
process.on('SIGINT', () => {
  console.log('\n👋 서버를 종료합니다...');
  db.close(); // 데이터베이스 연결 해제
  console.log('✅ 데이터베이스 연결이 해제되었습니다.');
  process.exit(0); // 정상 종료 (코드 0)
});
