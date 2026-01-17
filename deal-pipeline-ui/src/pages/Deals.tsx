import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dealsAPI } from '../api/deals.api';
import type { Deal } from '../types';

export default function Deals() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDeals = async () => {
      try {
        const dealsData = await dealsAPI.getAll();
        setDeals(dealsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load deals');
      } finally {
        setLoading(false);
      }
    };

    loadDeals();
  }, []);

  if (loading) return <div>Loading deals...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Deals - Table View</h1>
        <Link to="/deals" style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
          Kanban View
        </Link>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#f0f0f0' }}>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>ID</th>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Name</th>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Owner</th>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Stage</th>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Check Size</th>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Status</th>
            <th style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'left' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {deals.map((deal) => (
            <tr key={deal.id}>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>{deal.id}</td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>{deal.name}</td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>{deal.owner}</td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>{deal.stage}</td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>{deal.check_size ? `$${(deal.check_size / 1000000).toFixed(1)}M` : 'N/A'}</td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>{deal.status}</td>
              <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                <Link to={`/deals/${deal.id}`} style={{ color: '#007bff', textDecoration: 'none' }}>
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
