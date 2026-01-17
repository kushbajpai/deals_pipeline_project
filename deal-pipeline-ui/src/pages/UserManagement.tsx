import React, { useState } from 'react';
import type { User } from '../types';
import { usersAPI } from '../api/users.api';
import { UserRow } from '../components/Users/UserRow';
import '../styles/UserManagement.css';

export default function UserManagement() {
  const [users, setUsers] = React.useState<User[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | 'admin' | 'analyst' | 'partner'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('all');

  React.useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      console.log('Loading users...');
      const data = await usersAPI.getAll();
      console.log('Users loaded:', data);
      if (Array.isArray(data)) {
        setUsers(data);
      } else {
        console.error('Invalid response format:', data);
        setError('Invalid response format from server');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load users';
      console.error('Error loading users:', err);
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      const updatedUser = await usersAPI.updateRole(userId, newRole as "admin" | "analyst" | "partner");
      setUsers(users.map(u => u.id === userId ? updatedUser : u));
    } catch (err) {
      console.error('Failed to update role:', err);
      throw err;
    }
  };

  const handleToggleActive = async (userId: number, isActive: boolean) => {
    try {
      const updatedUser = await usersAPI.toggleActive(userId, isActive);
      setUsers(users.map(u => u.id === userId ? updatedUser : u));
    } catch (err) {
      console.error('Failed to toggle active status:', err);
      throw err;
    }
  };

  const handleDelete = async (userId: number) => {
    try {
      await usersAPI.deleteUser(userId);
      setUsers(users.filter(u => u.id !== userId));
    } catch (err) {
      console.error('Failed to delete user:', err);
      throw err;
    }
  };

  // Filter users based on search and filter criteria
  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.full_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    
    const matchesStatus = 
      statusFilter === 'all' || 
      (statusFilter === 'active' && user.is_active) ||
      (statusFilter === 'inactive' && !user.is_active);

    return matchesSearch && matchesRole && matchesStatus;
  });

  const roleStats = {
    admin: users.filter(u => u.role === 'admin').length,
    analyst: users.filter(u => u.role === 'analyst').length,
    partner: users.filter(u => u.role === 'partner').length,
  };

  return (
    <div className="user-management-container">
      <div className="user-management-header">
        <div>
          <h1>User Management</h1>
          <p className="subtitle">Manage user roles and permissions across the platform</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{users.length}</div>
          <div className="stat-label">Total Users</div>
        </div>
        <div className="stat-card admin">
          <div className="stat-number">{roleStats.admin}</div>
          <div className="stat-label">Admins</div>
          <p className="stat-desc">Full system access</p>
        </div>
        <div className="stat-card analyst">
          <div className="stat-number">{roleStats.analyst}</div>
          <div className="stat-label">Analysts</div>
          <p className="stat-desc">Deal management</p>
        </div>
        <div className="stat-card partner">
          <div className="stat-number">{roleStats.partner}</div>
          <div className="stat-label">Partners</div>
          <p className="stat-desc">Review & approval</p>
        </div>
      </div>

      {/* Filters Section */}
      <div className="filters-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by email or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <div className="filter-item">
            <label htmlFor="role-filter">Role:</label>
            <select
              id="role-filter"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as any)}
              className="filter-select"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="analyst">Analyst</option>
              <option value="partner">Partner</option>
            </select>
          </div>

          <div className="filter-item">
            <label htmlFor="status-filter">Status:</label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="filter-select"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <button
            className="btn-refresh"
            onClick={loadUsers}
            disabled={isLoading}
            title="Refresh user list"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Users List */}
      <div className="users-list-section">
        <div className="users-list-header">
          <h2>Registered Users ({filteredUsers.length})</h2>
          <p className="results-info">
            {filteredUsers.length} of {users.length} users shown
          </p>
        </div>

        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)} className="btn-close">✕</button>
          </div>
        )}

        {isLoading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading users...</p>
          </div>
        )}

        {!isLoading && filteredUsers.length === 0 && (
          <div className="empty-state">
            <p>No users found</p>
            {searchTerm || roleFilter !== 'all' || statusFilter !== 'all' ? (
              <p className="empty-state-hint">Try adjusting your filters</p>
            ) : (
              <p className="empty-state-hint">Start by adding new users to the system</p>
            )}
          </div>
        )}

        {!isLoading && filteredUsers.length > 0 && (
          <div className="users-list">
            {filteredUsers.map(user => (
              <UserRow
                key={user.id}
                user={user}
                onRoleChange={handleRoleChange}
                onToggleActive={handleToggleActive}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>

      {/* Role Guide */}
      <div className="role-guide">
        <h3>Role Permissions Guide</h3>
        <div className="role-guide-grid">
          <div className="role-guide-card admin">
            <h4>👑 Admin</h4>
            <ul>
              <li>✓ Manage all users</li>
              <li>✓ Change user roles</li>
              <li>✓ Full access to deals</li>
              <li>✓ Create IC memos</li>
              <li>✓ Comment & vote</li>
            </ul>
          </div>
          <div className="role-guide-card analyst">
            <h4>📊 Analyst</h4>
            <ul>
              <li>✓ Create & edit deals</li>
              <li>✓ Create IC memos</li>
              <li>✓ View all deals</li>
              <li>✓ Comment & vote</li>
              <li>✗ Cannot manage users</li>
            </ul>
          </div>
          <div className="role-guide-card partner">
            <h4>🤝 Partner</h4>
            <ul>
              <li>✓ View deals</li>
              <li>✓ Comment on deals</li>
              <li>✓ Vote on decisions</li>
              <li>✓ Approve/decline deals</li>
              <li>✗ Cannot create deals</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
