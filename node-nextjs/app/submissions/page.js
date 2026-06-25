'use client';

import { useState, useEffect } from 'react';
import { fetchSubmissions } from '@/lib/api';

/*
 * Submissions Page - 제출 현황 페이지
 * Express API에서 제출 목록을 가져와 코드 프리뷰와 함께 표시
 * 교육용: 코드 블록 렌더링과 상태 관리
 */

export default function SubmissionsPage() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchSubmissions();
        setSubmissions(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // 상태별 뱃지 매핑 함수
  function getStatusBadge(status) {
    // status의 다양한 형태를 처리
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

  if (loading) return <div className="loading">제출 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">오류: {error}</div>;

  return (
    <div>
      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">제출 현황</h1>
        <p className="page-subtitle">학생들의 코드 제출 � 채점 결과입니다</p>
      </div>

      {/* 제출 목록 - 카드 형태 */}
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
              {/* 헤더: 학생명, 과목명, 상태 */}
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

              {/* 코드 프리� */}
              {sub.code && (
                <div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    제출 코드:
                  </p>
                  <pre className="code-block">{sub.code}</pre>
                </div>
              )}

              {/* 메타 정보 */}
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
