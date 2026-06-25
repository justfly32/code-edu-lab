'use client'; // 클라이언트 �포넌트 - API 데이터 로�에 필요

import { useState, useEffect } from 'react';
import StatCard from '@/components/StatCard';
import Chart from '@/components/Chart';
import { fetchDashboardStats, fetchCourseChartData, fetchRecentSubmissions } from '@/lib/api';

/*
 * Dashboard Page - 메인 대시보드
 * 전체 현황을 보여주는 KPI 카드와 차트를 �시
 * 교육용: API 데이터를 가져와 화면에 렌더링하는 패턴
 */

export default function DashboardPage() {
  // 상태 변수 - 로딩, 데이터, 에러
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [recentSubmissions, setRecentSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // �포넌트가 마운트될 때 API에서 데이터를 가져옴
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        // API 병렬 요청 - Promise.all 활용
        const [statsData, chart, submissions] = await Promise.all([
          fetchDashboardStats(),
          fetchCourseChartData(),
          fetchRecentSubmissions(),
        ]);
        setStats(statsData);
        setChartData(chart);
        setRecentSubmissions(submissions);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // 로딩 중 메시지
  if (loading) {
    return (
      <div className="loading">
        <p>데이터를 불러오는 중...</p>
      </div>
    );
  }

  // 에러 메시지
  if (error) {
    return (
      <div className="error-message">
        API 서버에 연결할 수 없습니다: {error}
        <br />
        <small>Express 서버가 http://localhost:3001에서 실행 중인지 확인해주세요.</small>
      </div>
    );
  }

  return (
    <div>
      {/* 페이지 제목 */}
      <div>
        <h1 className="page-title">대시보드</h1>
        <p className="page-subtitle">코드 교육 랩의 전체 현황을 한눈에 확인하세요</p>
      </div>

      {/* KPI 카드 4개 - 주요 지표 �시 */}
      <div className="stats-grid">
        <StatCard
          label="전체 학생 수"
          value={stats?.totalStudents ?? '—'}
          change="이번 주 +5"
          changeType="positive"
        />
        <StatCard
          label="등록 과목 수"
          value={stats?.totalCourses ?? '—'}
          change="이번 주 +2"
          changeType="positive"
        />
        <StatCard
          label="누적 제출"
          value={stats?.totalSubmissions ?? '—'}
          change="오늘 12건"
          changeType="positive"
        />
        <StatCard
          label="평균 정답률"
          value={stats?.averageScore ? `${stats.averageScore}%` : '—'}
          change="-2.3%"
          changeType="negative"
        />
      </div>

      {/* 과목별 통계 차트 - Chart.js */}
      {chartData && (
        <Chart
          type="bar"
          title="과목별 통계"
          data={{
            labels: chartData.courses || [],
            datasets: [
              {
                label: '학생 수',
                data: chartData.studentCounts || [],
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: '#3b82f6',
                borderWidth: 1,
              },
              {
                label: '평균 점수',
                data: chartData.averageScores || [],
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: '#8b5cf6',
                borderWidth: 1,
              },
            ],
          }}
        />
      )}

      {/* 최근 제출 목록 */}
      <div className="table-wrapper">
        <h3 className="chart-title">최근 제출 현황</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>학생</th>
              <th>과목</th>
              <th style={{ width: '100px' }}>점수</th>
              <th style={{ width: '100px' }}>상태</th>
            </tr>
          </thead>
          <tbody>
            {recentSubmissions && recentSubmissions.length > 0
              ? recentSubmissions.map((sub, i) => (
                  <tr key={sub.id || i}>
                    <td>{sub.studentName || '-'}</td>
                    <td>{sub.courseName || '-'}</td>
                    <td>{sub.score ?? '-'}{typeof sub.score === 'number' ? '점' : ''}</td>
                    <td>
                      <span className={`badge ${sub.status === 'pass' ? 'badge-success' : 'badge-danger'}`}>
                        {sub.status === 'pass' ? '통과' : '실패'}
                      </span>
                    </td>
                  </tr>
                ))
              : (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', color: '#64748b' }}>
                    제출 내역이 없습니다
                  </td>
                </tr>
              )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
