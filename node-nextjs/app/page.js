/*
 * =============================================================================
 * 📄 page.js — 메인 대시보드 페이지 (/ 경로)
 * =============================================================================
 *
 * 🎯 이 페이지의 역할:
 *   - Express 백엔드(port 3001)에서 데이터를 가져와 KPI 카드, 차트, 최근 제출
 *     목록을 한 화면에 표시하는 메인 대시보드입니다.
 *   - 학습 포인트: 클라이언트 컴포넌트, 상태 관리, 비동기 데이터 페칭,
 *     조건부 렌더링, 리스트 렌더링을 모두 경험할 수 있는 종합 예제입니다.
 */

/*
 * =============================================================================
 * 🔵 'use client' 지시어 — 서버 컴포넌트 vs 클라이언트 컴포넌트
 * =============================================================================
 *
 * 이 줄은 파일 최상단에 위치해야 합니다!
 *
 * ✅ 'use client'가 하는 일:
 *   - 이 컴포넌트는 **클라이언트 컴포넌트(Client Component)**로 동작합니다.
 *   - 즉, 브라우저에서 JavaScript가 실행되며, 사용자 인터랙션(onClick, onChange),
 *     React 훅(useState, useEffect), 브라우저 API 등을 사용할 수 있습니다.
 *
 * ❌ 'use client'가 없으면 (서버 컴포넌트, Server Component):
 *   - 서버에서만 렌더링되어 HTML로 변환됩니다.
 *   - useState, useEffect, onClick 등 브라우저 기능을 사용할 수 없습니다.
 *   - 대신 초기 로딩이 빠르고, 번들 크기가 작아집니다.
 *
 * 🎯 선택 기준:
 *   - 데이터 페칭 + 사용자 인터랙션 필요 → 'use client' (이 파일처럼)
 *   - 정적인 내용만 표시, SEO 중요 → 서버 컴포넌트 (layout.js처럼)
 *   - 가능하면 서버 컴포넌트를 먼저 고려하고, 필요할 때만 'use client' 사용
 */
'use client';

/*
 * =============================================================================
 * 📦 useState와 useEffect 훅 import (React Hooks)
 * =============================================================================
 *
 * React Hooks는 함수형 컴포넌트에서 상태 관리와 생명주기 기능을 사용할 수
 * 있게 해주는 함수들입니다. (클래스 컴포넌트의 this.state, lifecycle methods 대체)
 *
 * 🔹 useState(초기값):
 *   - [값(상태), setter 함수]를 배열로 반환합니다.
 *   - 상태가 변경되면 컴포넌트가 자동으로 다시 렌더링(re-render)됩니다.
 *   - 예: const [count, setCount] = useState(0);
 *
 * 🔹 useEffect(함수, 의존성배열):
 *   - 컴포넌트가 렌더링될 때 부수 효과(side effect)를 실행합니다.
 *   - 데이터 페칭(fetch), DOM 조작, 타이머 설정 등에 사용됩니다.
 *   - 의존성 배열 []: 컴포넌트 마운트 시에만 실행 (최초 1회)
 *   - 의존성 배열 [courseId]: courseId가 변경될 때마다 재실행
 *   - 의존성 배열 생략: 매 렌더링마다 실행 (거의 사용 안 함)
 *   - cleanup 함수(return 함수): 컴포넌트 언마운트 시 실행 (메모리 누수 방지)
 */
import { useState, useEffect } from 'react';

/*
 * 📦 커스텀 컴포넌트 import
 *
 * - StatCard: KPI 카드 (학생 수, 과목 수 등의 지표를 표시하는 카드 UI)
 * - Chart: Chart.js 기반 차트 컴포넌트 (막대 그래프, 선 그래프 등)
 *
 * 이 컴포넌트들은 'components/' 디렉토리에 별도 파일로 정의되어 있습니다.
 * - 컴포넌트를 분리하면: 재사용성 ↑, 코드 가독성 ↑, 유지보수 ↑
 * - 각 컴포넌트는 자신의 UI와 스타일을 캡슐화합니다.
 */
import StatCard from '@/components/StatCard';
import Chart from '@/components/Chart';

/*
 * 📦 API 함수 import
 *
 * @/lib/api 파일에 정의된 데이터 페칭 함수들을 가져옵니다.
 * - API 함수는 fetch() 호출과 응답 처리를 추상화(캡슐화)합니다.
 * - 이렇게 분리하면: URL 변경 시 한 곳만 수정, 에러 처리 일관성, 테스트 용이
 *
 * 실제 fetch() 호출 예시 (api.js 내부):
 *   export async function fetchDashboardStats() {
 *     const res = await fetch('http://localhost:3001/api/stats');
 *     if (!res.ok) throw new Error('API 오류: ' + res.status);
 *     return res.json();  // JSON 응답을 JavaScript 객체로 변환
 *   }
 */
import { fetchDashboardStats, fetchCourseChartData, fetchRecentSubmissions } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ DashboardPage — 메인 대시보드 컴포넌트
 * =============================================================================
 *
 * 컴포넌트는 함수로 정의합니다. 함수명은 항상 대문자로 시작해야 합니다
 * (React가 HTML 태그와 구분하기 위한 규칙).
 *
 * 페이지 컴포넌트는 'export default function'으로 내보냅니다.
 * - export default: 이 파일에서 하나의 함수만 기본으로 내보낼 때 사용
 * - 명명된 export: export function 함수명() { ... } → { 함수명 }으로 import
 */
export default function DashboardPage() {
  /*
   * =============================================================================
   * 📊 useState — 상태(State) 선언
   * =============================================================================
   *
   * 각 상태가 하는 역할을 설명합니다:
   *
   * 1. stats (대시보드 통계): KPI 카드에 표시할 데이터
   *    - 초기값 null → 데이터 로딩 전에는 아직 값이 없음을 의미
   *    - API 응답: { totalStudents, totalCourses, totalSubmissions, averageScore }
   *
   * 2. chartData (차트 데이터): 과목별 통계 차트에 표시할 데이터
   *    - 초기값 null → 조건부 렌더링에 사용 (chartData && <Chart />)
   *
   * 3. recentSubmissions (최근 제출 목록): 테이블에 표시할 데이터
   *    - 초기값 [] (빈 배열) → map()으로 리스트 렌더링 가능
   *    - null이 아닌 빈 배열을 초기값으로 쓰면 map() 에러 방지
   *
   * 4. loading (로딩 상태): 데이터를 불러오는 중인지 표시
   *    - 초기값 true → 컴포넌트 마운트 시 바로 로딩 UI 표시
   *
   * 5. error (에러 상태): 데이터 페칭 실패 시 에러 메시지 저장
   *    - 초기값 null → 에러가 없음을 의미
   *    - 에러 발생 시 문자열이 저장되고, 조건부 렌더링으로 에러 UI 표시
   */
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /*
   * =============================================================================
   * 🔄 useEffect — 데이터 페칭 (Side Effect)
   * =============================================================================
   *
   * useEffect의 첫 번째 인자: 실행할 함수
   * useEffect의 두 번째 인자: 의존성 배열 (dependencies)
   *
   * 의존성 배열이 [] (빈 배열)이므로:
   * - 이 컴포넌트가 화면에 마운트(mount)될 때 한 번만 실행됩니다.
   * - 이후에는 재실행되지 않습니다 (리렌더링 시에도 무시).
   *
   * 만약 의존성 배열이 있다면 (예: [courseId]):
   * - courseId 값이 변경될 때마다 이전 실행 결과를 정리(cleanup)하고 재실행합니다.
   *
   * 생명주기 비유:
   * - useEffect(() => { ... }, [])  → componentDidMount (마운트)
   * - useEffect(() => { ... }, [dep]) → componentDidUpdate (업데이트)
   * - useEffect(() => { return cleanup }, []) → componentWillUnmount (언마운트)
   */
  useEffect(() => {
    /*
     * =============================================================================
     * ⚡ async/await — 비동기 처리 흐름
     * =============================================================================
     *
     * async 키워드: 함수가 비동기 함수임을 선언합니다.
     *   - async 함수는 항상 Promise를 반환합니다.
     *
     * await 키워드: Promise가 해결(resolve)될 때까지 기다립니다.
     *   - await는 async 함수 내부에서만 사용할 수 있습니다.
     *   - await가 있으면 코드가 동기식처럼 순차적으로 실행됩니다.
     *
     * 비유: 카페에서 커피를 주문할 때
     * - 동기(sync): 줄 서서 커피가 나올 때까지 기다림 (블로킹)
     * - 비동기(async): 번호표 받고 자리 앉아서 커피 완료 알림 기다림 (논블로킹)
     * - await: 번호표 받고 "커피 나올 때까지 여기서 기다릴게요" (코드 흐름은 대기)
     *
     * Promise 체인 (.then().catch())보다 async/await이 더 읽기 쉽습니다.
     */
    const loadData = async () => {
      /*
       * 🔐 try-catch-finally — 에러 처리
       *
       * try 블록: 데이터를 가져오는 로직을 실행합니다.
       *   - 성공하면 try 블록이 정상 종료됩니다.
       *   - 실패하면 즉시 catch 블록으로 이동합니다.
       *
       * catch (err) 블록: try 블록에서 예외(Error)가 발생하면 실행됩니다.
       *   - err.message에는 에러 설명 문자열이 들어 있습니다.
       *   - 네트워크 오류, 404/500 응답, JSON 파싱 실패 등이 여기서 잡힙니다.
       *
       * finally 블록: 성공/실패 여부와 관계없이 항상 실행됩니다.
       *   - 주로 정리(cleanup) 작업에 사용됩니다.
       *   - 여기서는 setLoading(false)로 로딩 상태를 해제합니다.
       */
      try {
        /*
         * 로딩 상태를 true로 변경 → 로딩 스피너 UI가 표시됩니다.
         * 이미 true일 수 있지만, 재호출 상황을 대비해 명시적으로 설정합니다.
         */
        setLoading(true);

        /*
         * =============================================================================
         * 📡 Promise.all — 병렬 API 요청
         * =============================================================================
         *
         * Promise.all([promise1, promise2, promise3]):
         * - 여러 Promise를 배열로 받아, 모두 완료될 때까지 기다립니다.
         * - 세 가지 API 요청을 동시에(병렬로) 보냅니다.
         * - 순차적으로 보내는 것보다 3배 빠릅니다!
         *
         * 구조 분해 할당(destructuring)으로 결과를 각 변수에 할당:
         *   결과 배열의 순서 = Promise.all에 전달한 배열의 순서
         *   [0] statsData ← fetchDashboardStats()의 결과
         *   [1] chart     ← fetchCourseChartData()의 결과
         *   [2] submissions ← fetchRecentSubmissions()의 결과
         *
         * 각 fetch 함수는 내부적으로 다음과 같이 동작합니다:
         *   const response = await fetch('http://localhost:3001/api/stats');
         *   if (!response.ok) throw new Error(...);
         *   return response.json();
         *
         * fetch() 설명:
         * - fetch(url) → HTTP GET 요청을 보냅니다.
         * - fetch(url, { method: 'POST', body: JSON.stringify(data) }) → POST 요청
         * - response.ok: HTTP 상태 코드가 200-299 범위인지 확인 (true/false)
         * - response.json(): 응답 본문을 JSON에서 JavaScript 객체로 변환 (Promise 반환)
         * - Express 서버는 http://localhost:3001에서 실행 중이어야 합니다.
         */
        const [statsData, chart, submissions] = await Promise.all([
          fetchDashboardStats(),       // GET http://localhost:3001/api/stats
          fetchCourseChartData(),      // GET http://localhost:3001/api/chart
          fetchRecentSubmissions(),    // GET http://localhost:3001/api/submissions/recent
        ]);

        /*
         * setStats(statsData): 가져온 데이터를 stats 상태에 저장합니다.
         * 상태가 업데이트되면 → 컴포넌트가 자동으로 다시 렌더링(re-render)됩니다.
         * → stats가 null에서 실제 데이터로 변경됨
         * → 조건부 렌더링에서 stats?.totalStudents 등의 값이 표시됨
         *
         * setter 함수 특징:
         * - 상태를 직접 변경하지 않고(mutation), 새 값으로 교체합니다 (immutable).
         * - 상태 변경은 비동기적으로 처리됩니다 (배치 업데이트, batch update).
         */
        setStats(statsData);
        setChartData(chart);
        setRecentSubmissions(submissions);
      } catch (err) {
        /*
         * ❌ 에러 발생 시 처리:
         * - err.message에 담긴 에러 문자열을 error 상태에 저장합니다.
         * - error 상태가 변경되면 조건부 렌더링(if (error))이 실행되어
         *   에러 메시지 UI가 화면에 표시됩니다.
         * - 예시 에러 메시지: "Failed to fetch" (서버가 실행 중이지 않을 때)
         */
        setError(err.message);
      } finally {
        /*
         * ✅ finally: 항상 실행됨
         *
         * 로딩 상태를 false로 변경합니다.
         * - 성공했든 실패했든 로딩 UI는 더 이상 표시되지 않습니다.
         * - setLoading(false)가 없으면 로딩 스피너가 계속 표시됩니다!
         * - 이 finally 블록이 없다면, 에러 발생 시에도 loading이 true로 남아
         *   사용자는 영원히 로딩 화면만 보게 됩니다. (👉 반드시 처리!)
         */
        setLoading(false);
      }
    };

    /*
     * loadData() 함수를 호출해야 실제로 실행됩니다.
     * useEffect 내부에서 async 함수를 직접 사용할 수 없으므로,
     * async 함수를 먼저 정의하고 호출하는 패턴을 사용합니다.
     *
     * 참고: useEffect(async () => { ... }, []) 형태는 React에서 허용되지 않습니다.
     * (useEffect의 콜백은 반드시 동기 함수여야 하며, cleanup 함수를 반환할 수 있어야 함)
     */
    loadData();

    /*
     * 의존성 배열이 []이므로 이 useEffect는 컴포넌트 마운트 시 1회만 실행됩니다.
     * ESLint는 여기에 'react-hooks/exhaustive-deps' 경고를 줄 수 있지만,
     * 의도적으로 []를 사용했습니다 (최초 1회만 로드).
     */
  }, []);

  /*
   * =============================================================================
   * 🌀 조건부 렌더링 1: 로딩 상태 (isLoading 패턴)
   * =============================================================================
   *
   * if (loading) { return ... }
   *
   * React 컴포넌트는 조건에 따라 다른 JSX를 반환할 수 있습니다.
   * JavaScript 함수이므로 if-else, 삼항 연산자, && 등을 자유롭게 사용합니다.
   *
   * isLoading 패턴은 가장 기본적인 UX 패턴입니다:
   * 1. 데이터 로딩 중 → "로딩 중..." 메시지 또는 스피너 표시
   * 2. 데이터 로딩 완료 → 실제 콘텐츠 표시
   * 3. 에러 발생 → 에러 메시지 표시 (다음 조건에서 처리)
   *
   * 이렇게 early return(조건에 맞으면 일찍 반환)하면
   * 메인 return문이 깔끔해지고 조건이 분리되어 가독성이 좋아집니다.
   */
  if (loading) {
    return (
      <div className="loading">
         
        <p>데이터를 불러오는 중...</p>
      </div>
    );
  }

  /*
   * =============================================================================
   * 🚨 조건부 렌더링 2: 에러 상태
   * =============================================================================
   *
   * if (error) { return ... }
   *
   * 로딩이 false이고 에러가 있으면 → 에러 UI 표시
   * 로딩과 에러 처리를 분리하면 사용자에게 명확한 피드백을 줄 수 있습니다.
   *
   * 에러 메시지에는:
   * - 구체적인 에러 내용 (err.message)
   * - 해결 방법 안내 (서버 실행 확인 메시지)
   * - 작은 글씨(small 태그)로 부가 설명 추가
   */
  if (error) {
    return (
      <div className="error-message">
        API 서버에 연결할 수 없습니다: {error}
        <br />
        <small>Express 서버가 http://localhost:3001에서 실행 중인지 확인해주세요.</small>
      </div>
    );
  }

  /*
   * =============================================================================
   * ✅ 메인 렌더링 — 데이터 로딩 완료, 에러 없음
   * =============================================================================
   *
   * 여기까지 도달했다면:
   * - loading === false (로딩 완료)
   * - error === null (에러 없음)
   * - stats, chartData, recentSubmissions에 데이터가 저장됨
   *
   * 이제 실제 대시보드 UI를 JSX로 렌더링합니다.
   */
  return (
    <div>
       

       
      <div>
        <h1 className="page-title">대시보드</h1>
        <p className="page-subtitle">코드 교육 랩의 전체 현황을 한눈에 확인하세요</p>
      </div>

       
      <div className="stats-grid">
        <StatCard
          label="전체 학생 수"
          value={stats?.totalStudents ?? '—'}
          change="이번 주 +5"
          changeType="positive"
        />
        <StatCard
          label="등록 과목 수"
          value={stats?.totalCourses ?? '—'}
          change="이번 주 +2"
          changeType="positive"
        />
        <StatCard
          label="누적 제출"
          value={stats?.totalSubmissions ?? '—'}
          change="오늘 12건"
          changeType="positive"
        />
        <StatCard
          label="평균 정답률"
          value={stats?.averageScore ? `${stats.averageScore}%` : '—'}
          /*
           * 템플릿 리터럴 (`${}`):
           * - JavaScript에서 문자열과 변수를 결합하는 현대적인 방식
           * - 이전 방식: '평균: ' + stats.averageScore + '%'
           * - 템플릿 리터럴: `평균: ${stats.averageScore}%`
           */
          change="-2.3%"
          changeType="negative"
        />
      </div>

       
      {chartData && (
        <Chart
          type="bar"
          title="과목별 통계"
          data={{
            /*
             * chartData 객체의 구조:
             * { courses: ['JS', 'Python', ...], studentCounts: [30, 25, ...], averageScores: [85, 72, ...] }
             * || []를 사용하여 courses가 undefined일 때 빈 배열로 대체 (에러 방지)
             */
            labels: chartData.courses || [],
            datasets: [
              {
                label: '학생 수',
                data: chartData.studentCounts || [],
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: '#3b82f6',
                borderWidth: 1,
              },
              {
                label: '평균 점수',
                data: chartData.averageScores || [],
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: '#8b5cf6',
                borderWidth: 1,
              },
            ],
          }}
        />
      )}

       
      <div className="table-wrapper">
        <h3 className="chart-title">최근 제출 현황</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>학생</th>
              <th>과목</th>
              <th style={{ width: '100px' }}>점수</th>
              <th style={{ width: '100px' }}>상태</th>
            </tr>
          </thead>
          <tbody>
             
            {recentSubmissions && recentSubmissions.length > 0
              ? recentSubmissions.map((sub, i) => (
                  <tr key={sub.id || i}>
                     
                    <td>{sub.studentName || '-'}</td>
                    <td>{sub.courseName || '-'}</td>
                    <td>
                      {sub.score ?? '-'}
                      {typeof sub.score === 'number' ? '점' : ''}
                       
                    </td>
                    <td>
                       
                      <span className={`badge ${sub.status === 'pass' ? 'badge-success' : 'badge-danger'}`}>
                        {sub.status === 'pass' ? '통과' : '실패'}
                      </span>
                    </td>
                  </tr>
                ))
              : (
                <tr>
                   
                  <td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>
                    제출 내역이 없습니다
                  </td>
                </tr>
              )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/*
 * =============================================================================
 * 📌 학습 요약
 * =============================================================================
 *
 * 이 페이지에서 배운 핵심 개념들:
 *
 * 1️⃣ 'use client' — 클라이언트 컴포넌트 선언 (서버 vs 클라이언트 차이)
 * 2️⃣ useState — 상태 관리 (stats, loading, error 등 5개 상태)
 * 3️⃣ useEffect — 생명주기 (마운트 시 데이터 페칭)
 * 4️⃣ async/await — 비동기 프로그래밍 (Promise + try-catch)
 * 5️⃣ fetch() — Express API 호출 (http://localhost:3001)
 * 6️⃣ Promise.all — 병렬 요청 (3개 API를 동시에 호출)
 * 7️⃣ 조건부 렌더링:
 *    - if (loading) — 로딩 UI
 *    - if (error) — 에러 UI
 *    - {chartData && <Chart />} — 데이터 존재 시 표시
 *    - {조건 ? map() : <빈화면>} — 데이터 유무에 따른 분기
 * 8️⃣ map() + key — 리스트 렌더링
 * 9️⃣ 옵셔널 체이닝(?.) + null 병합(??) — 안전한 속성 접근
 * 🔟 JSX 표현식 {} 사용법
 */
