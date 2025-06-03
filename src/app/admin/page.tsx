'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Table } from '../components/ui/Table';
import { Search } from '../components/ui/Search';
import { AddAnimeModal } from '../components/admin/AddAnimeModal';

interface AnimeItem {
  id: string;
  title: string;
  status: '完结' | '连载';
}

interface AnimeSearchResult {
  id: string;
  title: string;
  magnet: string;
}

export default function AdminMainPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loginTime, setLoginTime] = useState<string>('');
  const router = useRouter();

  // 静态模拟动漫数据
  const [animeList, setAnimeList] = useState<AnimeItem[]>([
    { id: '1', title: '小市民系列第一季', status: '完结' },
    { id: '2', title: '小市民系列第二季', status: '连载' },
    { id: '3', title: '药屋少女第一季', status: '完结' },
    { id: '4', title: '药屋少女第二季', status: '连载' },
    { id: '5', title: '间谍过家家第一季', status: '完结' },
    { id: '6', title: '间谍过家家第二季', status: '连载' },
    { id: '7', title: '鬼灭之刃第一季', status: '完结' },
    { id: '8', title: '鬼灭之刃第二季', status: '完结' },
    { id: '9', title: '鬼灭之刃第三季', status: '连载' },
    { id: '10', title: '进击的巨人第一季', status: '完结' },
    { id: '11', title: '进击的巨人第二季', status: '完结' },
    { id: '12', title: '进击的巨人第三季', status: '完结' },
    { id: '13', title: '一拳超人第一季', status: '完结' },
    { id: '14', title: '一拳超人第二季', status: '完结' },
    { id: '15', title: '咒术回战第一季', status: '完结' },
    { id: '16', title: '咒术回战第二季', status: '连载' },
  ]);

  // 搜索状态
  const [searchQuery, setSearchQuery] = useState('');

  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  // 模态框状态
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // 下载状态
  const [hasDownloading, setHasDownloading] = useState(false);

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

  // 添加动漫
  const handleAddAnimeToSystem = (anime: AnimeSearchResult) => {
    setIsAddModalOpen(false);
  };


  // 操作按钮处理函数
  const handleAddAnime = () => {
    setIsAddModalOpen(true);
  };

  const handlePikpakConfig = () => {
    console.log('PikPak配置');
  };

  const handleCurrentSeason = () => {
    console.log('当季新番');
  };

  const handleImport = () => {
    console.log('导入');
  };

  const handleExport = () => {
    console.log('导出');
  };

  const handleSearch = () => {
    console.log('搜索:', searchQuery);
    setCurrentPage(1); // 搜索时重置到第一页
  };

  // 表格操作按钮
  const handleEdit = (id: string) => {
    console.log('编辑:', id);
  };

  const handleManage = (id: string) => {
    console.log('管理:', id);
  };

  const handleUpdate = (id: string) => {
    console.log('更新:', id);
  };

  const handleDelete = (id: string) => {
    console.log('删除:', id);
    const newList = animeList.filter(item => item.id !== id);
    setAnimeList(newList);

    // 如果删除后当前页没有数据且不是第一页，则回到前一页
    const filteredCount = newList.filter(item =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase())
    ).length;
    const totalPages = Math.ceil(filteredCount / pageSize);
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  };

  // 下载按钮
  const handleDownloadCenter = () => {
    console.log('下载中心');
  };

  // 表格列定义
  const columns = [
    { key: 'title', title: '标题', width: '50%' },
    { key: 'status', title: '状态', width: '20%' },
    { key: 'actions', title: '操作', width: '30%' },
  ];

  // 处理表格数据，添加操作按钮
  const filteredData = animeList.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 分页计算
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentPageData = filteredData.slice(startIndex, endIndex);

  const tableData = currentPageData.map(item => ({
    title: <span className="text-gray-900 font-medium">{item.title}</span>,
    status: (
      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${item.status === '完结'
        ? 'bg-gray-100 text-gray-800'
        : 'bg-green-100 text-green-800'
        }`}>
        {item.status}
      </span>
    ),
    actions: (
      <div className="flex space-x-2">
        <Button
          variant="info"
          className="text-xs px-3 py-1"
          onClick={() => handleEdit(item.id)}
        >
          编辑
        </Button>
        <Button
          variant="primary"
          className="text-xs px-3 py-1"
          onClick={() => handleManage(item.id)}
        >
          管理
        </Button>
        {item.status === '连载' && (
          <Button
            variant="warning"
            className="text-xs px-3 py-1"
            onClick={() => handleUpdate(item.id)}
          >
            更新
          </Button>
        )}
        <Button
          variant="danger"
          className="text-xs px-3 py-1"
          onClick={() => handleDelete(item.id)}
        >
          删除
        </Button>
      </div>
    ),
  }));

  // 分页配置
  const pagination = {
    current: currentPage,
    total: filteredData.length,
    pageSize: pageSize,
    onChange: (page: number) => {
      setCurrentPage(page);
    },
    onPageSizeChange: (newPageSize: number) => {
      setPageSize(newPageSize);
      setCurrentPage(1); // 重置到第一页
    }
  };

  // 模拟下载状态
  useEffect(() => {
    // 模拟有下载任务的情况
    setHasDownloading(true);
  }, []);

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
          <h1 className="text-5xl mb-2 font-bold">
            Maple Anime 管理端
          </h1>
        </div>

        {/* 主内容区域 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {/* 操作栏 */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-center">
              {/* 左侧按钮组 */}
              <div className="flex space-x-3">
                <Button
                  variant="primary"
                  onClick={handleAddAnime}
                >
                  添加动漫
                </Button>
                <Button
                  variant="info"
                  onClick={handlePikpakConfig}
                >
                  PikPak配置
                </Button>
                <Button
                  variant="warning"
                  onClick={handleCurrentSeason}
                >
                  当季新番
                </Button>
                <Button
                  variant="success"
                  onClick={handleImport}
                >
                  导入
                </Button>
                <Button
                  variant="success"
                  onClick={handleExport}
                >
                  导出
                </Button>
              </div>

              {/* 右侧按钮组 */}
              <Search
                placeholder="搜索动漫..."
                value={searchQuery}
                onChange={(value) => {
                  setSearchQuery(value);
                  setCurrentPage(1);
                }}
                onSearch={handleSearch}
              />
            </div>
          </div>

          {/* 表格区域 */}
          <div className="p-6">
            <Table
              columns={columns}
              data={tableData}
              pagination={pagination}
            />
          </div>
        </div>

        {/* 下载按钮 */}
        {hasDownloading && (
          <button
            onClick={handleDownloadCenter}
            className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 z-50 w-16 h-16 text-3xl text-center"
            title="下载中心"
          >📥</button>
        )}

        {/* 动漫模态框 */}
        <AddAnimeModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onAddAnime={handleAddAnimeToSystem}
        />

      </div>
    </div>
  );
}