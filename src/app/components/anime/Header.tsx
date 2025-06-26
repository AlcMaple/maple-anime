'use client';

import Link from 'next/link';

interface HeaderProps {
    onSearchClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onSearchClick }) => {
    return (
        <header className="relative z-10 w-full">
            <div className="backdrop-blur-md bg-white/10 border-b border-white/20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* 左侧 */}
                        <div className="flex items-center">
                            <Link href="/" className="flex items-center space-x-2">
                                <div className="text-2xl font-bold text-white">
                                    Maple Anime
                                </div>
                            </Link>
                        </div>

                        {/* 右侧*/}
                        <div className="flex items-center">
                            <button
                                onClick={onSearchClick}
                                className="p-2 rounded-full text-white hover:bg-white/20 transition-all duration-200"
                                aria-label="搜索"
                            >
                                <svg
                                    className="w-6 h-6"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                                    />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};