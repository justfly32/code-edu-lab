'use client';

import { useState, useEffect } from 'react';
import { fetchCourses } from '@/lib/api';

/*
 * Courses Page - 과목 목록 페이지
 * Express API에서 과목 목록을 가져와 카드 형태로 표시
 * 교육용: 카드 그리드 레이아웃과 상태별 �지 표시
 */

export default function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchCourses();
        setCourses(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) return <div className="loading">과목 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">오류: {error}</div>;

  return (
    <div>
      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">과목 목록</h1>
        <p className="page-subtitle">코드 교육 �에서 제공하는 과목입니다</p>
      </div>

      {/* 과목 카드 그리드 */}
      <div className="card-grid">
        {courses.length > 0 ? (
          courses.map((course, i) => (
            <div className="course-card" key={course.id || i}>
              {/* 과목 제목 */}
              <h3 className="course-card-title">
                {course.name || course.title || '과목명 없음'}
              </h3>
              {/* 과목 설명 */}
              <p className="course-card-desc">
                {course.description || '설명이 없습니다'}
              </p>
              {/* 메타 정보: 학생 수, 난이도, 상태 */}
              <div className="course-card-meta">
                <div>
                  {course.studentCount !== undefined && (
                    <span>수강생: {course.studentCount}명</span>
                  )}
                </div>
                <div>
                  {course.level && (
                    <span className="badge badge-info">{course.level}</span>
                  )}
                </div>
              </div>
              {/* 상태 뱃지 */}
              <div style={{ marginTop: '0.75rem' }}>
                <span className={`badge ${course.active ? 'badge-success' : 'badge-warning'}`}>
                  {course.active ? '진행중' : '종료'}
                </span>
              </div>
            </div>
          ))
        ) : (
          <div style={{ color: '#64748b', padding: '2rem', textAlign: 'center' }}>
            등록된 과목이 없습니다
          </div>
        )}
      </div>
    </div>
  );
}
