import React, { useState } from 'react';
import type { User } from '../../types';
import '../../styles/UserRow.css';

interface UserRowProps {
  user: User;
  onRoleChange: (userId: number, newRole: string) => Promise<void>;
  onToggleActive: (userId: number, isActive: boolean) => Promise<void>;
  onDelete: (userId: number) => Promise<void>;
}

const ROLE_INFO = {
  admin: {
    label: 'Admin',
    description: 'Full access to manage users and all operations',
    color: '#dc3545', // Red
  },
  analyst: {
    label: 'Analyst',
    description: 'Can create/edit deals and IC memos',
    color: '#007bff', // Blue
  },
  partner: {
    label: 'Partner',
    description: 'Can comment, vote, and approve/decline deals',
    color: '#28a745', // Green
  },
  user: {
    label: 'User',
    description: 'Standard user with limited access',
    color: '#6c757d', // Gray
  },
};

export const UserRow: React.FC<UserRowProps> = ({
  user,
  onRoleChange,
  onToggleActive,
  onDelete,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRoleDropdown, setShowRoleDropdown] = useState(false);

  const handleRoleChange = async (newRole: string) => {
    try {
      setIsLoading(true);
      setError(null);
      console.log(`Changing role for user ${user.id} from ${user.role} to ${newRole}`);
      await onRoleChange(user.id, newRole);
      setShowRoleDropdown(false);
      console.log('Role changed successfully');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to update role';
      setError(errorMsg);
      console.error('Error changing role:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleActive = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await onToggleActive(user.id, !user.is_active);
    } catch (err) {
      setError('Failed to update status');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete ${user.email}?`)) {
      try {
        setIsLoading(true);
        setError(null);
        await onDelete(user.id);
      } catch (err) {
        setError('Failed to delete user');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const roleInfo = ROLE_INFO[user.role as keyof typeof ROLE_INFO] || ROLE_INFO.user;
  const userCreatedDate = new Date(user.created_at).toLocaleDateString();

  return (
    <div className="user-row">
      <div className="user-row-main">
        <div className="user-info">
          <h3 className="user-email">{user.email}</h3>
          {user.full_name && <p className="user-name">{user.full_name}</p>}
          <p className="user-joined">Joined {userCreatedDate}</p>
        </div>

        <div className="user-role">
          <div className="role-badge" style={{ borderColor: roleInfo.color }}>
            <div className="role-dot" style={{ backgroundColor: roleInfo.color }}></div>
            <span className="role-label">{roleInfo.label}</span>
          </div>
          <p className="role-description">{roleInfo.description}</p>
        </div>

        <div className="user-status">
          <div className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
            {user.is_active ? '✓ Active' : '○ Inactive'}
          </div>
        </div>

        <div className="user-actions">
          <div className="role-change-container">
            <button
              className="btn-role-change"
              onClick={() => setShowRoleDropdown(!showRoleDropdown)}
              disabled={isLoading}
              title="Change user role"
            >
              Change Role ▼
            </button>
            {showRoleDropdown && (
              <div className="role-dropdown">
                {(['admin', 'analyst', 'partner'] as const).map((role) => (
                  <div
                    key={role}
                    className={`role-option ${user.role === role ? 'selected' : ''}`}
                    onClick={() => {
                      if (user.role !== role) {
                        handleRoleChange(role);
                      } else {
                        setShowRoleDropdown(false);
                      }
                    }}
                  >
                    {ROLE_INFO[role].label}
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            className={`btn-toggle ${user.is_active ? 'deactivate' : 'activate'}`}
            onClick={handleToggleActive}
            disabled={isLoading}
            title={user.is_active ? 'Deactivate user' : 'Activate user'}
          >
            {user.is_active ? 'Deactivate' : 'Activate'}
          </button>

          <button
            className="btn-delete"
            onClick={handleDelete}
            disabled={isLoading}
            title="Delete user"
          >
            Delete
          </button>
        </div>
      </div>

      {error && <div className="user-row-error">{error}</div>}
    </div>
  );
};
