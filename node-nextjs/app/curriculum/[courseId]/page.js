/*
 * =============================================================================
 * 📄 curriculum/[courseId]/page.js — 특정 강의 커리큘럼 상세 페이지
 * =============================================================================
 *
 * 🧭 이 파일이 위치한 경로: app/curriculum/[courseId]/page.js
 *
 * 🔗 실제 URL: /curriculum/javascript-basics  (또는 /curriculum/1, /curriculum/react-master 등)
 *
 * 🎯 이 페이지의 역할:
 *   - 특정 과목(courseId)의 상세 커리큘럼을 표시합니다.
 *   - 모듈 목록을 아코디언(accordion) 형태로 표시하여 각 모듈의 스텝을 볼 수 있습니다.
 *   - 각 스텝을 클릭하면 개별 스텝 페이지(/curriculum/{courseId}/{stepId})로 이동합니다.
 *   - 학습 포인트: 동적 라우트 파라미터(courseId) 사용법, 아코디언 UI 패턴,
 *     중첩된 map()으로 계층적 데이터 렌더링, Link로 상세 페이지 이동
 *
 * 🔗 Express API: GET http://localhost:3001/api/courses/:courseId/modules
 *   - 응답 예시: { course: { id, name, title, description }, modules: [{ id, name, steps: [...] }] }
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어
 * =============================================================================
 *
 * 이 페이지에서 'use client'가 필요한 이유:
 * 1. useState: courseData, loading, error, expandedModules 상태 관리
 * 2. useEffect: courseId가 변경될 때 데이터 재로딩
 * 3. onClick: 모듈 토글 버튼 클릭 처리 (toggleModule 함수)
 * 4. useParams: URL의 동적 파라미터(courseId) 읽기
 *
 * ❌ 'use client'가 없으면 발생하는 문제:
 * - useState is not defined → React Hooks를 찾을 수 없음
 * - onClick 이벤트 핸들러가 동작하지 않음 (서버에서는 이벤트를 처리할 수 없음)
 * - useParams 대신 props.params로 접근해야 함 (서버 컴포넌트 방식)
 *
 * ✅ 서버 컴포넌트에서 동적 파라미터 접근:
 *   export default async function CourseDetailPage({ params }) {
 *     const { courseId } = params;  // props로 params를 직접 받음
 *     const data = await fetch(...);
 *     return <JSX>;
 *   }
 */
'use client';

import { useState, useEffect } from 'react';

/*
 * =============================================================================
 * 🔗 Link 컴포넌트
 * =============================================================================
 *
 * Next.js의 Link 컴포넌트는 클라이언트 사이드 라우팅을 구현합니다.
 *
 * 브레드크럼(Breadcrumb) 네비게이션에 사용:
 * - 커리큘럼 > [과목명]
 * - 사용자가 현재 위치를 파악할 수 있도록 돕는 UI 패턴
 * - 각 단계를 클릭하면 이전 페이지로 이동 가능
 */
import Link from 'next/link';

/*
 * =============================================================================
 * 📦 useParams Hook — URL 동적 파라미터 읽기
 * =============================================================================
 *
 * useParams는 Next.js 13+ App Router에서 제공하는 훅입니다.
 * 현재 URL의 동적 파라미터(폴더명이 [param]으로 된 부분) 값을 가져옵니다.
 *
 * 파일 시스템 라우팅 vs 동적 파라미터:
 *
 *   app/
 *     curriculum/
 *       [courseId]/         ← 대괄호로 감싸면 동적 파라미터
 *         page.js           ← useParams().courseId로 접근
 *         [stepId]/
 *           page.js         ← useParams().courseId, useParams().stepId로 접근
 *
 * 예시:
 * - URL: /curriculum/javascript-basics
 * - params = { courseId: 'javascript-basics' }
 * - URL: /curriculum/123
 * - params = { courseId: '123' }
 *
 * 실제 사용 예:
 *   const params = useParams();
 *   const courseId = params.courseId;  // 'javascript-basics' 또는 '123'
 *
 * 구조 분해 할당으로 한 번에:
 *   const { courseId } = useParams();
 *
 * ⚠️ 주의: useParams()는 클라이언트 컴포넌트에서만 사용 가능합니다.
 * 서버 컴포넌트에서는 props.params를 사용합니다.
 *
 * @/next/navigation vs @/next/router:
 * - Next.js 13 App Router에서는 'next/navigation'을 사용합니다.
 * - 구버전 Pages Router에서는 'next/router'의 useRouter()를 사용했습니다.
 */
import { useParams } from 'next/navigation';

/*
 * 📦 API 함수 import
 *
 * fetchCourseModules(courseId):
 * - GET http://localhost:3001/api/courses/:courseId/modules
 * - courseId를 인자로 받아 해당 과목의 모듈과 스텝 데이터를 조회
 * - 응답: { course: {...}, modules: [{ id, name, steps: [{ id, title, completed }] }] }
 */
import { fetchCourseModules } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ CourseDetailPage 컴포넌트
 * =============================================================================
 */
export default function CourseDetailPage() {
  /*
   * =============================================================================
   * 📍 URL 파라미터 읽기
   * =============================================================================
   *
   * useParams() 훅을 호출하면 현재 URL의 모든 동적 파라미터를 담은 객체를 반환합니다.
   * 이 경로는 /curriculum/[courseId]이므로 params.courseId에 값이 있습니다.
   */
  const params = useParams();
  const courseId = params.courseId;

  /*
   * =============================================================================
   * 📊 State 선언
   * =============================================================================
   *
   * courseData: API 응답 데이터 전체 (null → 데이터 로딩 중)
   *   - courseData.course: 과목 정보 { id, name, title, description }
   *   - courseData.modules: 모듈 배열 [{ id, name, title, steps: [...] }]
   *
   * expandedModules: 아코디언 상태 관리 객체
   *   - { [moduleId]: true/false } 형태
   *   - true: 모듈이 펼쳐짐 (스텝 목록 표시)
   *   - false: 모듈이 접힘 (스텝 목록 숨김)
   *   - 예: { 'mod-1': true, 'mod-2': false, 'mod-3': false }
   *   - 첫 번째 모듈은 기본으로 펼쳐짐 (data.modules[0].id → true)
   */
  const [courseData, setCourseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedModules, setExpandedModules] = useState({});

  /*
   * =============================================================================
   * 🔄 useEffect — courseId 변경 시 데이터 로딩
   * =============================================================================
   *
   * ⚠️ 의존성 배열에 [courseId]가 있습니다!
   *
   * 이전 페이지들과 달리 의존성 배열이 비어 있지 않습니다.
   * 이유: courseId가 변경될 때마다 새로운 과목의 데이터를 로드해야 합니다.
   *
   * 시나리오:
   * 1. 사용자가 /curriculum/javascript-basics 접속
   *    → courseId = 'javascript-basics'
   *    → useEffect 실행 → 데이터 로드
   * 2. 사용자가 Link로 /curriculum/react-master로 이동
   *    → courseId = 'react-master' (변경됨)
   *    → useEffect 재실행 → 새 데이터 로드
   *    → 이전 데이터 정리(cleanup) 후 새 데이터 표시
   *
   * 의존성 배열 패턴:
   * - [] (빈 배열): 마운트 시 1회 실행
   * - [courseId]: courseId가 변경될 때마다 실행
   * - [courseId, stepId]: 둘 중 하나라도 변경되면 실행
   * - 생략: 매 렌더링마다 실행 (거의 사용 안 함)
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchCourseModules(courseId);
        setCourseData(data);

        /*
         * 첫 번째 모듈 자동 펼침:
         * 데이터 로딩 후 modules 배열이 있으면 첫 번째 모듈을 기본으로 펼칩니다.
         * 객체 키를 동적으로 설정: { [data.modules[0].id]: true }
         *
         * 계산된 속성명 (Computed Property Names):
         * - 객체의 키를 변수나 표현식으로 동적으로 설정
         * - [key]: value 형태
         * - 예: { [module.id]: true } → { 'mod-abc-123': true }
         */
        if (data?.modules && data.modules.length > 0) {
          setExpandedModules({ [data.modules[0].id]: true });
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [courseId]);  // ✅ courseId가 변경되면 재실행

  /*
   * =============================================================================
   * ↩️ 모듈 토글 함수 (아코디언 열기/닫기)
   * =============================================================================
   *
   * 이 함수는 모듈 헤더 버튼의 onClick 핸들러로 연결됩니다.
   * 사용자가 모듈 헤더를 클릭할 때마다 호출됩니다.
   *
   * setExpandedModules((prev) => ({ ...prev, [moduleId]: !prev[moduleId] }));
   *
   * 이 패턴의 특징:
   * 1. 함수형 업데이트 (Functional Update):
   *    - setState(새값) 대신 setState((prev) => 새값) 사용
   *    - 이전 상태(prev)를 기반으로 새 상태 계산
   *    - 여러 번 호출되어도 각각 최신 prev를 사용하여 안전
   *
   * 2. 스프레드 연산자 (...prev):
   *    - prev 객체의 모든 속성을 새 객체에 복사
   *    - 기존 상태를 유지하면서 특정 키만 업데이트
   *    - 불변성(Immutability) 유지: 객체를 직접 수정하지 않고 새 객체 생성
   *
   * 3. 계산된 속성명 [moduleId]:
   *    - moduleId 변수값을 객체 키로 사용
   *    - !prev[moduleId]: 현재 값을 반전 (true→false, false→true)
   *
   * 예시:
   *   prev = { 'mod-1': true, 'mod-2': false }
   *   toggleModule('mod-2') 호출
   *   → { ...prev, ['mod-2']: !false }
   *   → { 'mod-1': true, 'mod-2': true }
   */
  const toggleModule = (moduleId) => {
    setExpandedModules((prev) => ({
      ...prev,
      [moduleId]: !prev[moduleId],
    }));
  };

  /*
   * =============================================================================
   * 🌀 조건부 렌더링
   * =============================================================================
   */
  if (loading) {
    return <div className="loading">과목 정보를 불러오는 중...</div>;
  }

  if (error) {
    return (
      <div className="error-message">
        오류: {error}
        <br />
        <small>Express 서버가 http://localhost:3001에서 실행 중인지 확인해주세요.</small>
      </div>
    );
  }

  /*
   * =============================================================================
   * 📊 데이터 계산 (진행률 등)
   * =============================================================================
   *
   * 모듈 데이터를 기반으로 진행률을 계산합니다.
   * 중첩된 reduce():
   * - 외부 reduce(): 모듈 배열 순회
   * - 내부 filter().length: 각 모듈의 steps 배열에서 completed가 true인 항목 카운트
   *
   * flatMap() 대안:
   *   modules.flatMap(m => m.steps).filter(s => s.completed).length
   *   - 모든 스텝을 하나의 배열로 평탄화 후 필터링
   *   - 가독성은 좋지만 중첩 객체 접근이 필요할 때는 reduce()가 유연
   */
  const course = courseData?.course || {};
  const modules = courseData?.modules || [];
  const totalSteps = modules.reduce((sum, m) => sum + (m.steps?.length || 0), 0);
  const completedSteps = modules.reduce(
    (sum, m) => sum + (m.steps?.filter((s) => s.completed).length || 0),
    0
  );
  const progress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  /*
   * =============================================================================
   * ✅ 메인 렌더링
   * =============================================================================
   */
  return (
    <div>
       
      <nav style={{ marginBottom: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <Link href="/curriculum" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
          커리큘럼
        </Link>
        {' > '}
        <span>{course.name || course.title || courseId}</span>
      </nav>

       
      <div>
        <h1 className="page-title">{course.name || course.title || '과목명 없음'}</h1>
        <p className="page-subtitle">{course.description || '과목 설명이 없습니다'}</p>
      </div>

       
      <div className="stat-card" style={{ marginBottom: '2rem' }}>
        <div className="stat-card-label">과목 진행률</div>
        <div className="stat-card-value">{progress}%</div>
        <div className="progress-bar-container" style={{ marginTop: '0.75rem' }}>
          <div className="progress-bar-bg">
            <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>
        <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          {completedSteps}/{totalSteps} 스텝 완료 ({modules.length}개 모듈)
        </div>
      </div>

       
      <div className="module-list">
        {modules.length > 0 ? (
          modules.map((module, moduleIndex) => (
            <div key={module.id || moduleIndex} className="module-item">
               
              <button
                className="module-header"
                onClick={() => toggleModule(module.id)}
                style={{
                  width: '100%',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '1rem 1.25rem',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '0.5rem',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',          // 마우스 오버 시 손가락 커서
                  fontSize: '1rem',
                  fontWeight: 600,
                  textAlign: 'left',
                }}
              >
                <span>
                  {moduleIndex + 1}. {module.name || module.title || '모듈명 없음'}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {module.steps?.length || 0}개 스텝{' '}
                  {expandedModules[module.id] ? '▲' : '▼'}
                   
                </span>
              </button>

               
              {expandedModules[module.id] && module.steps && (
                <div className="module-steps" style={{ padding: '0.5rem 0' }}>
                  {module.steps.map((step, stepIndex) => (
                    <Link
                      key={step.id || stepIndex}
                      href={`/curriculum/${courseId}/${step.id}`}
                      /*
                       * 동적 경로 생성: 템플릿 리터럴 사용
                       * - courseId와 step.id를 결합하여 URL 생성
                       * - 결과: /curriculum/javascript-basics/step-1
                       *
                       * Link href:
                       * - 절대 경로: href="/curriculum/js/step1"
                       * - 상대 경로: href={`${courseId}/${step.id}`} (권장 안 함)
                       * - 항상 절대 경로를 사용하는 것이 안전합니다.
                       */
                      className="step-link"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0.75rem 1rem',
                        marginLeft: '1rem',
                        marginBottom: '0.25rem',
                        backgroundColor: 'var(--bg-primary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '0.375rem',
                        textDecoration: 'none',  // Link의 밑줄 제거
                        color: 'var(--text-primary)',
                        transition: 'background-color 0.2s',  // 호버 효과 (CSS 전환)
                      }}
                    >
                       
                      <span
                        style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '50%',
                          border: `2px solid ${step.completed ? 'var(--accent-success)' : 'var(--border-color)'}`,
                          backgroundColor: step.completed ? 'var(--accent-success)' : 'transparent',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginRight: '0.75rem',
                          fontSize: '0.7rem',
                          color: 'white',
                          flexShrink: 0,
                        }}
                      >
                        {step.completed ? '✓' : ''}
                      </span>

                       
                      <span style={{ flex: 1 }}>
                        <span style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }}>
                          {stepIndex + 1}.
                        </span>
                        {step.title || step.id}
                      </span>

                       
                      <span style={{ color: 'var(--text-muted)' }}>→</span>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))
        ) : (
          <div style={{ color: '#64748b', padding: '2rem', textAlign: 'center' }}>
            이 과목에는 아직 모듈이 없습니다.
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
 * 1️⃣ useParams() — URL 동적 파라미터(courseId) 읽기
 * 2️⃣ 파일 시스템 라우팅 — [courseId] 폴더가 동적 라우트를 만듦
 * 3️⃣ useEffect 의존성 배열 [courseId] — 파라미터 변경 시 데이터 재로딩
 * 4️⃣ 아코디언 UI — onClick 토글 + 조건부 렌더링으로 구현
 * 5️⃣ 함수형 업데이트 — setState((prev) => ...prev)
 * 6️⃣ 스프레드 연산자 + 계산된 속성명 — 불변성 유지하며 상태 업데이트
 * 7️⃣ 중첩 map() — 모듈 배열 > 스텝 배열 계층적 렌더링
 * 8️⃣ Link로 동적 경로 생성 — `/curriculum/${courseId}/${step.id}`
 * 9️⃣ 브레드크럼 네비게이션 — 현재 위치 표시 UI 패턴
 * 🔟 조건부 스타일링 — 완료 상태에 따른 동그라미 아이콘
 */
