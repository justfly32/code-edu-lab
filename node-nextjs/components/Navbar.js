'use client'; // 클라이언트 컴포�트 - 현재 페이지 감지에 필요

import Link from 'next/link';
import { usePathname } from 'next/navigation';

/*
 * Navbar �포�트 - 상단 내비게이션 바
 * 현재 경로에 �라 활성 �크를 강조 표시
 * 교육용: usePathname() 훅의 사용법을 보여�
 */

// 네비게이션 항목 설정
const navItems = [
  { href: '/', label: '대시보드', icon: '�' },
  { href: '/students', label: '학생 관리', icon: '👨‍🎓' },
  { href: '/courses', label: '과목 목록', icon: '📚' },
  { href: '/submissions', label: '제출 현황', icon: '📝' },
];

export default function Navbar() {
  // 현재 경로를 가져오는 Next.js 훅
  const pathname = usePathname();

  return (
    <nav className="navbar">
      {/* �고 영역 */}
      <Link href="/" className="navbar-brand">
        � 코드 교육 랩
      </Link>
      {/* 네비게이션 �크 */}
      <ul className="navbar-nav">
        {navItems.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              className={pathname === item.href ? 'active' : ''}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
