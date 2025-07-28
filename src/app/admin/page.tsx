'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { Button } from '@/ui/Button';
import { Table } from '@/ui/Table';
import { Search } from '@/ui/Search';
import { message } from '@/ui/Message';
import { Loading } from '@/ui/Loading';

import { AddAnimeModal } from '@/components/admin/AddAnimeModal';
import { PikPakConfigModal } from '@/components/admin/PikPakConfigModal';
import { CalendarModal } from '@/components/admin/CalendarModal';
import { EditAnimeModal } from '@/components/admin/EditAnimeModal';
import { EpisodeManagementModal } from '@/components/admin/EpisodeManagementModal';
import { UpdateAnimeModal } from '@/components/admin/UpdateAnimeModal';
import { DeleteAnimeModal } from '@/components/admin/DeleteAnimeModal';
import { ConfirmModal } from '@/components/admin/ConfirmModal';

import { pikpakApi } from '@/services/pikpak';
import { AnimeItem } from '@/services/types';

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

  // 搜索状态
  const [searchQuery, setSearchQuery] = useState('');

  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  // 模态框状态
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isPikPakConfigOpen, setIsPikPakConfigOpen] = useState(false);
  const [isCalendarModalOpen, setIsCalendarModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isSyncConfirmOpen, setIsSyncConfirmOpen] = useState(false);

  // 当前编辑的动漫
  const [currentEditAnime, setCurrentEditAnime] = useState<AnimeItem | null>(null);

  // 动漫列表状态
  const [animeList, setAnimeList] = useState<AnimeItem[]>([]);
  const [isLoadingAnimes, setIsLoadingAnimes] = useState(false);

  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
  const [currentUpdateAnime, setCurrentUpdateAnime] = useState<AnimeItem | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [currentDeleteAnime, setCurrentDeleteAnime] = useState<AnimeItem | null>(null);

  // 加载动漫列表
  const loadAnimeList = async () => {
    const pikpakUsername = localStorage.getItem('pikpak_username');
    const pikpakPassword = localStorage.getItem('pikpak_password');

    if (!pikpakUsername || !pikpakPassword) {
      message.error('请先配置PikPak账号信息');
      return;
    }

    setIsLoadingAnimes(true);
    try {
      const response = await pikpakApi.getAnimeList();
      console.log("加载动漫列表数据：", response);


      if (response.code == 200) {
        setAnimeList(response.data);
        message.success(`成功加载 ${response.data.length} 个动漫`);
      } else {
        message.error('加载动漫列表失败');
      }
    } catch (error) {
      console.error('加载动漫列表失败:', error);
    } finally {
      setIsLoadingAnimes(false);
    }
  };

  // 编辑保存完成后刷新列表
  const handleEditSave = () => {
    loadAnimeList();
  };

  // 获取动漫列表
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      loadAnimeList();
    }
  }, [isAuthenticated, isLoading]);

  // 管理集数状态
  const [isEpisodeModalOpen, setIsEpisodeModalOpen] = useState(false);
  const [currentManageAnime, setCurrentManageAnime] = useState<{ id: string; title: string } | null>(null);


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
    setIsPikPakConfigOpen(true);
  };

  const handlePikPakConfigSave = (config: any) => {
    console.log('PikPak配置已保存:', config);
  };

  const handleCurrentSeason = () => {
    setIsCalendarModalOpen(true);
  };

  const [refreshIsLoading, setRefreshIsLoading] = useState(false);

  // 同步数据
  const refreshData = async () => {
    const pikpakUsername = localStorage.getItem('pikpak_username');
    const pikpakPassword = localStorage.getItem('pikpak_password');

    if (!pikpakUsername || !pikpakPassword) {
      message.error('请先配置PikPak账号信息');
      return;
    }

    setRefreshIsLoading(true);

    try {
      const response = await pikpakApi.syncData({ username: pikpakUsername, password: pikpakPassword });

      if (response.success) {
        message.success('同步数据成功');
      } else {
        message.error('同步数据失败');
      }
    } catch (error) {
      console.error('同步数据失败:', error);
    } finally {
      setRefreshIsLoading(false);
    }
  }

  const synData = () => {
    setIsSyncConfirmOpen(true);
    // refreshData();
  };

  // 确认同步
  const confirmSyncData = () => {
    setIsSyncConfirmOpen(false);
    refreshData();
  };

  const handleSearch = () => {
    console.log('搜索:', searchQuery);
    setCurrentPage(1); // 搜索时重置到第一页
  };

  // 表格操作按钮
  const handleEdit = (id: string) => {
    const anime = animeList.find(item => item.id === id);
    if (anime) {
      console.log("当前的动漫数据：", anime);

      setCurrentEditAnime(anime);
      setIsEditModalOpen(true);
    }
  };

  const handleManage = (id: string) => {
    const anime = animeList.find(item => item.id === id);
    if (anime) {
      setCurrentManageAnime({ id: anime.id, title: anime.title });
      setIsEpisodeModalOpen(true);
    }
  };

  const handleUpdate = (id: string) => {
    console.log("更新动漫的 id：", id);

    const anime = animeList.find(item => item.id === id);
    if (anime) {
      setCurrentUpdateAnime(anime);
      setIsUpdateModalOpen(true);
    }
  };

  const handleUpdateComplete = () => {
    // 更新完成后刷新动漫列表
    loadAnimeList();
    message.success('动漫更新完成');
  };

  const handleDelete = (id: string) => {
    const anime = animeList.find(item => item.id === id);
    if (anime) {
      setCurrentDeleteAnime(anime);
      setIsDeleteModalOpen(true);
    }
  };

  const handleDeleteComplete = () => {
    // 删除完成后重新加载动漫列表
    loadAnimeList(); // 或者调用你现有的刷新数据方法
    message.success('动漫删除完成');
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
                  onClick={synData}
                >
                  同步
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
              loading={isLoadingAnimes}
            />
          </div>
        </div>

        {/* 同步数据遮罩 */}
        {refreshIsLoading && (
          <div className="absolute inset-0 bg-white/90 flex items-center justify-center z-10">
            <div className="text-center">
              <Loading
                variant="spinner"
                size="large"
                color="primary"
                text="正在同步数据，此过程可能需要几分钟时间，请耐心等待..."
              />
            </div>
          </div>
        )}

        {/* 添加动漫模态框 */}
        <AddAnimeModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onAddAnime={handleAddAnimeToSystem}
        />

        {/* PikPak配置模态框 */}
        <PikPakConfigModal
          isOpen={isPikPakConfigOpen}
          onClose={() => setIsPikPakConfigOpen(false)}
          onSave={handlePikPakConfigSave}
        />

        {/* 当季新番模态框 */}
        <CalendarModal
          isOpen={isCalendarModalOpen}
          onClose={() => setIsCalendarModalOpen(false)}
        />

        {/* 编辑动漫模态框 */}
        <EditAnimeModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          anime={currentEditAnime}
          onSave={handleEditSave}
        />

        {/* 集数管理模态框 */}
        <EpisodeManagementModal
          isOpen={isEpisodeModalOpen}
          onClose={() => {
            setIsEpisodeModalOpen(false);
            setCurrentManageAnime(null);
          }}
          animeId={currentManageAnime?.id || ''}
          animeTitle={currentManageAnime?.title || ''}
        />

        <UpdateAnimeModal
          isOpen={isUpdateModalOpen}
          onClose={() => {
            setIsUpdateModalOpen(false);
            setCurrentUpdateAnime(null);
          }}
          onUpdateComplete={handleUpdateComplete}
          currentAnime={currentUpdateAnime}
        />

        <DeleteAnimeModal
          isOpen={isDeleteModalOpen}
          onClose={() => {
            setIsDeleteModalOpen(false);
            setCurrentDeleteAnime(null);
          }}
          onDeleteComplete={handleDeleteComplete}
          anime={currentDeleteAnime}
        />

        {/* 确认弹窗 */}
        <ConfirmModal
          isOpen={isSyncConfirmOpen}
          onClose={() => setIsSyncConfirmOpen(false)}
          onConfirm={confirmSyncData}
          title="确认同步数据"
          content="同步数据操作将会从PikPak服务器获取最新的动漫文件信息，此过程可能需要几分钟时间。确定要继续吗？"
          confirmText="开始同步"
          confirmVariant="success"
          isLoading={refreshIsLoading}
        />
      </div>
    </div>
  );
}