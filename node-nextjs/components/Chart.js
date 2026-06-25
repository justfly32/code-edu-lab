'use client'; // 클라이언트 컴포�트 - 차트 �더링에 필요

import { useEffect, useRef } from 'react';

/*
 * Chart 컴포�트 - Chart.js를 사용한 데이터 시각화
 * 교육용: CDN을 통해 Chart.js를 로드하고 canvas에 차트를 그리는 예제
 */

export default function Chart({ type = 'bar', data, options, title }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    // Chart.js를 CDN에서 동적으로 로드
    const loadChart = async () => {
      let ChartLib;

      // 전역 Chart.js가 없으면 CDN에서 로드
      if (typeof window.Chart === 'undefined') {
        // chart.js 스크립트 태그 생성
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
        document.head.appendChild(script);

        // 로드 �료 대기
        await new Promise((resolve, reject) => {
          script.onload = resolve;
          script.onerror = reject;
        });
      }

      ChartLib = window.Chart;

      // 이미 차트가 있으면 파괴 후 재생성
      if (chartRef.current) {
        chartRef.current.destroy();
      }

      // 다크 테마에 맞는 기본 �션
      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#94a3b8',
              font: { family: 'Pretendard, sans-serif', size: 12 }
            }
          }
        },
        scales: {
          x: {
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(71, 85, 105, 0.3)' }
          },
          y: {
            ticks: { color: '#94a3b8' },
            grid: { color: 'rgba(71, 85, 105, 0.3)' }
          }
        }
      };

      // 차트 생성
      if (canvasRef.current) {
        chartRef.current = new ChartLib(canvasRef.current, {
          type,
          data,
          options: { ...defaultOptions, ...options }
        });
      }
    };

    loadChart();

    // 클린업 - �포넌트 언마운트 시 차트 파괴
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, [type, data, options]);

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      {/* 차트가 그려질 canvas 요소 */}
      <div style={{ height: '300px' }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  );
}
