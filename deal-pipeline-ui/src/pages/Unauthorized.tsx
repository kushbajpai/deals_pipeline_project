import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function Unauthorized() {
  const { logout } = useAuth();

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', padding: '40px', textAlign: 'center', border: '1px solid #f0ad4e', borderRadius: '8px', backgroundColor: '#fcf8e3' }}>
      <h1 style={{ color: '#8a6d3b' }}>Access Denied</h1>
      <p style={{ color: '#8a6d3b', fontSize: '16px', marginBottom: '20px' }}>
        You don't have permission to access this resource. Your current role doesn't grant access to this section.
      </p>
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <Link 
          to="/deals" 
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#5cb85c', 
            color: 'white', 
            textDecoration: 'none', 
            borderRadius: '4px' 
          }}
        >
          Back to Deals
        </Link>
        <button
          onClick={() => {
            logout();
            window.location.href = '/login';
          }}
          style={{
            padding: '10px 20px',
            backgroundColor: '#d9534f',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
}
