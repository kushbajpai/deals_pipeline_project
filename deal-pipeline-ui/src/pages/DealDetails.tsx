import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { dealsAPI } from '../api/deals.api';
import type { Deal as DealType, Activity } from '../types';
import ICMemoEditor from '../components/ICMemo/ICMemoEditor';
import '../styles/DealDetails.css';

export default function DealDetails() {
  const { id } = useParams<{ id: string }>();
  const [deal, setDeal] = useState<DealType | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'memo' | 'activities'>('overview');

  useEffect(() => {
    const loadDeal = async () => {
      try {
        if (!id) {
          setError('Deal ID not provided');
          return;
        }
        const dealData = await dealsAPI.getById(parseInt(id, 10));
        setDeal(dealData);

        // Load activities
        const activitiesData = await dealsAPI.getActivities(parseInt(id, 10));
        setActivities(activitiesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load deal');
      } finally {
        setLoading(false);
      }
    };

    loadDeal();
  }, [id]);

  if (loading) return <div>Loading deal details...</div>;
  if (error) return <div style={{ color: 'red' }}>Error: {error}</div>;
  if (!deal) return <div>Deal not found</div>;

  const dealId = parseInt(id || '0', 10);

  return (
    <div className="deal-details-page">
      <Link to="/deals" style={{ color: '#007bff', textDecoration: 'none', marginBottom: '20px', display: 'block' }}>
        ← Back to Pipeline
      </Link>
      
      <div className="deal-details-header-section">
        <h1>{deal.name}</h1>
        <div className="deal-status-badges">
          <span className={`stage-badge stage-${deal.stage.toLowerCase().replace(/\s+/g, '-')}`}>
            {deal.stage}
          </span>
          <span className={`status-badge status-${deal.status}`}>
            {deal.status}
          </span>
        </div>
      </div>

      <div className="deal-tabs">
        <button
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-button ${activeTab === 'memo' ? 'active' : ''}`}
          onClick={() => setActiveTab('memo')}
        >
          IC Memo
        </button>
        <button
          className={`tab-button ${activeTab === 'activities' ? 'active' : ''}`}
          onClick={() => setActiveTab('activities')}
        >
          Activity Log ({activities.length})
        </button>
      </div>

      <div className="deal-tabs-content">
        {activeTab === 'overview' && (
          <div className="tab-content">
            <div style={{ border: '1px solid #ddd', padding: '20px', borderRadius: '8px', backgroundColor: '#fff' }}>
              <h2>Deal Information</h2>
              <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                <div>
                  <p><strong>ID:</strong> {deal.id}</p>
                  <p><strong>Owner:</strong> {deal.owner}</p>
                  <p><strong>Stage:</strong> {deal.stage}</p>
                  <p><strong>Status:</strong> <span style={{ backgroundColor: deal.status === 'active' ? '#c8e6c9' : '#ffccbc', color: deal.status === 'active' ? '#2e7d32' : '#d84315', padding: '4px 8px', borderRadius: '4px' }}>{deal.status}</span></p>
                </div>
                <div>
                  {deal.company_url && (
                    <p><strong>Company URL:</strong> <a href={deal.company_url} target="_blank" rel="noopener noreferrer">{deal.company_url}</a></p>
                  )}
                  {deal.round && (
                    <p><strong>Round:</strong> {deal.round}</p>
                  )}
                  {deal.check_size && (
                    <p><strong>Check Size:</strong> ${(deal.check_size / 1000000).toFixed(1)}M</p>
                  )}
                </div>
              </div>
              <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #ddd' }}>
                <h3>Timeline</h3>
                {deal.created_at && (
                  <p><strong>Created:</strong> {new Date(deal.created_at).toLocaleString()}</p>
                )}
                {deal.updated_at && (
                  <p><strong>Last Updated:</strong> {new Date(deal.updated_at).toLocaleString()}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'memo' && (
          <div className="tab-content">
            {dealId && <ICMemoEditor dealId={dealId} />}
          </div>
        )}

        {activeTab === 'activities' && (
          <div className="tab-content">
            <div className="activities-list">
              {activities.length > 0 ? (
                activities.map((activity) => (
                  <div key={activity.id} className="activity-item">
                    <div className="activity-header">
                      <span className="activity-type">{activity.activity_type}</span>
                      <span className="activity-date">
                        {new Date(activity.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="activity-description">{activity.description}</p>
                    {activity.old_value && activity.new_value && (
                      <div className="activity-changes">
                        <span className="old-value">From: <strong>{activity.old_value}</strong></span>
                        <span className="new-value">To: <strong>{activity.new_value}</strong></span>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="no-activities">No activities yet</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
