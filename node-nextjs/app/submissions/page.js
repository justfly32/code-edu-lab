/*
 * =============================================================================
 * 📄 submissions/page.js — 제출물 목록 페이지 (/submissions)
 * =============================================================================
 *
 * 🎯 이 페이지의 역할:
 *   - Express 백엔드에서 학생들의 코드 제출 목록을 가져와 카드 형태로 표시합니다.
 *   - 각 제출 카드에는 학생명, 과목명, 점수, 상태(통과/실패/대기중), 제출 코드,
 *     언어, 제출일 등의 정보가 표시됩니다.
 *   - 학습 포인트: 다양한 상태값 처리 함수(getStatusBadge), 코드 미리보기(pre 태그),
 *     다양한 조건부 렌더링, 날짜 포맷팅, 복잡한 객체 데이터 표시
 *
 * 🔗 Express API: GET http://localhost:3001/api/submissions
 *   - 응답 예시:
 *     [{ id: 1, studentName: '홍길동', courseName: 'JavaScript', score: 85,
 *        status: 'pass', code: 'console.log("hello")', language: 'javascript',
 *        submittedAt: '2024-03-15T10:30:00Z' }]
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어
 * =============================================================================
 *
 * 이 페이지의 'use client' 의존도:
 *
 * 1️⃣ useState — submissions 배열, loading, error 상태 관리
 * 2️⃣ useEffect — API 데이터 페칭
 * 3️⃣ getStatusBadge 함수 — 다양한 상태값(200, 'pass', 'pending' 등)을
 *    받아서 적절한 뱃지 UI로 변환
 *    (순수 JavaScript 함수이지만, JSX를 반환하므로 클라이언트에서 사용)
 *
 * ❌ 만약 이 페이지를 서버 컴포넌트로 바꾼다면:
 * - getStatusBadge 함수는 그대로 사용 가능 (JSX 반환 함수)
 * - 하지만 useState/useEffect 대신 async 컴포넌트로 변경
 * - 데이터는 props로 직접 받거나, 컴포넌트 내에서 await fetch()로 직접 조회
 * - 장점: 초기 HTML에 모든 데이터가 포함되어 검색 엔진이 내용을 인식할 수 있음
 *
 * "클라이언트 컴포넌트는 사용자와 상호작용이 필요한 페이지만 사용하라"
 * - 여기서는 학습 목적으로 클라이언트 컴포넌트 패턴을 사용합니다.
 */
'use client';

import { useState, useEffect } from 'react';

/*
 * 📦 API 함수 import
 *
 * fetchSubmissions():
 * - GET http://localhost:3001/api/submissions
 * - 모든 제출물 목록을 JSON 배열로 반환
 *
 * Express 서버의 /api/submissions 엔드포인트:
 * - 데이터베이스에서 submissions 테이블을 조회
 * - JOIN으로 학생 이름, 과목명 등 포함
 * - 최신순으로 정렬 (보통 submittedAt DESC)
 */
import { fetchSubmissions } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ SubmissionsPage 컴포넌트
 * =============================================================================
 */
export default function SubmissionsPage() {
  /*
   * =============================================================================
   * 📊 State 선언
   * =============================================================================
   *
   * submissions: 제출물 배열 (초기값: [])
   *   - 각 제출물 객체: { id, studentName, courseName, score, status, code, language, submittedAt }
   *   - 빈 배열 초기화: map() 호출 안전, "제출 내역이 없습니다" 처리 가능
   *
   * loading: 로딩 상태 (초기값: true)
   * error: 에러 메시지 (초기값: null)
   */
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /*
   * =============================================================================
   * 🔄 useEffect — 데이터 로딩
   * =============================================================================
   *
   * fetchSubmissions() → Express API 호출
   * → 응답 데이터를 submissions 상태에 저장
   * → 컴포넌트 리렌더링 → 제출물 카드 표시
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchSubmissions();  // Express API 호출
        setSubmissions(data);
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
   * 🏷️ 상태별 뱃지 함수 — 다양한 API 응답 처리
   * =============================================================================
   *
   * 이 함수는 제출 상태(status)의 다양한 표현을 통일된 뱃지로 변환합니다.
   *
   * API마다 status 값이 다를 수 있으므로 (200 vs 'pass' vs 'success'),
   * 여러 값을 포괄적으로 처리하는 함수를 만듭니다.
   *
   * ✅ JavaScript 배열.includes():
   * - 배열에 특정 값이 포함되어 있는지 확인
   * - [200, '200', 'pass', 'success', 'accepted'].includes(status)
   * - status가 위 목록 중 하나와 일치하면 true 반환
   * - OR(||) 연산자를 여러 번 쓰는 것보다 간결함
   *
   * ✅ 함수형 컴포넌트 외부에 함수를 정의하는 이유:
   * - 이 함수는 상태나 props에 의존하지 않으므로 컴포넌트 외부에 정의
   * - 컴포넌트가 리렌더링될 때마다 새로 생성되지 않음 (성능 최적화)
   * - 순수 함수: 같은 입력에 항상 같은 출력 반환
   *
   * 참고: JSX를 반환하는 함수이므로 .tsx/.jsx 파일에서만 사용 가능
   */
  function getStatusBadge(status) {
    /*
     * 각 조건을 배열.includes()로 확인:
     *
     * status 값의 예시:
     * - 통과(pass): 200 (숫자), '200' (문자열), 'pass', 'success', 'accepted'
     * - 실패(fail): 400 (숫자), '400', 'fail', 'failed', 'rejected', 'wrong'
     * - 대기중: 'pending'
     * - 그 외: status 값을 그대로 표시 (또는 '알 수 없음')
     *
     * 이렇게 다양한 값을 처리하는 이유:
     * - Express API의 구현이 변경될 수 있음
     * - 여러 소스(DB, 외부 API)에서 데이터를 받을 수 있음
     * - 프론트엔드에서 방어적으로 코딩 (Defensive Programming)
     */
    if ([200, '200', 'pass', 'success', 'accepted'].includes(status)) {
      return <span className="badge badge-success">통과</span>;
    }
    if ([400, '400', 'fail', 'failed', 'rejected', 'wrong'].includes(status)) {
      return <span className="badge badge-danger">실패</span>;
    }
    if (status === 'pending') {
      return <span className="badge badge-warning">대기중</span>;
    }
    return <span className="badge badge-info">{status || '알 수 없음'}</span>;
  }

  /*
   * =============================================================================
   * 🌀 조건부 렌더링 (Early Return)
   * =============================================================================
   */
  if (loading) return <div className="loading">제출 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">오류: {error}</div>;

  /*
   * =============================================================================
   * ✅ 메인 렌더링 — 제출물 카드 목록
   * =============================================================================
   */
  return (
    <div>
      <div>
        <h1 className="page-title">제출 현황</h1>
        <p className="page-subtitle">학생들의 코드 제출 및 채점 결과입니다</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {submissions.length > 0 ? (
          submissions.map((sub, i) => (
            <div
              key={sub.id || i}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: '0.75rem',
                padding: '1.5rem',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '1rem',
                }}
              >
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>
                    {sub.studentName || '알 수 없음'}
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginLeft: '0.5rem' }}>
                      {sub.studentId || ''}
                    </span>
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    {sub.courseName || sub.assignmentName || '-'}
                  </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  {sub.score !== undefined && (
                    <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>
                      {sub.score}점
                    </span>
                  )}
                  {getStatusBadge(sub.status)}
                </div>
              </div>
              {sub.code && (
                <div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    제출 코드:
                  </p>
                  <pre className="code-block">{sub.code}</pre>
                </div>
              )}
              <div
                style={{
                  marginTop: '0.75rem',
                  display: 'flex',
                  gap: '1rem',
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                }}
              >
                {sub.language && <span>언어: {sub.language}</span>}
                {sub.submittedAt && (
                  <span>
                    제출일: {new Date(sub.submittedAt).toLocaleString('ko-KR')}
                  </span>
                )}
              </div>
            </div>
          ))
        ) : (
          <div style={{ color: '#64748b', padding: '3rem', textAlign: 'center' }}>
            제출 내역이 없습니다
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
 * 1️⃣ 'use client' — 클라이언트 컴포넌트의 필요성과 서버 컴포넌트 전환 고려
 * 2️⃣ useState/useEffect — 데이터 페칭 기본 패턴
 * 3️⃣ async/await — 비동기 API 호출
 * 4️⃣ try-catch-finally — 완전한 에러 처리 (로딩 해제 보장)
 * 5️⃣ 배열.includes() — 여러 값 조건 비교 (방어적 코딩)
 * 6️⃣ 조건부 렌더링:
 *    - if (loading) / if (error) — Early Return
 *    - {sub.code && <pre>} — 코드가 있을 때만 표시
 *    - {sub.score !== undefined && ...} — 점수가 있을 때만 표시
 *    - {sub.language && ...} — 언어 정보가 있을 때만 표시
 * 7️⃣ map() + key — 제출물 카드 리스트 렌더링
 * 8️⃣ 함수로 JSX 반환 — getStatusBadge() 패턴 (재사용성)
 * 9️⃣ <pre> 태그 — 코드 블록 표시 (공백/줄바꿈 유지)
 * 🔟 Date.toLocaleString('ko-KR') — 한국 날짜/시간 포맷팅
 *
 * 💡 추가 학습 포인트:
 * - 방어적 프로그래밍: 다양한 API 응답에 대비한 코드
 * - || fallback 체인: 여러 필드명(courseName / assignmentName) 처리
 * - 인라인 스타일로 Flexbox 레이아웃 구성
 * - 함수형 상태 관리: getStatusBadge는 순수 함수
 */
