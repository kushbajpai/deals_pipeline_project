import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import '../styles/Navigation.css';

export const Navigation: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/deals" className="nav-brand-link">
            💼 Deal Pipeline
          </Link>
        </div>

        <div className="nav-links">
          <Link
            to="/deals"
            className={`nav-link ${isActive('/deals') ? 'active' : ''}`}
            title="Kanban view of deals"
          >
            Kanban Board
          </Link>

          <Link
            to="/deals-table"
            className={`nav-link ${isActive('/deals-table') ? 'active' : ''}`}
            title="Table view of all deals"
          >
            All Deals
          </Link>

          {user.role.toLowerCase() === 'admin' && (
            <Link
              to="/users"
              className={`nav-link ${isActive('/users') ? 'active' : ''}`}
              title="Manage user roles and permissions"
            >
              👥 Users
            </Link>
          )}
        </div>

        <div className="nav-user">
          <div className="user-info">
            <span className="user-role" title={`Role: ${user.role}`}>
              {user.role.toUpperCase()}
            </span>
            <span className="user-email">{user.email}</span>
          </div>
          <button
            className="nav-logout"
            onClick={logout}
            title="Logout"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};
