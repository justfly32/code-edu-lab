/*
 * =============================================================================
 * 📄 courses/page.js — 강의 목록 페이지 (/courses)
 * =============================================================================
 *
 * 🎯 이 페이지의 역할:
 *   - Express 백엔드에서 강의(과목) 목록을 가져와 카드 그리드 형태로 표시합니다.
 *   - 각 카드에는 강의명, 설명, 수강생 수, 난이도, 진행 상태가 표시됩니다.
 *   - 학습 포인트: 카드 UI 레이아웃, 조건부 정보 표시, 데이터가 없을 때의 fallback 처리
 *
 * 🔗 Express API: GET http://localhost:3001/api/courses
 *   - 응답 예시: [{ id: 1, name: 'JavaScript 기초', description: '...', studentCount: 30, level: '초급', active: true }]
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어 — 이 파일이 왜 필요한가?
 * =============================================================================
 *
 * 이 페이지는 사용자가 직접 입력하는 요소(onChange)는 없지만,
 * 다음과 같은 이유로 'use client'가 필요합니다:
 *
 * 1️⃣ useState로 courses, loading, error 상태 관리
 * 2️⃣ useEffect로 마운트 시 fetch() 호출
 * 3️⃣ 클라이언트 사이드에서 동적 UI 업데이트
 *
 * ❌ 'use client'가 없다면:
 *   - useState is not defined 에러 발생
 *   - useEffect is not defined 에러 발생
 *   - 서버 컴포넌트에서는 fetch() 결과를 await로 직접 받아도 되지만,
 *     상태 변경(setState)에 따른 동적 업데이트는 불가능합니다.
 *
 * ✅ 서버 컴포넌트라면:
 *   - async 컴포넌트로 선언하고 직접 fetch() 호출
 *   - useState 없이 데이터를 직접 props로 전달
 *   - 예: export default async function CoursesPage() { const data = await fetch(...); return <JSX>; }
 *
 * 하지만 여기서는 학습 목적으로 클라이언트 컴포넌트 패턴을 사용합니다.
 */
'use client';

/*
 * =============================================================================
 * 📦 React Hooks import
 * =============================================================================
 *
 * useState와 useEffect는 React 16.8에서 도입된 Hooks입니다.
 *
 * Hooks 이전 (클래스 컴포넌트):
 *   class CoursesPage extends React.Component {
 *     state = { courses: [], loading: true, error: null };
 *     componentDidMount() { ... fetch ... }
 *     render() { return <JSX>; }
 *   }
 *
 * Hooks 이후 (함수형 컴포넌트):
 *   function CoursesPage() {
 *     const [courses, setCourses] = useState([]);
 *     useEffect(() => { ... fetch ... }, []);
 *     return <JSX>;
 *   }
 *
 * ✅ Hooks의 장점:
 * - 코드가 간결해짐 (class boilerplate 제거)
 * - this 바인딩 문제 없음
 * - 커스텀 Hook으로 로직 재사용 가능
 * - 테스트하기 쉬움
 */
import { useState, useEffect } from 'react';

/*
 * 📦 API 함수 import
 *
 * fetchCourses() 함수:
 * - @/lib/api.js에 정의된 API 호출 함수
 * - 내부 동작: fetch('http://localhost:3001/api/courses') → res.json()
 * - 각 과정 객체: { id, name, title, description, studentCount, level, active }
 *
 * API 함수를 분리한 이유 (관심사 분리, Separation of Concerns):
 * - 페이지 컴포넌트: UI 렌더링에 집중
 * - API 함수: 데이터 페칭과 에러 처리 로직을 캡슐화
 * - 재사용성: 다른 페이지에서도 동일한 API 함수를 호출 가능
 * - 유지보수: API URL이 변경되면 api.js만 수정하면 됨
 */
import { fetchCourses } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ CoursesPage 컴포넌트
 * =============================================================================
 *
 * 컴포넌트 구조:
 * 1. 상태(state) 선언
 * 2. useEffect로 데이터 로딩 (side effect)
 * 3. 조건부 렌더링 (로딩 → 에러 → 메인 콘텐츠)
 * 4. 메인 JSX 반환
 */
export default function CoursesPage() {
  /*
   * =============================================================================
   * 📊 State 선언
   * =============================================================================
   *
   * courses: 강의 목록 배열 (초기값: [])
   *   - API 응답이 배열이라고 가정
   *   - 빈 배열로 초기화하여 map() 호출 안전성 확보
   *
   * loading: 데이터 로딩 상태 (초기값: true)
   *   - true → 로딩 메시지 표시
   *   - false → 실제 카드 목록 표시
   *
   * error: 에러 메시지 (초기값: null)
   *   - null → 정상
   *   - 문자열 → 에러 UI 표시
   *
   * ❓ 왜 error를 null로 초기화할까?
   *   - null은 '값이 없음'을 의미
   *   - if (error) 조건에서 null은 falsy이므로 통과
   *   - 에러 발생 시 문자열이 저장되어 truthy가 됨
   */
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /*
   * =============================================================================
   * 🔄 useEffect — 강의 목록 데이터 로딩
   * =============================================================================
   *
   * async 함수 호출 패턴 설명:
   *
   * 1. useEffect의 콜백은 동기 함수여야 함 (cleanup 함수 반환 가능)
   * 2. 하지만 데이터 페칭은 비동기(async)로 처리해야 함
   * 3. 해결책: 콜백 내부에 async 함수를 정의하고 즉시 호출
   *
   * loadData 함수가 실행되면:
   *   → try 블록: fetchCourses() 호출, 응답을 courses에 저장
   *   → catch 블록: 에러 발생 시 error 상태 업데이트
   *   → finally 블록: loading 상태를 false로 변경
   *
   * 🚨 주의: 의존성 배열이 []이므로, 페이지를 떠났다가 돌아와도
   *   API를 다시 호출하지 않습니다. (캐싱 필요 시 SWR, TanStack Query 사용)
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);                   // 로딩 시작
        const data = await fetchCourses();  // Express API 호출 (blocking)
        setCourses(data);                   // 데이터 저장 → 리렌더링 트리거
      } catch (err) {
        setError(err.message);              // 에러 저장 → 에러 UI 표시
      } finally {
        setLoading(false);                  // 로딩 종료 (항상 실행)
      }
    };
    loadData();  // 정의한 async 함수를 즉시 호출
  }, []);        // 의존성 배열: 빈 배열 → 최초 1회만 실행

  /*
   * =============================================================================
   * 🌀 조건부 렌더링 — Early Return
   * =============================================================================
   *
   * JavaScript의 함수는 return을 만나면 즉시 종료됩니다.
   * 이 특성을 활용하여 각 상태를 분기 처리합니다.
   *
   * 흐름:
   *   1. loading === true → 로딩 UI 반환 (아래 코드는 실행 안 됨)
   *   2. error !== null → 에러 UI 반환
   *   3. 둘 다 아님 → 메인 콘텐츠 반환
   */
  if (loading) return <div className="loading">과목 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">오류: {error}</div>;

  /*
   * =============================================================================
   * ✅ 메인 렌더링 — 강의 카드 그리드
   * =============================================================================
   */
  return (
    <div>
       
      <div>
        <h1 className="page-title">과목 목록</h1>
        <p className="page-subtitle">코드 교육 랩에서 제공하는 과목입니다</p>
      </div>

       
      <div className="card-grid">
        {courses.length > 0 ? (
          courses.map((course, i) => (
            <div className="course-card" key={course.id || i}>
               

               
              <h3 className="course-card-title">
                {course.name || course.title || '과목명 없음'}
                 
              </h3>

               
              <p className="course-card-desc">
                {course.description || '설명이 없습니다'}
              </p>

               
              <div className="course-card-meta">
                <div>
                  {course.studentCount !== undefined && (
                    <span>수강생: {course.studentCount}명</span>
                  )}
                </div>
                <div>
                  {course.level && (
                    <span className="badge badge-info">{course.level}</span>
                  )}
                </div>
              </div>

               
              <div style={{ marginTop: '0.75rem' }}>
                <span className={`badge ${course.active ? 'badge-success' : 'badge-warning'}`}>
                  {course.active ? '진행중' : '종료'}
                </span>
              </div>
            </div>
          ))
        ) : (
           
          <div style={{ color: '#64748b', padding: '2rem', textAlign: 'center' }}>
            등록된 과목이 없습니다
          </div>
        )}
      </div>
    </div>
  );
}

/*
 * =============================================================================
 * 📌 이 페이지에서 배운 핵심 개념
 * =============================================================================
 *
 * 1️⃣ 'use client' — 클라이언트 컴포넌트의 필요성
 * 2️⃣ useState — 3가지 상태(배열, bool, null) 선언 패턴
 * 3️⃣ useEffect — async 함수 호출 패턴 (정의 후 즉시 호출)
 * 4️⃣ try-catch-finally — 데이터 로딩의 완전한 에러 처리
 * 5️⃣ map() + key — 카드 그리드 리스트 렌더링
 * 6️⃣ 삼항 연산자 — 데이터 유무에 따른 UI 분기
 * 7️⃣ && 단락 평가 — 조건이 true일 때만 JSX 표시
 * 8️⃣ || fallback — name || title || '기본값' 패턴
 * 9️⃣ !== undefined — 숫자(0 포함)의 안전한 조건부 렌더링
 * 🔟 인라인 스타일(style={{}}) — 간단한 스타일링
 */
