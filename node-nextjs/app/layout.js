/*
 * =============================================================================
 * 📄 layout.js — Next.js App Router의 루트 레이아웃 파일
 * =============================================================================
 *
 * 📌 Next.js App Router 학습 포인트:
 *
 * 1️⃣ layout.js의 역할 (파일 시스템 라우팅):
 *    - app/ 디렉토리 아래에 있는 layout.js는 해당 폴더와 모든 하위 페이지의
 *      '공통 레이아웃'을 정의합니다.
 *    - 루트 layout.js(app/layout.js)는 전체 애플리케이션의 HTML 구조를 정의합니다.
 *    - 페이지마다 공통으로 보여줄 UI(내비게이션 바, 푸터, 사이드바 등)를 여기에 배치합니다.
 *
 * 2️⃣ 서버 컴포넌트 (Server Component):
 *    - layout.js는 'use client' 지시어가 없으므로 **서버 컴포넌트**입니다.
 *    - 서버 컴포넌트는 서버에서만 렌더링되며, 클라이언트로 전송되는 JavaScript
 *      번들 크기를 줄여줍니다.
 *    - 서버 컴포넌트에서는 useState, useEffect, onClick 등의 브라우저 기능을
 *      사용할 수 없습니다 → 사용자 인터랙션이 필요하면 'use client'를 추가해야 합니다.
 *    - 메타데이터 export, 데이터베이스 직접 조회 등은 서버 컴포넌트에서 수행합니다.
 *
 * 3️⃣ metadata 객체 (SEO & 메타데이터):
 *    - Next.js 13+에서는 layout.js(또는 page.js)에서 metadata 객체를 export하면
 *      HTML <head>의 <title>, <meta> 태그를 자동 생성합니다.
 *    - 이는 정적 메타데이터 방식이며, 동적 메타데이터는 generateMetadata() 함수를 사용합니다.
 *
 * 4️⃣ {children} prop:
 *    - layout 컴포넌트는 props로 { children }을 받습니다.
 *    - children은 현재 라우트에 해당하는 page.js의 렌더링 결과가 전달됩니다.
 *    - 즉, layout.js가 감싸는 틀이고, page.js가 그 안에 들어가는 내용물입니다.
 *
 * 5️⃣ 글로벌 CSS (globals.css):
 *    - import './globals.css'는 애플리케이션 전체에 적용되는 전역 스타일시트입니다.
 *    - 루트 레이아웃에서 한 번만 import하면 모든 페이지에 적용됩니다.
 *    - Tailwind CSS를 사용한다면 @tailwind 지시어가 포함된 CSS 파일을 여기서 import합니다.
 */

import Navbar from '@/components/Navbar';
/*
 * '@/' 경로 별칭(alias):
 * - Next.js는 jsconfig.json(또는 tsconfig.json)의 paths 설정을 통해
 *   '@/'를 'src/' 또는 프로젝트 루트의 특정 디렉토리로 매핑합니다.
 * - '../../components/Navbar' 같은 상대 경로 대신 '@/'를 사용하면
 *   경로가 간결해지고 파일 이동 시 import 경로를 수정할 필요가 줄어듭니다.
 */

import './globals.css';
/*
 * globals.css import:
 * - 이 파일은 전역 CSS 리셋, CSS 변수(custom properties), 기본 타이포그래피,
 *   공통 클래스 등을 정의합니다.
 * - CSS Module(.module.css)과 달리, 이 스타일은 컴포넌트 범위가 제한되지 않고
 *   전역에 적용됩니다.
 * - CSS Module을 사용하면 클래스명이 자동으로 해싱되어 스타일 충돌을 방지합니다.
 */

/* =============================================================================
 * 📋 메타데이터 설정
 * =============================================================================
 * Next.js 13+ App Router에서는 layout.js 또는 page.js에서 metadata 객체를
 * export하면 HTML <head>에 해당 meta 태그가 자동 주입됩니다.
 *
 * 정적 메타데이터: 아래처럼 객체를 직접 export (고정된 값)
 * 동적 메타데이터: generateMetadata() 함수를 async로 export (요청 시 동적 생성)
 *
 * 주요 속성:
 * - title: 브라우저 탭 제목, SEO <title> 태그
 * - description: 검색 엔진 결과에 표시되는 설명, <meta name="description">
 * - openGraph: SNS 공유 시 표시되는 미리보기 정보 (Facebook, Twitter, Slack 등)
 * - icons: 파비콘 설정
 */

export const metadata = {
  title: '코드 교육 랩 - 대시보드',
  /*
   * title 템플릿: template 속성을 사용하면 자식 페이지에서 title을 설정할 때
   * '%s | 사이트명' 형태로 자동 포맷됩니다.
   * 예) template: '%s | 코드 교육 랩'
   *     자식 페이지에서 title: '학생 목록' → 결과: '학생 목록 | 코드 교육 랩'
   */
  description: '코드 교육 랩 사용자 관리 시스템 — Next.js와 Express로 구축된 학습 대시보드',
  /*
   * description은 검색엔진 최적화(SEO)에서 중요한 요소입니다.
   * 150~160자 내외로 페이지의 목적을 요약하는 것이 좋습니다.
   */
};

/* =============================================================================
 * 🏗️ RootLayout 컴포넌트
 * =============================================================================
 *
 * 이 컴포넌트는 모든 페이지의 HTML 뼈대를 정의합니다.
 * JSX 문법 설명:
 * - HTML처럼 보이지만 실제로는 JavaScript의 확장 문법인 JSX입니다.
 * - JSX는 React.createElement() 호출로 변환되어 가상 DOM(Virtual DOM)을 생성합니다.
 * - {} 중괄호 안에는 JavaScript 표현식을 사용할 수 있습니다 (변수, 함수 호출 등).
 * - HTML과의 차이점: class → className, for → htmlFor, style={{ }} (객체 전달)
 */

export default function RootLayout({ children }) {
  /*
   * 함수형 컴포넌트:
   * - React 컴포넌트는 JavaScript 함수로 작성됩니다.
   * - props(속성)를 인자로 받아 JSX를 반환(return)합니다.
   * - { children }은 props 객체를 구조 분해 할당(destructuring)한 것입니다.
   *   (props.children 대신 { children }으로 직접 사용)
   */

  return (
    /*
     * ☕ JSX 규칙:
     * 1. 반드시 하나의 최상위 부모 요소로 감싸야 합니다.
     *    (<html>이 최상위, 또는 <></> Fragment 사용)
     * 2. 모든 태그는 닫혀야 합니다 (<br />, <input />)
     * 3. 속성은 camelCase로 작성합니다 (tabIndex, backgroundColor)
     * 4. 조건부 렌더링: {조건 && <요소>} 또는 {조건 ? <A> : <B>}
     * 5. 리스트 렌더링: {배열.map(item => <요소 key={item.id} />)}
     */
    <html lang="ko">
      {/*
       * <html lang="ko">:
       * - lang 속성은 스크린 리더(시각 장애인용 보조 기술)가 올바른 발음으로
       *   읽을 수 있도록 도와줍니다 (접근성, a11y).
       * - 검색 엔진이 페이지의 언어를 인식하는 데도 도움이 됩니다.
       */}
      <head>
        {/*
         * ★ Next.js의 <head> 특별 처리:
         * - Next.js는 <head> 내의 요소들을 자동으로 관리합니다.
         * - metadata 객체에서 설정한 title과 description은 자동으로 <head>에 추가됩니다.
         * - <link>, <script> 등 필요한 태그를 직접 추가할 수 있습니다.
         */}

        {/* 📐 Google Fonts - Pretendard 폰트
         *
         * Pretendard는 한국어에 최적화된 시스템-ui 대체 폰트입니다.
         * - CDN(Content Delivery Network)에서 CSS 파일을 로드합니다.
         * - @import 방식보다 <link> 방식이 페이지 로딩 성능에 더 유리합니다.
         * - next/font를 사용하면 폰트를 자체 호스팅하여 성능과 개인정보 보호에 유리합니다.
         *   (예: import local from 'next/font/local')
         */}
        <link
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css"
          rel="stylesheet"
        />
      </head>
      <body>
        {/*
         * 🧭 내비게이션 바 (Navbar 컴포넌트)
         *
         * Navbar는 모든 페이지에 공통으로 표시되는 메뉴입니다.
         * - 내부에 <Link> 컴포넌트를 사용하여 페이지 간 이동을 처리합니다.
         * - <Link>는 Next.js에서 제공하는 클라이언트 사이드 네비게이션 컴포넌트입니다.
         *   - <a> 태그와 달리 페이지 전체를 새로고침하지 않고 필요한 부분만 업데이트합니다.
         *   - 미리 관련 페이지의 코드를 prefetch(사전 로드)하여 빠른 이동을 제공합니다.
         * - 사용 예: <Link href="/students">학생 관리</Link>
         */}
        <Navbar />

        {/*
         * 📄 페이지 콘텐츠 영역 (children)
         *
         * {children}이 실제로 렌더링되는 위치입니다.
         * - 사용자가 /students로 접속하면 students/page.js의 내용이 children으로 전달됩니다.
         * - <main> 태그는 HTML5의 시맨틱 태그로, 페이지의 주요 콘텐츠 영역을 나타냅니다.
         * - 시맨틱 태그를 사용하면 검색 엔진과 스크린 리더가 페이지 구조를 더 잘 이해합니다.
         */}
        <main className="main-content">
          {/*
           * className="main-content":
           * - HTML의 class 속성에 해당합니다 (JSX에서는 className 사용)
           * - CSS Module을 사용 중이라면: import styles from './layout.module.css'
           *   → <main className={styles.mainContent}>
           * - CSS Module은 클래스명을 고유한 해시값으로 변환하여 스타일 충돌을 방지합니다.
           */}
          {children}
        </main>
      </body>
    </html>
  );
}

/*
 * =============================================================================
 * 📌 요약: Next.js App Router 파일 시스템 라우팅
 * =============================================================================
 *
 * app/                         → 루트 경로 (/)
 * ├── layout.js                → 모든 페이지의 공통 레이아웃 (이 파일)
 * ├── page.js                  → / 경로 (메인 대시보드)
 * ├── students/
 * │   └── page.js              → /students
 * ├── courses/
 * │   └── page.js              → /courses
 * ├── curriculum/
 * │   ├── page.js              → /curriculum
 * │   └── [courseId]/
 * │       ├── page.js          → /curriculum/123 (동적 라우트)
 * │       └── [stepId]/
 * │           └── page.js      → /curriculum/123/step-1 (중첩 동적 라우트)
 * ├── progress/
 * │   └── page.js              → /progress
 * └── submissions/
 *     └── page.js              → /submissions
 *
 * 🔑 핵심 규칙:
 * - 폴더 = URL 경로 세그먼트
 * - page.js = 해당 경로의 실제 페이지 콘텐츠
 * - layout.js = 해당 경로와 하위 경로의 공통 레이아웃
 * - [param] 폴더 = 동적 라우트 (URL 파라미터)
 * - loading.js = 로딩 UI (자동 Suspense 처리)
 * - error.js = 에러 UI (자동 Error Boundary 처리)
 * - not-found.js = 404 페이지
 */
