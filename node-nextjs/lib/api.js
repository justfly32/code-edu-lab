/**
 * API 통신 모듈
 * Express 백엔드(http://localhost:3001)와 통신하는 함수 모음
 * 교육용 코드: 각 함수가 어� 역할을 하는지 주석으로 설명
 */

// API 기본 URL - Express 서버 주소
const API_BASE = 'http://localhost:3001/api';

/**
 * 대시보드 KPI 데이터를 가져오는 함수
 * @returns {Promise<Object>} 통계 데이터 (학생 수, 과목 수, 제출 수, 평균 점수)
 */
export async function fetchDashboardStats() {
  // Express API에서 대시보드 통계 데이터 요청
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  if (!res.ok) throw new Error('대시보드 통계를 가져올 수 없습니다');
  return res.json();
}

/**
 * 차트용 과목별 데이터를 가져오는 함수
 * @returns {Promise<Object>} 과목별 학생 수, 평균 점수 데이터
 */
export async function fetchCourseChartData() {
  const res = await fetch(`${API_BASE}/dashboard/charts`);
  if (!res.ok) throw new Error('차트 데이터를 가져올 수 없습니다');
  return res.json();
}

/**
 * 전체 학생 목록을 가져오는 함수
 * @returns {Promise<Array>} 학생 배열
 */
export async function fetchStudents() {
  const res = await fetch(`${API_BASE}/students`);
  if (!res.ok) throw new Error('학생 목록을 가져올 수 없습니다');
  return res.json();
}

/**
 * 전체 과목 목록을 가져오는 함수
 * @returns {Promise<Array>} 과목 배열
 */
export async function fetchCourses() {
  const res = await fetch(`${API_BASE}/courses`);
  if (!res.ok) throw new Error('과목 목록을 가져올 수 없습니다');
  return res.json();
}

/**
 * 전체 제출 목록을 가져오는 함수
 * @returns {Promise<Array>} 제출 배열
 */
export async function fetchSubmissions() {
  const res = await fetch(`${API_BASE}/submissions`);
  if (!res.ok) throw new Error('제출 목록을 가져올 수 없습니다');
  return res.json();
}

/**
 * 최근 제출 목록을 가져오는 함수 (대시보드용)
 * @param {number} limit - 가져올 개수
 * @returns {Promise<Array>} 최근 제출 배열
 */
export async function fetchRecentSubmissions(limit = 5) {
  const res = await fetch(`${API_BASE}/submissions/recent?limit=${limit}`);
  if (!res.ok) throw new Error('최근 제출을 가져올 수 없습니다');
  return res.json();
}

/**
 * 커리큘럼 개요를 가져오는 함수
 * 전체 과목 목록과 각 과목의 진행률을 반환
 * @returns {Promise<Object>} 커리큘럼 개요 데이터 (courses 배열, overallProgress 등)
 */
export async function fetchCurriculumOverview() {
  const res = await fetch(`${API_BASE}/curriculum/overview`);
  if (!res.ok) throw new Error('커리큘럼 개요를 가져올 수 없습니다');
  return res.json();
}

/**
 * 특정 과목의 모듈 목록을 가져오는 함수
 * @param {string} courseId - 과목 식별자
 * @returns {Promise<Object>} 과목 상세 정보 (modules 배열, steps 포함)
 */
export async function fetchCourseModules(courseId) {
  const res = await fetch(`${API_BASE}/curriculum/${courseId}/modules`);
  if (!res.ok) throw new Error('과목 모듈을 가져올 수 없습니다');
  return res.json();
}

/**
 * 특정 스텝의 상세 정보를 가져오는 함수
 * @param {string} courseId - 과목 식별자
 * @param {string} stepId - 스텝 식별자
 * @returns {Promise<Object>} 스텝 상세 정보 (instruction, code, hints, expectedOutput 등)
 */
export async function fetchStepDetail(courseId, stepId) {
  const res = await fetch(`${API_BASE}/curriculum/${courseId}/steps/${stepId}`);
  if (!res.ok) throw new Error('스텝 상세 정보를 가져올 수 없습니다');
  return res.json();
}

/**
 * 스텝을 완료 상태로 표시하는 함수
 * @param {string} stepId - 완료할 스텝 식별자
 * @returns {Promise<Object>} 완료 결과 (success, completedAt 등)
 */
export async function markStepComplete(stepId) {
  const res = await fetch(`${API_BASE}/curriculum/steps/${stepId}/complete`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('스텝 완료 처리에 실패했습니다');
  return res.json();
}
