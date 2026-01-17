import { useDroppable } from '@dnd-kit/core';
import type { Deal, DealStage } from '../../types';
import KanbanCard from './KanbanCard';

interface KanbanColumnProps {
  stage: DealStage;
  deals: Deal[];
  activeId: number | null;
}

export default function KanbanColumn({ stage, deals, activeId }: KanbanColumnProps) {
  const { setNodeRef } = useDroppable({
    id: stage,
  });

  const stageColors: Record<DealStage, { bg: string; header: string }> = {
    Sourced: { bg: '#e8f4f8', header: '#0288d1' },
    Screen: { bg: '#f3e5f5', header: '#7b1fa2' },
    Diligence: { bg: '#fff3e0', header: '#f57c00' },
    IC: { bg: '#f1f8e9', header: '#689f38' },
    Invested: { bg: '#fce4ec', header: '#c2185b' },
    Passed: { bg: '#e0f2f1', header: '#00796b' },
  };

  const color = stageColors[stage];

  return (
    <div
      ref={setNodeRef}
      style={{
        backgroundColor: color.bg,
        borderRadius: '8px',
        padding: '16px',
        flex: '0 0 calc(100% / 6)',
        minWidth: '300px',
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - 140px)',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      }}
    >
      <div style={{
        backgroundColor: color.header,
        color: 'white',
        padding: '12px',
        borderRadius: '4px',
        marginBottom: '16px',
        fontWeight: 'bold',
        flex: '0 0 auto',
      }}>
        {stage}
        <span style={{ float: 'right', fontSize: '12px' }}>
          {deals.length}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: '1', overflowY: 'hidden' }}>
        {deals.map(deal => (
          <KanbanCard
            key={deal.id}
            deal={deal}
            isDragging={activeId === deal.id}
          />
        ))}
      </div>
    </div>
  );
}
