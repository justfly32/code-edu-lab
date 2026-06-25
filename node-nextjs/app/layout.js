import Navbar from '@/components/Navbar';
import './globals.css';

/*
 * Root Layout - 모든 �이�의 공통 �에서
 * 내비게이션 바를 포함하며, 모든 자식 �이� 요소로 구성
 * 교육용 이 레이어 구�를 보여�
 */

export const metadata = {
  title: '코드 교육 랩 - 대�보드',
  description: '코� �용 관� 시스템',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <head>
        {/* Google Fonts - 한국어 지원�는 Pretendard ��트 */}
        <link
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* 모든 �이�에 공통으로 �시�는 내�게이� 바 */}
        <Navbar />
        {/* �이�별 콘�츠가 들어가는 � */}
        <main className="main-content">
          {children}
        </main>
      </body>
    </html>
  );
}
