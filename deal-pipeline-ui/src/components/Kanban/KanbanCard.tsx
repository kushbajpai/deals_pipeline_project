import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useNavigate } from 'react-router-dom';
import type { Deal } from '../../types';

interface KanbanCardProps {
  deal: Deal;
  isDragging?: boolean;
}

export default function KanbanCard({ deal, isDragging }: KanbanCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: deal.id });
  const navigate = useNavigate();

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isSortableDragging ? 0.5 : 1,
  };

  const formattedCheckSize = deal.check_size
    ? `$${(deal.check_size / 1000000).toFixed(1)}M`
    : 'N/A';

  return (
    <div
      ref={setNodeRef}
      style={{
        ...style,
        backgroundColor: 'white',
        padding: '12px',
        borderRadius: '4px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        cursor: isDragging || isSortableDragging ? 'grabbing' : 'grab',
        border: '2px solid transparent',
        transition: 'border-color 0.2s',
      }}
      {...attributes}
      {...listeners}
      onClick={() => navigate(`/deals/${deal.id}`)}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = '#0288d1';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'transparent';
      }}
    >
      <div style={{ fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>
        {deal.name}
      </div>
      
      {deal.company_url && (
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
          🔗 {deal.company_url}
        </div>
      )}

      <div style={{ fontSize: '12px', color: '#999', marginBottom: '8px' }}>
        Owner: {deal.owner}
      </div>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '12px',
        paddingTop: '8px',
        borderTop: '1px solid #eee',
      }}>
        <span>Round: {deal.round || 'N/A'}</span>
        <span style={{ fontWeight: 'bold', color: '#0288d1' }}>
          {formattedCheckSize}
        </span>
      </div>

      {deal.status && (
        <div style={{
          marginTop: '8px',
          display: 'inline-block',
          backgroundColor: deal.status === 'active' ? '#c8e6c9' : '#ffccbc',
          color: deal.status === 'active' ? '#2e7d32' : '#d84315',
          padding: '2px 8px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 'bold',
        }}>
          {deal.status}
        </div>
      )}
    </div>
  );
}
