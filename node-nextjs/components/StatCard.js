/*
 * StatCard 컴포넌트 - 대시보드 통계 카드
 * 단일 숫자 값과 �찰 �시에 사용
 * props: label(�이름), value(값), change(증감), changeType(증감 유형)
 */

export default function StatCard({ label, value, change, changeType }) {
  return (
    <div className="stat-card">
      {/* �이 정보 */}
      <div className="stat-card-label">{label}</div>
      {/* 메인 값 */}
      <div className="stat-card-value">{value}</div>
      {/* 증감 표시 (선택) */}
      {change && (
        <div className={`stat-card-change ${changeType}`}>
          {changeType === 'positive' ? '▲' : changeType === 'negative' ? '▼' : '—'} {change}
        </div>
      )}
    </div>
  );
}
