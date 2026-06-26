/*
 * =============================================================================
 * 📄 curriculum/page.js — 커리큘럼 개요 페이지 (/curriculum)
 * =============================================================================
 *
 * 🎯 이 페이지의 역할:
 *   - Express 백엔드에서 전체 커리큘럼 데이터를 가져와 개요를 표시합니다.
 *   - 전체 진행률 요약(진행률 바), 과목별 카드, 모듈 구성 테이블을 보여줍니다.
 *   - 학습 포인트: 배열.reduce()로 통계 계산, Link 컴포넌트로 페이지 이동,
 *     진행률 시각화, 조건부 테이블 렌더링
 *
 * 🔗 Express API: GET http://localhost:3001/api/curriculum/overview
 *   - 응답 예시: { courses: [{ id, name, totalSteps, completedSteps, ... }], modules: [...] }
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어 — 클라이언트 컴포넌트
 * =============================================================================
 *
 * 이 페이지가 클라이언트 컴포넌트인 이유:
 * - useState로 커리큘럼 데이터 상태 관리
 * - useEffect로 마운트 시 데이터 페칭
 * - (참고) Link 컴포넌트는 서버/클라이언트 모두에서 사용 가능
 *
 * ❓ 만약 서버 컴포넌트로 바꾼다면?
 * - async 컴포넌트로 선언 (export default async function CurriculumPage())
 * - 직접 await fetchCurriculumOverview() 호출
 * - useState/useEffect 제거, 변수에 직접 할당
 * - 장점: 번들 크기 감소, 초기 로드 속도 향상
 * - 단점: 로딩/에러 UI를 컴포넌트 내에서 동적으로 제어하기 어려움
 *   (loading.js, error.js로 대체 가능)
 */
'use client';

import { useState, useEffect } from 'react';

/*
 * =============================================================================
 * 🔗 Link 컴포넌트 (Next.js 내장) — 페이지 이동
 * =============================================================================
 *
 * Link는 Next.js가 제공하는 네비게이션 컴포넌트입니다.
 * - <a> 태그 대신 <Link href="...">를 사용합니다.
 * - 클라이언트 사이드 라우팅: 페이지 전체를 새로고침하지 않고 필요한 부분만 업데이트
 * - 자동 prefetch: 뷰포트에 보이는 Link의 대상 페이지를 미리 로드
 *   (production 빌드에서만 활성화)
 * - 사용법: <Link href="/경로">텍스트 또는 요소</Link>
 *
 * ✅ <a> 태그와의 차이점:
 *   <a href="/students"> → 전체 페이지 새로고침 (느림, UX↓)
 *   <Link href="/students"> → 필요한 컴포넌트만 교체 (빠름, UX↑)
 *
 * ⚠️ Link 컴포넌트 내에서 <a>를 직접 사용하지 마세요.
 *   Link 자체가 <a>로 렌더링됩니다. (style/className은 Link에 직접 적용)
 *   만약 <a>를 중첩하면 중복된 <a> 태그가 생성됩니다.
 */
import Link from 'next/link';

/*
 * 📦 CurriculumCard 컴포넌트 — 개별 과목 카드 UI
 * - props로 course 객체를 받아 진행률과 함께 표시
 * - 내부에 Link를 포함하여 과목 상세 페이지로 이동
 */
import CurriculumCard from '@/components/CurriculumCard';

/*
 * 📦 API 함수 import
 *
 * fetchCurriculumOverview() - 커리큘럼 전체 데이터 조회
 *   - GET http://localhost:3001/api/curriculum/overview
 *   - 응답: { courses: [...], modules: [...], ... }
 */
import { fetchCurriculumOverview } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ CurriculumPage 컴포넌트
 * =============================================================================
 */
export default function CurriculumPage() {
  /*
   * =============================================================================
   * 📊 State 선언
   * =============================================================================
   *
   * curriculum: API 응답 전체를 저장하는 객체 (초기값: null)
   *   - { courses: [...], modules: [...] } 형태
   *   - null로 시작 → 조건부 렌더링(curriculum?.courses)으로 안전 접근
   *
   * loading: 로딩 상태 (초기값: true)
   * error: 에러 메시지 (초기값: null)
   */
  const [curriculum, setCurriculum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /*
   * =============================================================================
   * 🔄 useEffect — 데이터 로딩
   * =============================================================================
   *
   * fetchCurriculumOverview()를 호출하여 전체 커리큘럼 데이터를 받아옵니다.
   * API 응답 구조에 따라 courses와 modules 등의 데이터를 활용합니다.
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchCurriculumOverview();  // Express API 호출
        setCurriculum(data);                             // 데이터 저장
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
   * 🌀 조건부 렌더링 — 로딩 & 에러
   * =============================================================================
   */
  if (loading) {
    return <div className="loading">커리큘럼을 불러오는 중...</div>;
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
   * 📊 배열.reduce()로 전체 통계 계산
   * =============================================================================
   *
   * reduce() 메서드는 배열의 모든 요소를 순회하며 단일 값으로 누적합니다.
   *
   * 구문: array.reduce((accumulator, currentValue) => { ... }, initialValue)
   *
   * - accumulator(누적값): 이전 콜백의 반환값 (첫 호출 시 initialValue)
   * - currentValue(현재값): 배열의 현재 요소
   * - initialValue(초기값): 0 (숫자 누적이므로)
   *
   * 예: [1, 2, 3].reduce((sum, n) => sum + n, 0) → 6
   *
   * 여기서는 두 번의 reduce()로 각각 totalSteps와 completedSteps를 계산합니다.
   *
   * 옵셔널 체이닝(curriculum?.courses):
   * - curriculum이 null/undefined면 undefined 반환 (에러 방지)
   * - curriculum이 있으면 courses 속성 접근
   * - || []로 undefined인 경우 빈 배열로 대체 → reduce() 호출 안전
   */
  const courses = curriculum?.courses || [];
  const totalSteps = courses.reduce((sum, c) => sum + (c.totalSteps || 0), 0);
  const completedSteps = courses.reduce((sum, c) => sum + (c.completedSteps || 0), 0);

  /*
   * 전체 진행률 계산:
   * - totalSteps가 0보다 크면 (completedSteps / totalSteps) * 100
   * - totalSteps가 0이면 0 (0으로 나누기 방지)
   * - Math.round(): 소수점 반올림하여 정수로 표시
   */
  const overallProgress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  /*
   * =============================================================================
   * ✅ 메인 렌더링
   * =============================================================================
   */
  return (
    <div>
       
      <div>
        <h1 className="page-title">커리큘럼 가이드</h1>
        <p className="page-subtitle">코드 교육 랩의 전체 과목과 학습 현황을 확인하세요</p>
      </div>

       
      <div className="curriculum-overview">
        <div className="stat-card" style={{ marginBottom: '2rem' }}>
          <div className="stat-card-label">전체 학습 진행률</div>
          <div className="stat-card-value">{overallProgress}%</div>
           
          <div className="progress-bar-container" style={{ marginTop: '0.75rem' }}>
            <div className="progress-bar-bg">
              <div
                className="progress-bar-fill"
                style={{ width: `${overallProgress}%` }}
              />
            </div>
          </div>
          <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {completedSteps}/{totalSteps} 스텝 완료 ({courses.length}개 과목)
          </div>
        </div>
      </div>

       
      <div className="card-grid">
        {courses.length > 0 ? (
          courses.map((course, i) => (
            <CurriculumCard key={course.id || i} course={course} />
          ))
        ) : (
          <div style={{ color: '#64748b', padding: '2rem', textAlign: 'center' }}>
            등록된 과목이 없습니다. API 서버의 데이터를 확인해주세요.
          </div>
        )}
      </div>

       
      {curriculum?.modules && curriculum.modules.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h2 className="chart-title">모듈 구성</h2>
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>모듈명</th>
                  <th>과목</th>
                  <th>스텝 수</th>
                </tr>
              </thead>
              <tbody>
                {curriculum.modules.map((module, i) => (
                  <tr key={module.id || i}>
                    <td>{module.name || module.title || '-'}</td>
                     
                    <td>{module.courseName || '-'}</td>
                    <td>{module.stepCount || 0}개</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

/*
 * =============================================================================
 * 📌 이 페이지에서 배운 핵심 개념
 * =============================================================================
 *
 * 1️⃣ 'use client' — 클라이언트 컴포넌트의 역할
 * 2️⃣ useState/useEffect — 데이터 페칭 패턴
 * 3️⃣ async/await + try-catch — 비동기 에러 처리
 * 4️⃣ Link 컴포넌트 — 클라이언트 사이드 네비게이션 (Next.js 특징)
 * 5️⃣ 배열.reduce() — 통계 계산 (totalSteps, completedSteps 누적)
 * 6️⃣ 진행률 바 — 동적 width 스타일링 (% 값)
 * 7️⃣ 옵셔널 체이닝(?. ) — curriculum?.courses 안전 접근
 * 8️⃣ && 단락 평가 — 모듈 테이블 조건부 렌더링
 * 9️⃣ map() + key — 카드와 테이블 리스트 렌더링
 * 🔟 동적 라우트 경로 — /curriculum/{course.id} Link 구성
 */
