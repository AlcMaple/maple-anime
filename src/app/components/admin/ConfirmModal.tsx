import React from 'react';
import { Modal } from '@/ui/Modal';
import { Button } from '@/ui/Button';

interface ConfirmModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    content: string;
    confirmText?: string;
    cancelText?: string;
    confirmVariant?: 'primary' | 'warning' | 'danger' | 'success' | 'info';
    isLoading?: boolean;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    content,
    confirmText = '确认',
    cancelText = '取消',
    confirmVariant = 'primary',
    isLoading = false
}) => {
    const handleConfirm = () => {
        onConfirm();
    };

    const handleCancel = () => {
        if (!isLoading) {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <Modal
            isOpen={isOpen}
            onClose={handleCancel}
            title={title}
            size="md"
            closeOnOverlayClick={!isLoading}
        >
            <div className="p-6">
                <div className="mb-6">
                    <p className="text-gray-700 text-sm leading-relaxed">
                        {content}
                    </p>
                </div>

                <div className="flex justify-end space-x-3">
                    <Button
                        variant="secondary"
                        onClick={handleCancel}
                        disabled={isLoading}
                    >
                        {cancelText}
                    </Button>
                    <Button
                        variant={confirmVariant}
                        onClick={handleConfirm}
                        disabled={isLoading}
                    >
                        {isLoading ? '处理中...' : confirmText}
                    </Button>
                </div>
            </div>
        </Modal>
    );
};