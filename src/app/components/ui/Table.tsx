import React from 'react';
import { Loading } from './Loading';

interface Column {
    key: string;
    title: string | React.ReactNode;
    width?: string;
}

interface PaginationProps {
    current: number;
    total: number;
    pageSize: number;
    onChange: (page: number) => void;
    onPageSizeChange: (pageSize: number) => void;
}

interface TableProps {
    columns: Column[];
    data: any[];
    pagination?: PaginationProps;
    className?: string;
    loading?: boolean;
}

const Pagination: React.FC<PaginationProps> = ({
    current,
    total,
    pageSize,
    onChange,
    onPageSizeChange
}) => {
    const totalPages = Math.ceil(total / pageSize);
    const startIndex = (current - 1) * pageSize + 1;
    const endIndex = Math.min(current * pageSize, total);

    const getPageNumbers = () => {
        const pages = [];
        const maxVisible = 5;

        if (totalPages <= maxVisible) {
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            if (current <= 3) {
                for (let i = 1; i <= 4; i++) {
                    pages.push(i);
                }
                pages.push('...');
                pages.push(totalPages);
            } else if (current >= totalPages - 2) {
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 3; i <= totalPages; i++) {
                    pages.push(i);
                }
            } else {
                pages.push(1);
                pages.push('...');
                for (let i = current - 1; i <= current + 1; i++) {
                    pages.push(i);
                }
                pages.push('...');
                pages.push(totalPages);
            }
        }

        return pages;
    };

    return (
        <div className="flex items-center justify-between px-6 py-3 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                    显示 {startIndex} 到 {endIndex} 条，共 {total} 条记录
                </span>
            </div>

            <div className="flex items-center space-x-2">
                <button
                    onClick={() => onChange(current - 1)}
                    disabled={current === 1}
                    className="text-gray-900 font-medium px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    上一页
                </button>

                {getPageNumbers().map((page, index) => (
                    <button
                        key={index}
                        onClick={() => typeof page === 'number' && onChange(page)}
                        disabled={page === '...'}
                        className={`text-gray-900 font-medium px-3 py-1 text-sm border rounded ${page === current
                            ? 'bg-blue-500 text-white border-blue-500'
                            : page === '...'
                                ? 'border-transparent cursor-default'
                                : 'border-gray-300 hover:bg-gray-50'
                            }`}
                    >
                        {page}
                    </button>
                ))}

                <button
                    onClick={() => onChange(current + 1)}
                    disabled={current === totalPages}
                    className="text-gray-900 font-medium px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    下一页
                </button>
            </div>
        </div>
    );
};

export const Table: React.FC<TableProps> = ({
    columns,
    data,
    pagination,
    className = '',
    loading = false
}) => {
    return (
        <div className={`bg-white rounded-lg border border-gray-200 overflow-hidden ${className}`}>
            <table className="w-full">
                <thead className="bg-gray-50">
                    <tr>
                        {columns.map((column) => (
                            <th
                                key={column.key}
                                className="px-6 py-3 text-left text-xs font-medium text-gray-900 uppercase tracking-wider"
                                style={{ width: column.width }}
                            >
                                {column.title}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {loading ? (
                        <tr>
                            <td
                                colSpan={columns.length}
                                className="px-6 py-8 text-center"
                            >
                                <Loading
                                    variant='spinner'
                                    size='large'
                                    color='primary'
                                    text='正在加载...'
                                />
                            </td>
                        </tr>
                    ) : data.length === 0 ? (
                        <tr>
                            <td
                                colSpan={columns.length}
                                className="px-6 py-8 text-center text-gray-500"
                            >
                                暂无数据
                            </td>
                        </tr>
                    ) : (
                        data.map((row, index) => (
                            <tr key={index} className="hover:bg-gray-50 transition-colors">
                                {columns.map((column) => (
                                    <td key={column.key} className="px-6 py-4 whitespace-nowrap">
                                        {row[column.key]}
                                    </td>
                                ))}
                            </tr>
                        ))
                    )}
                </tbody>
            </table>

            {pagination && !loading && (
                <Pagination {...pagination} />
            )}
        </div>
    );
};