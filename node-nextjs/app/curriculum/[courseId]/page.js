'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { fetchCourseModules } from '@/lib/api';

/*
 * CourseDetail Page - 과목 상세 페이지
 * 선택한 과목의 모듈 목록과 각 모듈의 스텝을 표시
 * 교육용: 아코디언 형태의 모듈 확장/축소 UI
 */
export default function CourseDetailPage() {
  const params = useParams();
  const courseId = params.courseId;

  const [courseData, setCourseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedModules, setExpandedModules] = useState({});

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchCourseModules(courseId);
        setCourseData(data);
        // 첫 번째 모듈은 기본적으로 펼쳐서 보여줌
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
  }, [courseId]);

  // 모듈 토글 (열기/닫기)
  const toggleModule = (moduleId) => {
    setExpandedModules((prev) => ({
      ...prev,
      [moduleId]: !prev[moduleId],
    }));
  };

  // 로딩 상태
  if (loading) {
    return <div className="loading">과목 정보를 불러오는 중...</div>;
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

  const course = courseData?.course || {};
  const modules = courseData?.modules || [];
  const totalSteps = modules.reduce((sum, m) => sum + (m.steps?.length || 0), 0);
  const completedSteps = modules.reduce(
    (sum, m) => sum + (m.steps?.filter((s) => s.completed).length || 0),
    0
  );
  const progress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div>
      {/* 경로 네비게이션 (브레드크럼) */}
      <nav style={{ marginBottom: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <Link href="/curriculum" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
          커리큘럼
        </Link>
        {' > '}
        <span>{course.name || course.title || courseId}</span>
      </nav>

      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">{course.name || course.title || '과목명 없음'}</h1>
        <p className="page-subtitle">{course.description || '과목 설명이 없습니다'}</p>
      </div>

      {/* 과목 진행률 */}
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

      {/* 모듈 목록 - 아코디언 형태 */}
      <div className="module-list">
        {modules.length > 0 ? (
          modules.map((module, moduleIndex) => (
            <div key={module.id || moduleIndex} className="module-item">
              {/* 모듈 헤더 - 클릭하면 토글 */}
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
                  cursor: 'pointer',
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

              {/* 모듈 내용 - 스텝 목록 (펼칠 때만 표시) */}
              {expandedModules[module.id] && module.steps && (
                <div className="module-steps" style={{ padding: '0.5rem 0' }}>
                  {module.steps.map((step, stepIndex) => (
                    <Link
                      key={step.id || stepIndex}
                      href={`/curriculum/${courseId}/${step.id}`}
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
                        textDecoration: 'none',
                        color: 'var(--text-primary)',
                        transition: 'background-color 0.2s',
                      }}
                    >
                      {/* 완료 상태 표시 */}
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

                      {/* 스텝 제목 */}
                      <span style={{ flex: 1 }}>
                        <span style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }}>
                          {stepIndex + 1}.
                        </span>
                        {step.title || step.id}
                      </span>

                      {/* 화살표 아이콘 */}
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
