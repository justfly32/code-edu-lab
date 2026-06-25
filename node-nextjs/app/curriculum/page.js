'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import CurriculumCard from '@/components/CurriculumCard';
import { fetchCurriculumOverview } from '@/lib/api';

/*
 * Curriculum Page - 커리큘럼 개요 페이지
 * 전체 과목 목록과 각 과목의 진행률을 한눈에 확인
 * 교육용: 카드 기반 레이아웃과 진행률 시각화
 */
export default function CurriculumPage() {
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
    return <div className="loading">커리큘럼을 불러오는 중...</div>;
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

  // 전체 진행률 계산
  const courses = curriculum?.courses || [];
  const totalSteps = courses.reduce((sum, c) => sum + (c.totalSteps || 0), 0);
  const completedSteps = courses.reduce((sum, c) => sum + (c.completedSteps || 0), 0);
  const overallProgress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div>
      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">커리큘럼 가이드</h1>
        <p className="page-subtitle">코드 교육 랩의 전체 과목과 학습 현황을 확인하세요</p>
      </div>

      {/* 전체 진행률 요약 */}
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

      {/* 과목 카드 그리드 */}
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

      {/* 모듈 목록 섹션 (있을 경우) */}
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
