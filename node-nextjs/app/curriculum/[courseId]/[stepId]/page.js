/*
 * =============================================================================
 * 📄 curriculum/[courseId]/[stepId]/page.js — 개별 스텝 학습 페이지
 * =============================================================================
 *
 * 🧭 파일 경로: app/curriculum/[courseId]/[stepId]/page.js
 *
 * 🔗 실제 URL: /curriculum/javascript-basics/step-1
 *   - courseId = 'javascript-basics'
 *   - stepId = 'step-1'
 *
 * 🎯 이 페이지의 역할:
 *   - 특정 강의(courseId)의 특정 스텝(stepId) 상세 내용을 표시합니다.
 *   - 지시사항, 코드 예제, 예상 출력, 힌트(접기/펼치기), 완료 버튼을 제공합니다.
 *   - 학습 포인트: 중첩 동적 라우트, 복합적인 상태 관리, 사용자 액션 처리
 *     (완료 표시), 이전/다음 스텝 네비게이션, 조건부 UI 분기
 *
 * 🔗 Express API: GET http://localhost:3001/api/courses/:courseId/steps/:stepId
 *   - 응답: { step: { id, title, description, instruction, code, expectedOutput, hints, completed }, allSteps: [...] }
 *   - PUT http://localhost:3001/api/steps/:stepId/complete (markStepComplete)
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어
 * =============================================================================
 *
 * 이 페이지는 가장 많은 클라이언트 기능을 사용합니다:
 *
 * 1️⃣ useState (7개 상태): step, steps, loading, error, hintsOpen,
 *    completing, completed
 * 2️⃣ useEffect: courseId + stepId 변경 시 데이터 로딩
 * 3️⃣ useParams: URL에서 courseId와 stepId 읽기
 * 4️⃣ useRouter: 완료 후 프로그래밍 방식으로 페이지 이동
 * 5️⃣ onClick, onChange: 버튼 클릭, 힌트 토글, 완료 처리
 * 6️⃣ 브라우저 API: navigator.clipboard.writeText() (코드 복사)
 *
 * 이 모든 기능은 서버 컴포넌트에서 사용할 수 없으므로
 * 'use client'가 필수적입니다.
 */
'use client';

import { useState, useEffect } from 'react';

/*
 * =============================================================================
 * 🔗 Link 컴포넌트 — 페이지 내비게이션
 * =============================================================================
 *
 * Link는 <a> 태그를 대체하는 Next.js의 라우팅 컴포넌트입니다.
 *
 * 사용된 위치:
 * 1. 브레드크럼: <Link href="/curriculum">커리큘럼</Link>
 * 2. 브레드크럼: <Link href={`/curriculum/${courseId}`}>{step?.courseName}</Link>
 *
 * ✅ Link의 장점:
 * - 페이지 전체를 새로고침하지 않음 (빠른 전환)
 * - 사전 로드(prefetch): 뷰포트에 보이는 Link의 대상을 미리 다운로드
 * - JSX 내에서 React 컴포넌트처럼 사용 가능
 */
import Link from 'next/link';

/*
 * =============================================================================
 * 📦 useParams & useRouter (next/navigation)
 * =============================================================================
 *
 * 🔹 useParams(): URL 동적 파라미터 객체 반환
 *   - /curriculum/[courseId]/[stepId] → { courseId: '...', stepId: '...' }
 *   - 구조 분해: const { courseId, stepId } = useParams();
 *
 * 🔹 useRouter(): 프로그래밍 방식 라우팅
 *   - router.push('/경로'): 페이지 이동
 *   - router.replace('/경로'): 히스토리 교체 (뒤로 가기 불가)
 *   - router.back(): 이전 페이지로
 *   - router.refresh(): 현재 페이지 새로고침 (서버 컴포넌트 리렌더링)
 *
 * useRouter vs Link:
 * - Link: JSX에서 선언적 사용 (사용자가 클릭하는 UI)
 * - useRouter: JavaScript 코드에서 동적 이동 (완료 후 자동 이동 등)
 *
 * @/next/navigation (App Router) vs @/next/router (Pages Router):
 * - App Router에서는 'next/navigation'을 사용합니다.
 * - 구버전('next/router')은 호환성을 위해 유지되지만 새 프로젝트는 'next/navigation'을 사용하세요.
 */
import { useParams, useRouter } from 'next/navigation';

/*
 * 📦 API 함수 import
 *
 * fetchStepDetail(courseId, stepId):
 *   - GET http://localhost:3001/api/courses/:courseId/steps/:stepId
 *   - 특정 스텝의 상세 데이터 조회
 *
 * markStepComplete(stepId):
 *   - PUT http://localhost:3001/api/steps/:stepId/complete
 *   - 스텝을 완료 상태로 업데이트
 *
 * StepNavigation: 이전/다음 스텝 이동을 위한 커스텀 컴포넌트
 */
import { fetchStepDetail, markStepComplete } from '@/lib/api';
import StepNavigation from '@/components/StepNavigation';

/*
 * =============================================================================
 * 🏗️ StepDetailPage 컴포넌트 — 개별 스텝 학습 페이지
 * =============================================================================
 */
export default function StepDetailPage() {
  /*
   * =============================================================================
   * 📍 URL 동적 파라미터 읽기
   * =============================================================================
   */
  const params = useParams();
  const router = useRouter();
  const { courseId, stepId } = params;
  /*
   * 구조 분해 할당 (Destructuring):
   * - params.courseId와 params.stepId를 각각 변수에 할당
   * - 객체의 속성명과 변수명이 같으면 축약 가능
   * - 위는 const { courseId } = params; const { stepId } = params; 와 동일
   */

  /*
   * =============================================================================
   * 📊 State 선언 (7가지 상태)
   * =============================================================================
   *
   * step: 현재 스텝의 상세 데이터 (객체 또는 null)
   *   - { id, title, description, instruction, code, expectedOutput, hints, completed }
   *   - 초기값: null → 조건부 렌더링으로 안전 접근 (step?.title)
   *
   * steps: 전체 스텝 목록 (이전/다음 네비게이션용)
   *   - 배열: [{ id, title, ... }, ...]
   *   - 초기값: [] → map() 안전
   *
   * loading: 데이터 로딩 상태 (true/false)
   * error: 에러 메시지 (null 또는 문자열)
   *
   * hintsOpen: 힌트 섹션 열림/닫힘 (true/false)
   *   - 힌트는 사용자가 원할 때만 볼 수 있도록 버튼으로 제어
   *
   * completing: 완료 처리 중 상태 (true/false)
   *   - 완료 버튼을 누르면 true → API 호출 중
   *   - API 응답을 기다리는 동안 버튼 비활성화 + "처리 중..." 표시
   *   - 중복 클릭 방지 (debounce 역할)
   *
   * completed: 스텟 완료 여부 (true/false)
   *   - API 응답에서 step.completed 값 저장
   *   - true면 완료 메시지 표시, false면 완료 버튼 표시
   */
  const [step, setStep] = useState(null);
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hintsOpen, setHintsOpen] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);

  /*
   * =============================================================================
   * 🔄 useEffect — 스텝 데이터 로딩 (courseId + stepId 변경 시)
   * =============================================================================
   *
   * 의존성 배열: [courseId, stepId]
   *
   * 의존성 배열에 두 개의 값이 있으므로:
   * - courseId 변경 → 데이터 재로딩 (다른 강의의 스텝)
   * - stepId 변경 → 데이터 재로딩 (같은 강의의 다른 스텝)
   * - 둘 다 변경 → 데이터 재로딩
   *
   * 만약 [courseId, stepId]를 생략하면:
   * - stepId가 변경되어도 이전 스텝 데이터가 계속 표시됨
   * - (버그: 사용자가 다른 스텝으로 이동해도 화면이 바뀌지 않음)
   *
   * useEffect cleanup:
   * - 의존성 배열 값이 변경되면 이전 effect가 정리(cleanup)되고
   * - 새 effect가 실행됩니다.
   * - 여기서는 cleanup 함수가 없지만, 구독(subscription)이나
   *   타이머가 있다면 반드시 cleanup에서 해제해야 합니다 (메모리 누수 방지).
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        /*
         * fetchStepDetail(courseId, stepId):
         * - Express API에 GET 요청을 보냅니다.
         * - 응답 데이터: { step: {...}, allSteps: [...] }
         *
         * setStep(data.step || data):
         * - data.step이 있으면 사용, 없으면 data 자체를 step으로 사용
         * - API 응답 구조의 유연한 대응
         *
         * setSteps(data.allSteps || data.steps || []):
         * - allSteps가 있으면 사용, steps가 있으면 사용, 없으면 빈 배열
         * - 여러 fallback으로 다양한 API 응답 구조에 대응
         */
        const data = await fetchStepDetail(courseId, stepId);
        setStep(data.step || data);
        setSteps(data.allSteps || data.steps || []);
        setCompleted(data.step?.completed || data.completed || false);
        /*
         * completed 상태 초기화:
         * - API 응답에서 스텝의 완료 상태를 읽어와서 설정
         * - 처음에는 data.step?.completed를 확인
         * - 구조가 다르면 data.completed 확인
         * - 둘 다 없으면 false (미완료)
         */
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
        /*
         * 힌트 상태 초기화:
         * - 새 스텝으로 이동할 때마다 힌트는 접힌 상태로 초기화
         * - 사용자 경험: 다른 스텝으로 이동했는데 이전 스텝의 힌트가 펼쳐져 있으면 혼란
         */
        setHintsOpen(false);
      }
    };
    loadData();
  }, [courseId, stepId]);  // ✅ courseId 또는 stepId 변경 시 재실행

  /*
   * =============================================================================
   * ✅ 스텝 완료 처리 함수
   * =============================================================================
   *
   * async/await + try-catch 패턴:
   *
   * 1. setCompleting(true) → 버튼 비활성화 (중복 클릭 방지)
   * 2. await markStepComplete(stepId) → API 호출 (PUT 요청)
   * 3. setCompleted(true) → 화면을 "완료됨" 상태로 전환
   * 4. 에러 발생 시 → alert()으로 사용자에게 알림
   * 5. finally → setCompleting(false) (완료 처리 종료)
   *
   * 이 패턴은 "낙관적 업데이트(Optimistic Update)"의 반대인
   * "보수적 업데이트(Pessimistic Update)"입니다:
   * - API 응답을 기다린 후에 UI를 업데이트
   * - 항상 서버의 최신 상태를 반영
   * - 네트워크 지연 시 사용자가 잠시 기다려야 함
   *
   * 낙관적 업데이트:
   * - API 호출 전에 먼저 UI를 업데이트 (즉시 반응)
   * - API 실패 시 롤백(되돌리기)
   * - 장점: 빠른 UX, 단점: 구현 복잡
   */
  const handleComplete = async () => {
    try {
      setCompleting(true);
      await markStepComplete(stepId);
      /*
       * markStepComplete(stepId):
       * - PUT http://localhost:3001/api/steps/:stepId/complete
       * - 서버에서 해당 스텝을 완료 상태로 변경
       * - await: 응답이 올 때까지 기다림 (비동기)
       */
      setCompleted(true);  // UI 업데이트: 완료 메시지 표시
    } catch (err) {
      /*
       * alert(): 브라우저 기본 알림창
       * - 간단한 에러 알림에는 적합하지만, UX가 좋지 않음
       * - 실제 프로덕션에서는 toast notification 사용 권장
       */
      alert('완료 처리에 실패했습니다: ' + err.message);
    } finally {
      setCompleting(false);  // 버튼 활성화 (에러가 있어도)
    }
  };

  /*
   * =============================================================================
   * 🌀 조건부 렌더링
   * =============================================================================
   */
  if (loading) {
    return <div className="loading">스텝을 불러오는 중...</div>;
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
   * ✅ 메인 렌더링 — 스텝 상세 페이지
   * =============================================================================
   */
  return (
    <div>
       
      <nav style={{ marginBottom: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <Link href="/curriculum" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
          커리큘럼
        </Link>
        {' > '}
        <Link href={`/curriculum/${courseId}`} style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
          {step?.courseName || courseId}
           
        </Link>
        {' > '}
        <span>{step?.title || stepId}</span>
      </nav>

       
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="page-title">{step?.title || '스텝 제목 없음'}</h1>
        {step?.description && (
          <p className="page-subtitle">{step.description}</p>
        )}
      </div>

       
      <div className="step-section" style={{ marginBottom: '1.5rem' }}>
        <h2 className="step-section-title">📋 학습 지시사항</h2>
        <div className="step-instruction">
          {step?.instruction || '지시사항이 없습니다.'}
        </div>
      </div>

       
      {step?.code && (
        <div className="step-section" style={{ marginBottom: '1.5rem' }}>
          <h2 className="step-section-title">💻 코드 예제</h2>
          <div className="code-block-wrapper">
            <div className="code-block-header">
              <span className="code-lang-badge">{step?.language || 'javascript'}</span>
              <button
                className="btn-copy"
                onClick={() => navigator.clipboard?.writeText(step.code)}
                /*
                 * 📋 navigator.clipboard.writeText():
                 * - 브라우저 API로 클립보드에 텍스트 복사
                 * - ?. (옵셔널 체이닝): clipboard API가 없는 브라우저에서 에러 방지
                 * - async/await으로 처리할 수도 있지만, 여기서는 간단히 사용
                 * - 단점: HTTPS에서만 동작, 사용자에게 권한 요청
                 *
                 * 대안: document.execCommand('copy') (구식, but 범용)
                 */
                style={{
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.75rem',
                  backgroundColor: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '0.25rem',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                }}
              >
                복사
              </button>
            </div>
            <pre className="code-block">{step.code}</pre>
          </div>
        </div>
      )}

       
      {step?.expectedOutput && (
        <div className="step-section" style={{ marginBottom: '1.5rem' }}>
          <h2 className="step-section-title">✅ 예상 출력</h2>
          <div className="expected-output">
            <pre>{step.expectedOutput}</pre>
          </div>
        </div>
      )}

       
      {step?.hints && step.hints.length > 0 && (
        <div className="step-section" style={{ marginBottom: '1.5rem' }}>
          <button
            className="hints-toggle"
            onClick={() => setHintsOpen(!hintsOpen)}
            /*
             * onClick={setHintsOpen(!hintsOpen)} → ❌ 즉시 실행 (잘못된 패턴)
             * onClick={() => setHintsOpen(!hintsOpen)} → ✅ 클릭 시 실행 (올바른 패턴)
             *
             * 화살표 함수로 감싸는 이유:
             * - JSX 평가 시 함수가 아닌 함수 호출 결과를 onClick에 전달하게 됨
             * - 화살표 함수로 감싸면 클릭 시에만 실행됨
             */
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1rem',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '0.5rem',
              color: 'var(--accent-warning)',
              cursor: 'pointer',
              fontSize: '0.95rem',
              fontWeight: 600,
              width: '100%',
              textAlign: 'left',
            }}
          >
            <span style={{ fontSize: '1.2rem' }}>💡</span>
            힌트 {hintsOpen ? '숨기기' : '보기'}
            <span style={{ marginLeft: 'auto', fontSize: '0.8rem' }}>
              {hintsOpen ? '▲' : '▼'}
            </span>
          </button>

           
          {hintsOpen && (
            <div className="hints-content" style={{ marginTop: '0.5rem' }}>
              {step.hints.map((hint, i) => (
                <div
                  key={i}
                  /*
                   * ⚠️ key={i} (배열 인덱스):
                   * 힌트 배열은 정적이므로 인덱스를 key로 사용해도 무방
                   * 하지만 항목이 추가/제거/정렬된다면 고유 ID 사용 권장
                   */
                  className="hint-item"
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '0.375rem',
                    marginBottom: '0.5rem',
                    fontSize: '0.9rem',
                    color: 'var(--text-secondary)',
                  }}
                >
                  <strong style={{ color: 'var(--accent-warning)' }}>힌트 {i + 1}:</strong>{' '}
                  {hint}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

       
      <div style={{ margin: '2rem 0' }}>
        {completed ? (
          <div
            style={{
              padding: '1rem',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '0.5rem',
              color: 'var(--accent-success)',
              fontWeight: 600,
              textAlign: 'center',
            }}
          >
            ✓ 이 스텝은 이미 완료되었습니다!
          </div>
        ) : (
          <button
            onClick={handleComplete}
            disabled={completing}
            style={{
              width: '100%',
              padding: '1rem',
              backgroundColor: 'var(--accent-success)',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              fontSize: '1.1rem',
              fontWeight: 700,
              cursor: completing ? 'not-allowed' : 'pointer',
              opacity: completing ? 0.7 : 1,
              transition: 'opacity 0.2s',
            }}
          >
            {completing ? '처리 중...' : '✓ 완료'}
             
          </button>
        )}
      </div>

       
      {steps.length > 0 && (
        <StepNavigation courseId={courseId} steps={steps} currentStepId={stepId} />
      )}
    </div>
  );
}

/*
 * =============================================================================
 * 📌 이 페이지에서 배운 핵심 개념
 * =============================================================================
 *
 * 1️⃣ 중첩 동적 라우트 — [courseId]/[stepId] 두 단계 동적 파라미터
 * 2️⃣ useParams() — 여러 동적 파라미터 읽기 ({ courseId, stepId })
 * 3️⃣ useRouter() — 프로그래밍 방식 라우팅
 * 4️⃣ useState (7개) — 다양한 유형의 상태 관리 (객체, 배열, boolean)
 * 5️⃣ useEffect [courseId, stepId] — 두 값이 변경될 때 데이터 재로딩
 * 6️⃣ async/await 데이터 페칭 + try-catch-finally 에러 처리
 * 7️⃣ 조건부 렌더링 다양하게:
 *    - if (loading) / if (error) — Early Return
 *    - {step?.code && <JSX>} — 데이터 존재 시 표시
 *    - {completed ? <완료> : <버튼>} — 상태에 따른 UI 전환
 * 8️⃣ onClick 핸들러 — 화살표 함수로 감싸는 패턴
 * 9️⃣ disabled 속성 — 중복 클릭 방지 (completing 상태)
 * 🔟 브라우저 API — navigator.clipboard.writeText()로 코드 복사
 *
 * 💡 추가 학습 포인트:
 * - 보수적 업데이트 (Pessimistic): API 응답 후 UI 업데이트
 * - 낙관적 업데이트 (Optimistic): UI 먼저 업데이트 후 API 호출
 * - alert() 대신 Toast Notification 사용
 * - 힌트 토글: 접기/펼치기 UI 패턴
 */
