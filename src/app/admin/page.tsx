'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';

interface AnimeSearchResult {
  id: string;
  title: string;
  magnet: string;
}

interface PikPakCredentials {
  username: string;
  password: string;
}

export default function AdminMainPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loginTime, setLoginTime] = useState<string>('');
  const router = useRouter();

  // 动漫搜索相关状态
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<AnimeSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');

  // PikPak配置相关状态
  const [pikpakCredentials, setPikpakCredentials] = useState<PikPakCredentials>({ username: '', password: '' });
  const [savePikpak, setSavePikpak] = useState(false);

  // 检查登录状态
  useEffect(() => {
    const checkAuth = () => {
      const authStatus = localStorage.getItem('adminAuth');
      const loginTimeStr = localStorage.getItem('adminLoginTime');

      if (authStatus === 'true' && loginTimeStr) {
        const loginDate = new Date(loginTimeStr);
        const now = new Date();
        const daysDiff = (now.getTime() - loginDate.getTime()) / (1000 * 3600 * 24);

        if (daysDiff < 7) {
          setIsAuthenticated(true);
          setLoginTime(loginDate.toLocaleString());
          loadPikPakCredentials();
        } else {
          localStorage.removeItem('adminAuth');
          localStorage.removeItem('adminLoginTime');
          router.push('/admin/login');
        }
      } else {
        router.push('/admin/login');
      }
      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  // 加载保存的PikPak账号
  const loadPikPakCredentials = () => {
    const savedUsername = localStorage.getItem('pikpak_username');
    const savedPassword = localStorage.getItem('pikpak_password');

    if (savedUsername && savedPassword) {
      setPikpakCredentials({ username: savedUsername, password: savedPassword });
      setSavePikpak(true);
    }
  };

  // 搜索动漫
  const handleAnimeSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchError('请输入动漫名称');
      return;
    }

    setIsSearching(true);
    setSearchError('');
    setSearchResults([]);

    try {
      const response = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: searchQuery })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setSearchResults(data);

      if (data.length === 0) {
        setSearchError('没有找到相关动漫资源');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : '搜索失败';
      setSearchError(`搜索失败: ${errorMsg}`);
    } finally {
      setIsSearching(false);
    }
  };

  // 下载到PikPak
  const downloadToPikPak = async (magnet: string, title: string) => {
    if (!pikpakCredentials.username || !pikpakCredentials.password) {
      return;
    }
  };

  // 加载中状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-800 text-center">
          <p className="text-xl">验证登录状态...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen p-5 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* 页面头部 */}
        <div className="text-center mb-8 text-gray-800">
          <div className="text-5xl mb-2 font-bold">
            Maple Anime 管理端
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main区域 */}
          <div className="lg:col-span-3 space-y-6">

            {/* 动漫搜索 */}
            {/* <Card title="动漫搜索" variant="section">
              <div className="flex space-x-3 mb-4">
                <Input
                  placeholder="输入动漫名称进行搜索（如：赛马娘）"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAnimeSearch()}
                  className="flex-1"
                />
                <Button
                  variant="primary"
                  onClick={handleAnimeSearch}
                  disabled={isSearching}
                  className=''
                >
                  {isSearching ? '🔄 搜索中...' : '搜索'}
                </Button>
              </div>

              {searchError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                  <span className="text-sm text-red-700">❌ {searchError}</span>
                </div>
              )}

              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                {searchResults.length > 0 ? (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">✅ 找到 {searchResults.length} 个搜索结果：</p>
                    {searchResults.map((anime, index) => (
                      <div key={anime.id} className="bg-white border border-gray-200 rounded-lg p-4">
                        <h4 className="font-medium text-gray-800 mb-2">{anime.title}</h4>
                        <p className="text-xs text-gray-500 mb-3 break-all">
                          磁力链接: {anime.magnet.substring(0, 100)}...
                        </p>
                        <div className="flex space-x-2">
                          <Button
                            variant="success"
                            className="text-xs"
                            onClick={() => downloadToPikPak(anime.magnet, anime.title)}
                          >
                            📥 下载到PikPak
                          </Button>
                          <Button variant="info" className="text-xs">
                            ➕ 添加到管理系统
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">搜索结果将在这里显示...</p>
                )}
              </div>
            </Card> */}
          </div>

          {/* 侧边栏 */}
          <div className="space-y-6">
            {/* PikPak配置 */}
            {/* <Card title="PikPak 配置" variant="sidebar">
              <div className="space-y-3">
                <Input
                  placeholder="PikPak 用户名"
                  value={pikpakCredentials.username}
                  onChange={(e) => setPikpakCredentials(prev => ({ ...prev, username: e.target.value }))}
                  className="text-sm"
                />
                <Input
                  type="password"
                  placeholder="PikPak 密码"
                  value={pikpakCredentials.password}
                  onChange={(e) => setPikpakCredentials(prev => ({ ...prev, password: e.target.value }))}
                  className="text-sm"
                />
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="savePikPak"
                    checked={savePikpak}
                    onChange={(e) => setSavePikpak(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="savePikPak" className="text-xs text-gray-600">
                    保存账号密码
                  </label>
                </div>
              </div>
            </Card> */}
          </div>
        </div>
      </div>
    </div>
  );
}