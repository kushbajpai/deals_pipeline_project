import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { Navigation } from './components/Navigation';
import Login from './pages/Login';
import Kanban from './pages/Kanban';
import Deals from './pages/Deals';
import DealDetails from './pages/DealDetails';
import UserManagement from './pages/UserManagement';
import Unauthorized from './pages/Unauthorized';
import './App.css';

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Navigation />
        <Routes>
          <Route path="/" element={<Navigate to="/deals" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/unauthorized" element={<Unauthorized />} />

          <Route path="/deals" element={
            <ProtectedRoute roles={["ADMIN","ANALYST","PARTNER"]}>
              <Kanban />
            </ProtectedRoute>
          } />

          <Route path="/deals-table" element={
            <ProtectedRoute roles={["ADMIN","ANALYST","PARTNER"]}>
              <Deals />
            </ProtectedRoute>
          } />

          <Route path="/deals/:id" element={
            <ProtectedRoute roles={["ADMIN","ANALYST","PARTNER"]}>
              <DealDetails />
            </ProtectedRoute>
          } />

          <Route path="/users" element={
            <ProtectedRoute roles={["ADMIN"]}>
              <UserManagement />
            </ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </Router>
  );
}