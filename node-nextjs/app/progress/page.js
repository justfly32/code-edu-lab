/*
 * =============================================================================
 * 📄 progress/page.js — 학습 진도 페이지 (/progress)
 * =============================================================================
 *
 * 🎯 이 페이지의 역할:
 *   - Express 백엔드에서 커리큘럼 데이터를 가져와 학습 진행 상황을 시각화합니다.
 *   - 전체 진행 통계(4개 KPI), 전체 진행률 바, 과목별 상세 진행 현황을 표시합니다.
 *   - 학습 포인트: 통계 시각화, 과목별 진행률 계산, 조건부 뱃지 스타일링,
 *     Link로 과목 상세 페이지 연결, 학습 팁 섹션 (정적 콘텐츠)
 *
 * 🔗 Express API: GET http://localhost:3001/api/curriculum/overview
 *   (curriculum/page.js와 동일한 API 사용)
 *
 * 📌 참고: progress 페이지와 curriculum 페이지는 같은 API를 사용하지만
 *   표시 방식이 다릅니다. curriculum은 개요/카드 중심, progress는 진행률에 초점.
 *   이는 같은 데이터를 여러 관점으로 시각화하는 패턴의 좋은 예시입니다.
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어
 * =============================================================================
 *
 * 이 페이지가 클라이언트 컴포넌트인 이유:
 * - useState로 curriculum 데이터 상태 관리
 * - useEffect로 API 데이터 페칭
 * - Link 컴포넌트로 페이지 이동 (서버 컴포넌트에서도 가능)
 *
 * 만약 서버 컴포넌트로 리팩토링한다면:
 * - async 컴포넌트로 변경: export default async function ProgressPage()
 * - 직접 fetch() 호출: const data = await fetchCurriculumOverview()
 * - 상태 관리 불필요 (데이터를 변수에 직접 할당)
 * - 로딩 처리는 loading.js, 에러 처리는 error.js에서 담당
 * - 번들 크기가 줄어들고 초기 로딩이 빨라짐
 *
 * "가능하면 서버 컴포넌트를 먼저 고려하라"는 Next.js 공식 권장사항이지만,
 * 학습 목적으로 클라이언트 컴포넌트 패턴을 유지합니다.
 */
'use client';

import { useState, useEffect } from 'react';

/*
 * =============================================================================
 * 🔗 Link 컴포넌트
 * =============================================================================
 *
 * Link는 Next.js에서 페이지 이동을 담당하는 핵심 컴포넌트입니다.
 *
 * 사용 패턴 (이 페이지에서):
 * - 과목명을 클릭하면 해당 과목의 상세 커리큘럼 페이지로 이동
 * - href={`/curriculum/${course.id}`} 형태로 동적 경로 생성
 *
 * ✅ Link의 동작 방식:
 * 1. 사용자가 Link 위에 마우스를 올리면 (hover)
 *    → Next.js가 해당 페이지를 미리 로드 (prefetch)
 * 2. 사용자가 클릭
 *    → 페이지 전체를 새로고침하지 않고 JavaScript로 필요한 부분만 교체
 * 3. 결과: 네이티브 앱처럼 빠른 페이지 전환
 */
import Link from 'next/link';

/*
 * 📦 API 함수 import
 *
 * fetchCurriculumOverview():
 * - GET http://localhost:3001/api/curriculum/overview
 * - 커리큘럼 전체 데이터 조회 (courses 배열, modules 배열 등)
 *
 * curriculum/page.js와 같은 API를 사용하지만,
 * 표시하는 방식이 다릅니다 (재사용성의 좋은 예).
 */
import { fetchCurriculumOverview } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ ProgressPage 컴포넌트
 * =============================================================================
 */
export default function ProgressPage() {
  /*
   * =============================================================================
   * 📊 State 선언
   * =============================================================================
   *
   * curriculum: API 응답 전체 데이터 (초기값: null)
   *   - curriculum?.courses: 과목별 진행 데이터 배열
   *
   * loading, error: 표준 로딩/에러 상태
   */
  const [curriculum, setCurriculum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /*
   * =============================================================================
   * 🔄 useEffect — 데이터 로딩
   * =============================================================================
   *
   * 이전 페이지들과 동일한 패턴:
   * 1. async 함수 정의 (loadData)
   * 2. useEffect 내에서 즉시 호출
   * 3. 의존성 배열 []: 마운트 시 1회 실행
   *
   * 🔄 fetch() 호출 흐름 (api.js 내부):
   *
   *   const response = await fetch('http://localhost:3001/api/curriculum/overview');
   *   // 1. 브라우저가 Express 서버(port 3001)로 HTTP GET 요청을 보냄
   *   // 2. 서버가 데이터베이스를 조회하여 JSON 응답을 반환
   *   // 3. response: { ok: true, status: 200, body: ReadableStream, ... }
   *
   *   if (!response.ok) {
   *     throw new Error('HTTP error! status: ' + response.status);
   *   }
   *   // 4. HTTP 상태 코드가 200-299가 아니면 에러 throw
   *   //    (404 Not Found, 500 Internal Server Error 등)
   *
   *   return response.json();
   *   // 5. JSON 응답 본문을 JavaScript 객체로 변환 (Promise 반환)
   *   // 6. 반환된 객체: { courses: [...], modules: [...] }
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchCurriculumOverview();
        setCurriculum(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  /*
   * =============================================================================
   * 📊 통계 계산 (배열 메서드 활용)
   * =============================================================================
   *
   * courses 배열에서 데이터 추출:
   *
   * 1. courses = curriculum?.courses || []
   *    - curriculum이 null/undefined면 빈 배열로 대체
   *    - 이후의 reduce(), length 등이 안전하게 동작
   *
   * 2. totalSteps = courses.reduce((sum, c) => sum + (c.totalSteps || 0), 0)
   *    - 각 course의 totalSteps를 누적 합산
   *    - c.totalSteps가 undefined면 0으로 처리 (|| 0)
   *
   * 3. completedSteps = courses.reduce(...)
   *    - 각 course의 completedSteps를 누적 합산
   *
   * 4. overallProgress = Math.round((completedSteps / totalSteps) * 100)
   *    - 전체 진행률을 백분율로 계산
   *    - Math.round(): 반올림 (소수점 제거)
   *    - totalSteps > 0 ? ... : 0 (0으로 나누기 방지)
   */
  const courses = curriculum?.courses || [];
  const totalSteps = courses.reduce((sum, c) => sum + (c.totalSteps || 0), 0);
  const completedSteps = courses.reduce((sum, c) => sum + (c.completedSteps || 0), 0);
  const overallProgress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  /*
   * =============================================================================
   * 🌀 조건부 렌더링
   * =============================================================================
   */
  if (loading) {
    return <div className="loading">진행 현황을 불러오는 중...</div>;
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
   * ✅ 메인 렌더링
   * =============================================================================
   */
  return (
    <div>
       
      <div>
        <h1 className="page-title">학습 현황</h1>
        <p className="page-subtitle">나의 학습 진행 상황을 확인하세요</p>
      </div>

       
      <div className="stats-grid" style={{ marginBottom: '2rem' }}>
        <div className="stat-card">
          <div className="stat-card-label">전체 진행률</div>
          <div className="stat-card-value">{overallProgress}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">완료한 스텝</div>
          <div className="stat-card-value">{completedSteps}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">전체 스텝</div>
          <div className="stat-card-value">{totalSteps}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">등록 과목</div>
          <div className="stat-card-value">{courses.length}</div>
        </div>
      </div>

       
      <div className="chart-container" style={{ marginBottom: '2rem' }}>
        <h3 className="chart-title">전체 학습 진행률</h3>
        <div className="progress-bar-container">
          <div className="progress-bar-bg" style={{ height: '24px' }}>
            <div
              className="progress-bar-fill"
              style={{ width: `${overallProgress}%`, height: '100%' }}
            />
          </div>
          <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: '1.2rem', fontWeight: 700 }}>
            {overallProgress}%
          </div>
        </div>
      </div>

       
      <h2 className="chart-title">과목별 진행 현황</h2>
      <div className="course-progress-list" style={{ marginTop: '1rem' }}>
        {courses.length > 0 ? (
          courses.map((course, i) => {
            /*
             * 각 과목별 진행률 계산:
             * - 이 변수들은 map() 콜백 내부에서만 유효 (블록 스코프)
             * - 각 과목마다 독립적으로 계산됨
             *
             * const와 let의 차이:
             * - const: 재할당 불가 (한 번 할당하면 값 변경 불가)
             * - let: 재할당 가능
             * - 가능하면 const 사용 (의도치 않은 변경 방지)
             */
            const cTotal = course.totalSteps || 0;
            const cCompleted = course.completedSteps || 0;
            const cProgress = cTotal > 0 ? Math.round((cCompleted / cTotal) * 100) : 0;

            return (
              <div
                key={course.id || i}
                className="course-progress-item"
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '0.75rem',
                  padding: '1.25rem',
                  marginBottom: '1rem',
                }}
              >
                 
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <Link
                    href={`/curriculum/${course.id}`}
                    style={{
                      fontSize: '1.1rem',
                      fontWeight: 600,
                      color: 'var(--text-primary)',
                      textDecoration: 'none',
                    }}
                  >
                    {course.name || course.title || '과목명 없음'}
                  </Link>
                  <span className={`badge ${cProgress === 100 ? 'badge-success' : cProgress > 0 ? 'badge-info' : 'badge-warning'}`}>
                    {cProgress === 100 ? '완료' : cProgress > 0 ? '진행중' : '시작전'}
                  </span>
                </div>

                 
                {course.description && (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                    {course.description}
                  </p>
                )}

                 
                <div className="progress-bar-container">
                  <div className="progress-bar-bg">
                    <div className="progress-bar-fill" style={{ width: `${cProgress}%` }} />
                  </div>
                  <span className="progress-text">
                    {cCompleted}/{cTotal} 스텝 ({cProgress}%)
                  </span>
                </div>
              </div>
            );
          })
        ) : (
          <div style={{ color: '#64748b', padding: '2rem', textAlign: 'center' }}>
            등록된 과목이 없습니다.
          </div>
        )}
      </div>

       
      <div className="chart-container" style={{ marginTop: '2rem' }}>
        <h3 className="chart-title">💡 학습 팁</h3>
        <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-secondary)', lineHeight: 2 }}>
          <li>각 스텝을 순서대로 진행하는 것을 권장합니다</li>
          <li>코드 예제를 직접 입력해보면 더 효과적으로 학습할 수 있습니다</li>
          <li>힌트가 필요할 때만 힌트를 확인하고, 먼저 스스로 생각해보세요</li>
          <li>완료 버튼을 눌러 진행 상황을 기록하세요</li>
        </ul>
      </div>
    </div>
  );
}

/*
 * =============================================================================
 * 📌 이 페이지에서 배운 핵심 개념
 * =============================================================================
 *
 * 1️⃣ 'use client' — 클라이언트 컴포넌트의 역할과 서버 컴포넌트로의 변환 가능성
 * 2️⃣ useState/useEffect — 표준 데이터 페칭 패턴
 * 3️⃣ async/await + try-catch-finally — 완전한 에러 처리
 * 4️⃣ 배열.reduce() — 통계 데이터 집계 (totalSteps, completedSteps)
 * 5️⃣ 진행률 계산 — (완료 / 전체) * 100, 0 나누기 방지
 * 6️⃣ map() + key — 과목별 진행 카드 리스트 렌더링
 * 7️⃣ 조건부 뱃지 — 중첩 삼항 연산자로 3가지 상태 표시
 * 8️⃣ Link 컴포넌트 — 과목 상세 페이지로 이동 (/curriculum/{course.id})
 * 9️⃣ 진행률 바 — 동적 width 스타일링
 * 🔟 정적 콘텐츠 — API와 무관한 UI (학습 팁 섹션)
 */
