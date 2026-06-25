'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { fetchCurriculumOverview } from '@/lib/api';

/*
 * Progress Page - 학생 진행 대시보드
 * 전체 학습 진행 현황을 시각적으로 표시
 * 교육용: 진행률 차트와 통계 시각화
 */
export default function ProgressPage() {
  const [curriculum, setCurriculum] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  // 로딩 상태
  if (loading) {
    return <div className="loading">진행 현황을 불러오는 중...</div>;
  }

  // 에러 상태
  if (error) {
    return (
      <div className="error-message">
        오류: {error}
        <br />
        <small>Express 서버가 http://localhost:3001에서 실행 중인지 확인해주세요.</small>
      </div>
    );
  }

  const courses = curriculum?.courses || [];
  const totalSteps = courses.reduce((sum, c) => sum + (c.totalSteps || 0), 0);
  const completedSteps = courses.reduce((sum, c) => sum + (c.completedSteps || 0), 0);
  const overallProgress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div>
      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">학습 현황</h1>
        <p className="page-subtitle">나의 학습 진행 상황을 확인하세요</p>
      </div>

      {/* 전체 진행 통계 카드 */}
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

      {/* 전체 진행률 바 */}
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

      {/* 과목별 진행 현황 */}
      <h2 className="chart-title">과목별 진행 현황</h2>
      <div className="course-progress-list" style={{ marginTop: '1rem' }}>
        {courses.length > 0 ? (
          courses.map((course, i) => {
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
                {/* 과목 헤더 */}
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

                {/* 과목 설명 */}
                {course.description && (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                    {course.description}
                  </p>
                )}

                {/* 진행률 바 */}
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

      {/* 학습 팁 섹션 */}
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
