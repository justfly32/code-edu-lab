'use client';

import Link from 'next/link';

/*
 * StepNavigation 컴포넌트 - 스텝 간 이동 네비게이션
 * 이전/다음 스텝으로 이동하는 버튼 제공
 * 교육용: 순차적 학습 진행 패턴
 */
export default function StepNavigation({ courseId, steps, currentStepId }) {
  // 현재 스텝의 인덱스 찾기
  const currentIndex = steps.findIndex((step) => step.id === currentStepId);
  const prevStep = currentIndex > 0 ? steps[currentIndex - 1] : null;
  const nextStep = currentIndex < steps.length - 1 ? steps[currentIndex + 1] : null;

  // 진행률 계산
  const progress = ((currentIndex + 1) / steps.length) * 100;

  return (
    <div className="step-navigation">
      {/* 진행 표시 */}
      <div className="step-progress-info">
        <span>스텝 {currentIndex + 1} / {steps.length}</span>
        <div className="progress-bar-bg" style={{ flex: 1, marginLeft: '1rem' }}>
          <div
            className="progress-bar-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 이전/다음 버튼 */}
      <div className="step-nav-buttons">
        {prevStep ? (
          <Link href={`/curriculum/${courseId}/${prevStep.id}`} className="btn btn-secondary">
            ← 이전: {prevStep.title || prevStep.id}
          </Link>
        ) : (
          <div /> // 빈 공간 유지
        )}

        {nextStep ? (
          <Link href={`/curriculum/${courseId}/${nextStep.id}`} className="btn btn-primary">
            다음: {nextStep.title || nextStep.id} →
          </Link>
        ) : (
          <Link href={`/curriculum/${courseId}`} className="btn btn-success">
            과목 완료로 돌아가기 ✓
          </Link>
        )}
      </div>
    </div>
  );
}
