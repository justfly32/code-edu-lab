'use client'; // 클라이언트 �포넌트 - fetch 사용

import { useState, useEffect } from 'react';
import { fetchStudents } from '@/lib/api';

/*
 * Students Page - 학생 관리 페이지
 * Express API에서 학생 목록을 가져와 테이블로 �시
 * 교육용: 테이블 �더링과 �색 기능의 기본
 */

export default function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const data = await fetchStudents();
        setStudents(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // 검색 필터링 - 학생 이름 또는 이메일 기준
  const filteredStudents = students.filter((student) => {
    if (!search) return true;
    const query = search.toLowerCase();
    return (
      (student.name && student.name.toLowerCase().includes(query)) ||
      (student.email && student.email.toLowerCase().includes(query)) ||
      (student.studentId && student.studentId.toLowerCase().includes(query))
    );
  });

  if (loading) return <div className="loading">학생 목록을 불러오는 중...</div>;
  if (error) return <div className="error-message">오류: {error}</div>;

  return (
    <div>
      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">학생 관리</h1>
        <p className="page-subtitle">코드 교육 랩에 등록된 학생 목록입니다</p>
      </div>

      {/* 검색 입력 - 필터링용 */}
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

      {/* 학생 테이블 */}
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

      {/* 총 학생 수 �시 */}
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
        총 {filteredStudents.length}명의 학생
        {search && `(전체 ${students.length}명 중 검색 결과)`}
      </p>
    </div>
  );
}
