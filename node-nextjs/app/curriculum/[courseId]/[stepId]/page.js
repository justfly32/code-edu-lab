'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { fetchStepDetail, markStepComplete } from '@/lib/api';
import StepNavigation from '@/components/StepNavigation';

/*
 * StepDetail Page - 개별 스텝 학습 페이지
 * 스텝의 상세 지시사항, 코드 예제, 예상 출력, 힌트를 표시
 * 교육용: 인터랙티브 학습 경험 제공
 */
export default function StepDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { courseId, stepId } = params;

  const [step, setStep] = useState(null);
  const [steps, setSteps] = useState([]); // 이전/다음 이동용 전체 스텝 목록
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hintsOpen, setHintsOpen] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchStepDetail(courseId, stepId);
        setStep(data.step || data);
        setSteps(data.allSteps || data.steps || []);
        setCompleted(data.step?.completed || data.completed || false);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [courseId, stepId]);

  /* 스텝 완료 처리 함수 */
  const handleComplete = async () => {
    try {
      setCompleting(true);
      await markStepComplete(stepId);
      setCompleted(true);
    } catch (err) {
      alert('완료 처리에 실패했습니다: ' + err.message);
    } finally {
      setCompleting(false);
    }
  };

  /* 로딩 상태 */
  if (loading) {
    return <div className="loading">스텝을 불러오는 중...</div>;
  }

  /* 에러 상태 */
  if (error) {
    return (
      <div className="error-message">
        오류: {error}
        <br />
        <small>Express 서버가 http://localhost:3001에서 실행 중인지 확인해주세요.</small>
      </div>
    );
  }

  return (
    <div>
      {/* 경로 네비게이션 */}
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

      {/* 스텝 제목 */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="page-title">{step?.title || '스텝 제목 없음'}</h1>
        {step?.description && (
          <p className="page-subtitle">{step.description}</p>
        )}
      </div>

      {/* 지시사항 섹션 - 한국어 상세 설명 */}
      <div className="step-section" style={{ marginBottom: '1.5rem' }}>
        <h2 className="step-section-title">📋 학습 지시사항</h2>
        <div className="step-instruction">
          {step?.instruction || '지시사항이 없습니다.'}
        </div>
      </div>

      {/* 코드 예제 섹션 - 구문 강조 */}
      {step?.code && (
        <div className="step-section" style={{ marginBottom: '1.5rem' }}>
          <h2 className="step-section-title">💻 코드 예제</h2>
          <div className="code-block-wrapper">
            <div className="code-block-header">
              <span className="code-lang-badge">{step?.language || 'javascript'}</span>
              <button
                className="btn-copy"
                onClick={() => navigator.clipboard?.writeText(step.code)}
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

      {/* 예상 출력 섹션 */}
      {step?.expectedOutput && (
        <div className="step-section" style={{ marginBottom: '1.5rem' }}>
          <h2 className="step-section-title">✅ 예상 출력</h2>
          <div className="expected-output">
            <pre>{step.expectedOutput}</pre>
          </div>
        </div>
      )}

      {/* 힌트 섹션 - 접기/펼치기 가능 */}
      {step?.hints && step.hints.length > 0 && (
        <div className="step-section" style={{ marginBottom: '1.5rem' }}>
          <button
            className="hints-toggle"
            onClick={() => setHintsOpen(!hintsOpen)}
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

      {/* 완료 버튼 */}
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

      {/* 이전/다음 네비게이션 */}
      {steps.length > 0 && (
        <StepNavigation courseId={courseId} steps={steps} currentStepId={stepId} />
      )}
    </div>
  );
}
