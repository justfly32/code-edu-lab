'use client';

import Link from 'next/link';

/*
 * CurriculumCard 컴포넌트 - 커리큘럼 과목 카드
 * 과목 제목, 설명, 진행률을 시각적으로 표시
 * 교육용: 진행률 바와 링크 네비게이션 패턴
 */
export default function CurriculumCard({ course }) {
  // 진행률 계산 (완료된 스텝 / 전체 스텝)
  const totalSteps = course.totalSteps || 0;
  const completedSteps = course.completedSteps || 0;
  const progress = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0;

  return (
    <div className="curriculum-card">
      {/* 과목 제목 */}
      <h3 className="curriculum-card-title">
        <Link href={`/curriculum/${course.id}`}>
          {course.name || course.title || '과목명 없음'}
        </Link>
      </h3>

      {/* 과목 설명 */}
      <p className="curriculum-card-desc">
        {course.description || '설명이 없습니다'}
      </p>

      {/* 모듈 수 및 스텝 수 정보 */}
      <div className="curriculum-card-meta">
        <span>모듈: {course.moduleCount || 0}개</span>
        <span>스텝: {totalSteps}개</span>
      </div>

      {/* 진행률 바 */}
      <div className="progress-bar-container">
        <div className="progress-bar-bg">
          <div
            className="progress-bar-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="progress-text">
          {completedSteps}/{totalSteps} 완료 ({progress}%)
        </span>
      </div>

      {/* 난이도 뱃지 */}
      {course.level && (
        <div style={{ marginTop: '0.75rem' }}>
          <span className="badge badge-info">{course.level}</span>
        </div>
      )}
    </div>
  );
}
