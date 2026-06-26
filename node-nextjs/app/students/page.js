/*
 * =============================================================================
 * 📄 students/page.js — 학생 목록 페이지 (/students)
 * =============================================================================
 *
 * 🎯 이 페이지의 역할:
 *   - Express 백엔드에서 학생 목록 데이터를 가져와 테이블 형태로 표시합니다.
 *   - 검색 기능을 통해 학생 이름, 이메일, 학번으로 필터링할 수 있습니다.
 *   - 학습 포인트: 검색어에 따른 상태 관리, 배열 필터링 패턴,
 *     테이블 리스트 렌더링, 동적 CSS 클래스 바인딩
 *
 * 🔗 Express API: GET http://localhost:3001/api/students
 *   - 응답 예시: [{ id: 1, studentId: 'S001', name: '홍길동', email: '...', ... }]
 */

/*
 * =============================================================================
 * 🔵 'use client' — 클라이언트 컴포넌트
 * =============================================================================
 *
 * 이 지시어가 필요한 이유:
 * - useState로 검색어(search) 상태를 관리합니다 → 브라우저 상태 필요
 * - useEffect로 API 데이터를 가져옵니다 → 브라우저 fetch 필요
 * - <input>의 onChange 이벤트를 처리합니다 → 브라우저 이벤트 필요
 * - onChange={(e) => setSearch(e.target.value)}:
 *   입력 필드의 값이 변경될 때마다 search 상태를 업데이트합니다.
 *
 * 서버 컴포넌트로는 위 세 가지를 할 수 없으므로 'use client'가 필수입니다.
 *
 * ✅ 결정 기준:
 *   "사용자의 입력을 받거나, 브라우저 API를 사용하거나, useState가 필요하면
 *    무조건 'use client'를 붙이세요."
 */
'use client';

/*
 * =============================================================================
 * 📦 React Hooks import
 * =============================================================================
 *
 * useState: 상태 관리 훅
 * - const [search, setSearch] = useState('');  // 검색어 상태
 * - search가 변경될 때마다 컴포넌트가 다시 렌더링됩니다.
 * - 렌더링 시 filteredStudents가 다시 계산되어 검색 결과가 업데이트됩니다.
 *
 * useEffect: 생명주기 훅
 * - 컴포넌트 마운트 시 1회 데이터 페칭을 실행합니다.
 *
 * ✅ useEffect의 의존성 배열이 []인 이유:
 *   - 학생 목록은 페이지 로드 시 한 번만 가져오면 됩니다.
 *   - 검색은 클라이언트 측에서 이미 가져온 데이터를 필터링하므로
 *     API를 다시 호출할 필요가 없습니다.
 *
 * ❌ 만약 서버 측 검색이라면:
 *   - 의존성 배열에 [search]를 추가하고, search가 변경될 때마다
 *     API에 검색어를 전달하여 결과를 받아와야 합니다.
 *   - 이 경우는 검색어가 바뀔 때마다 네트워크 요청이 발생합니다.
 */
import { useState, useEffect } from 'react';

/*
 * 📦 API 함수 import
 *
 * fetchStudents() 함수는 @/lib/api.js에 정의되어 있습니다.
 * 내부 구현 예시:
 *   export async function fetchStudents() {
 *     const res = await fetch('http://localhost:3001/api/students');
 *     if (!res.ok) throw new Error(...);
 *     return res.json();
 *   }
 *
 * Express 서버의 /api/students 엔드포인트는:
 * - 전체 학생 목록을 JSON 배열로 반환합니다.
 * - 각 학생 객체는 { id, studentId, name, email, createdAt, active } 구조입니다.
 */
import { fetchStudents } from '@/lib/api';

/*
 * =============================================================================
 * 🏗️ StudentsPage 컴포넌트
 * =============================================================================
 *
 * 함수형 컴포넌트는 React 16.8(Hooks 도입) 이후 표준이 되었습니다.
 * 이전에는 클래스 컴포넌트(class Component extends React.Component)를 사용했지만,
 * 현재는 함수형 컴포넌트 + Hooks 조합이 공식 권장 방식입니다.
 */
export default function StudentsPage() {
  /*
   * =============================================================================
   * 📊 State 선언
   * =============================================================================
   *
   * students: DB에서 가져온 전체 학생 배열 (초기값: 빈 배열)
   *   - API 응답이 배열이므로 초기값을 []로 설정합니다.
   *   - null로 설정하면 map() 호출 시 "Cannot read properties of null" 에러가 발생합니다.
   *   - 따라서 데이터 배열은 항상 빈 배열로 초기화하는 것이 안전합니다.
   *
   * loading: API 요청 진행 중인지 여부 (초기값: true)
   *   - true면 로딩 UI 표시, false면 실제 콘텐츠 표시
   *
   * error: API 요청 실패 시 에러 메시지 (초기값: null)
   *   - null이 아니면 에러 UI를 조건부 렌더링으로 표시
   *
   * search: 사용자의 검색 입력값 (초기값: '')
   *   - input onChange → setSearch(e.target.value)로 업데이트
   *   - 검색어가 변경될 때마다 filteredStudents가 다시 계산됨
   */
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  /*
   * =============================================================================
   * 🔄 useEffect — 학생 목록 데이터 로딩
   * =============================================================================
   *
   * 실행 시점: 컴포넌트가 화면에 마운트(mount)된 직후
   * 실행 횟수: 1회 (의존성 배열이 []이므로)
   *
   * 내부 흐름:
   * 1. setLoading(true) → 로딩 UI 활성화
   * 2. await fetchStudents() → Express API 호출 (비동기)
   * 3. setStudents(data) → 받은 데이터를 상태에 저장
   * 4. setLoading(false) → 로딩 UI 비활성화, 학생 테이블 표시
   *
   * 만약 2번에서 에러 발생 시:
   * - catch 블록으로 이동 → setError(err.message)
   * - finally 블록 → setLoading(false) (에러가 있어도 로딩은 종료)
   */
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchStudents();  // Express API 호출
        setStudents(data);                    // 상태 업데이트 → 리렌더링
      } catch (err) {
        setError(err.message);               // 에러 메시지 저장
      } finally {
        setLoading(false);                    // 로딩 종료 (항상 실행)
      }
    };
    loadData();
  }, []);  // 빈 배열: 마운트 시 1회만 실행

  /*
   * =============================================================================
   * 🔍 검색 필터링 — 배열.filter() 메서드
   * =============================================================================
   *
   * JavaScript 배열의 filter() 메서드:
   * - 배열의 각 요소에 대해 조건 함수를 실행합니다.
   * - 조건이 true인 요소만 모아 새 배열을 반환합니다.
   * - 원본 배열(students)은 변경되지 않습니다 (immutable).
   *
   * 이 패턴을 '클라이언트 측 필터링'이라고 합니다.
   * - 장점: 네트워크 요청 없이 즉시 필터링됨 (빠름, 서버 부하 없음)
   * - 단점: 데이터가 매우 많으면 브라우저 성능에 영향
   * - 대안: 서버 측 검색 (검색어를 API로 보내 서버에서 필터링)
   *
   * 📌 화살표 함수 (Arrow Function):
   *   (student) => { return 조건; }
   *   - (매개변수) => { 실행문 }
   *   - 실행문이 한 줄이면 {}와 return 생략 가능
   *   - (student) => student.name.includes(query)  // 한 줄 축약형
   *
   * 📌 includes() 문자열 메서드:
   *   - 문자열에 특정 문자열이 포함되어 있으면 true 반환
   *   - 대소문자 구분: toLowerCase()로 모두 소문자로 변환 후 비교
   */
  const filteredStudents = students.filter((student) => {
    /*
     * 검색어가 비어있으면 (search === '') 모든 학생을 표시합니다.
     * !search → search가 ''(빈 문자열)이면 true
     * 즉시 true 반환 → filter가 모든 요소를 통과시킴
     */
    if (!search) return true;

    /*
     * toLowerCase()로 검색어와 데이터를 모두 소문자로 변환:
     * - 'Kim'을 입력해도 'kim'으로 변환되어 'kim', 'Kim', 'KIM' 모두 검색됨
     * - 대소문자 구분 없는 검색을 위해 필수적인 처리입니다.
     */
    const query = search.toLowerCase();

    /*
     * OR(||) 조건으로 여러 필드에서 동시 검색:
     * - 학생 이름(name), 이메일(email), 학번(studentId) 중 하나라도
     *   검색어를 포함하면 true 반환
     *
     * 옵셔널 체이닝(student.name && student.name.toLowerCase()...):
     * - student.name이 null/undefined면 includes() 호출 시 에러
     * - (student.name && ...)은 name이 존재할 때만 includes() 실행
     * - name이 null이면 false 반환 (단락 평가)
     */
    return (
      (student.name && student.name.toLowerCase().includes(query)) ||
      (student.email && student.email.toLowerCase().includes(query)) ||
      (student.studentId && student.studentId.toLowerCase().includes(query))
    );
  });

  /*
   * =============================================================================
   * 🌀 조건부 렌더링 — 로딩 & 에러 (Early Return)
   * =============================================================================
   *
   * Early Return 패턴:
   * - 조건에 맞으면 해당 JSX를 반환하고 함수를 즉시 종료합니다.
   * - 메인 return문이 깔끔해지고 중첩 조건문을 피할 수 있습니다.
   *
   * 🔹 Inline 조건부 렌더링 (한 줄):
   *   조건 && <요소>  또는  조건 ? <A> : <B>
   *
   * 🔹 Early Return (여러 줄):
   *   if (loading) return <로딩 UI>;
   *   if (error) return <에러 UI>;
   *   return <메인 콘텐츠>;
   *
   * Early Return의 장점:
   * - 로딩/에러 상태 로직이 메인 렌더링과 분리됨
   * - 각 상태의 UI가 독립적으로 관리됨
   * - 조건이 많아져도 가독성이 유지됨
   */
  if (loading) return <div className="loading">학생 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">오류: {error}</div>;

  /*
   * =============================================================================
   * ✅ 메인 렌더링
   * =============================================================================
   *
   * loading === false && error === null → 실제 학생 목록 UI 표시
   */
  return (
    <div>
       
      <div>
        <h1 className="page-title">학생 관리</h1>
        <p className="page-subtitle">코드 교육 랩에 등록된 학생 목록입니다</p>
      </div>

       
      <div style={{ marginBottom: '1.5rem' }}>
        <input
          type="text"
          placeholder="학생 이름, 이메일, 학번으로 검색..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            width: '100%',
            maxWidth: '400px',
            padding: '0.75rem 1rem',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: '0.5rem',
            color: 'var(--text-primary)',
            fontSize: '0.9rem',
          }}
        />
      </div>

       
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>학번</th>
              <th>이름</th>
              <th>이메일</th>
              <th>등록일</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
             
            {filteredStudents.length > 0 ? (
              filteredStudents.map((student, i) => (
                 
                <tr key={student.id || i}>
                  <td>{student.studentId || '-'}</td>
                  <td>{student.name || '-'}</td>
                  <td>{student.email || '-'}</td>
                  <td>
                     
                    {student.createdAt
                      ? new Date(student.createdAt).toLocaleDateString('ko-KR')
                      : '-'}
                  </td>
                  <td>
                     
                    <span className={`badge ${student.active ? 'badge-success' : 'badge-warning'}`}>
                      {student.active ? '활성' : '비활성'}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
               
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', color: '#64748b' }}>
                  {search ? '검색 결과가 없습니다' : '등록된 학생이 없습니다'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

       
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
        총 {filteredStudents.length}명의 학생
        {search && `(전체 ${students.length}명 중 검색 결과)`}
      </p>
    </div>
  );
}

/*
 * =============================================================================
 * 📌 이 페이지에서 배운 핵심 개념
 * =============================================================================
 *
 * 1️⃣ 'use client' 지시어 — 브라우저 상태/이벤트가 필요한 컴포넌트
 * 2️⃣ useState로 검색어(search) 상태 관리
 * 3️⃣ useEffect로 컴포넌트 마운트 시 데이터 페칭
 * 4️⃣ async/await + try-catch-finally 에러 처리 패턴
 * 5️⃣ 배열.filter()로 클라이언트 측 검색 필터링
 * 6️⃣ map() + key로 테이블 리스트 렌더링
 * 7️⃣ 삼항 연산자로 데이터 유무에 따른 UI 분기
 * 8️⃣ 인라인 스타일(style={{}})과 동적 className 생성
 * 9️⃣ 제어 컴포넌트(Controlled Component) 패턴
 * 🔟 toLocaleDateString으로 날짜 포맷팅
 */
