import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DndContext,
  closestCorners,
  type DragEndEvent,
  DragOverlay,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { dealsAPI } from '../api/deals.api';
import type { Deal, DealStage } from '../types';
import KanbanCard from '../components/Kanban/KanbanCard';
import KanbanColumn from '../components/Kanban/KanbanColumn';

const STAGES: DealStage[] = ['Sourced', 'Screen', 'Diligence', 'IC', 'Invested', 'Passed'];

export default function Kanban() {
  const [deals, setDeals] = useState<Record<DealStage, Deal[]>>({
    Sourced: [],
    Screen: [],
    Diligence: [],
    IC: [],
    Invested: [],
    Passed: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeId, setActiveId] = useState<number | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadDeals();
  }, []);

  const loadDeals = async () => {
    try {
      setLoading(true);
      const allDeals: Deal[] = [];
      
      // Load deals from each stage
      for (const stage of STAGES) {
        try {
          const stageDeals = await dealsAPI.getByStage(stage);
          allDeals.push(...stageDeals);
        } catch (err) {
          console.warn(`Failed to load deals for stage ${stage}:`, err);
        }
      }

      // Group deals by stage
      const groupedDeals = STAGES.reduce((acc, stage) => {
        acc[stage] = allDeals.filter(deal => deal.stage === stage);
        return acc;
      }, {} as Record<DealStage, Deal[]>);

      setDeals(groupedDeals);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load deals');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const dealId = active.id as number;
    const overStage = over.id as DealStage;

    // Find which stage the deal is currently in
    const activeStage = Object.entries(deals).find(([, stageDeal]) =>
      stageDeal.some(d => d.id === dealId)
    )?.[0] as DealStage | undefined;

    if (!activeStage) return;

    const deal = deals[activeStage].find(d => d.id === dealId);
    if (!deal || deal.stage === overStage) return;

    try {
      // Update deal stage on backend
      const response = await dealsAPI.moveToStage(deal.id, { stage: overStage });
      
      // Log the activity message
      if (response.activity) {
        console.log(`✓ Activity: ${response.activity.description}`);
      }

      // Update local state
      setDeals(prev => {
        const updated = { ...prev };
        updated[activeStage] = updated[activeStage].filter(d => d.id !== deal.id);
        updated[overStage] = [...updated[overStage], { ...deal, stage: overStage }];
        return updated;
      });
    } catch (err) {
      console.error('Failed to move deal:', err);
      setError('Failed to move deal. Please try again.');
    }
  };

  const handleDragStart = (event: any) => {
    setActiveId(event.active.id as number);
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading pipeline...</div>;

  return (
    <DndContext
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100%' }}>
        <div style={{ padding: '20px', backgroundColor: '#f5f5f5', borderBottom: '1px solid #ddd', flex: '0 0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 style={{ margin: '0' }}>Deal Pipeline</h1>
            <button
              onClick={() => navigate('/deals-table')}
              style={{
                padding: '8px 16px',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Table View
            </button>
          </div>
          {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
        </div>

        <div style={{
          display: 'flex',
          gap: '12px',
          overflowX: 'auto',
          overflowY: 'hidden',
          padding: '16px',
          flex: '1',
          alignItems: 'stretch',
          backgroundColor: '#fafafa',
        }}>
          {STAGES.map(stage => (
            <SortableContext
              key={stage}
              items={deals[stage].map(d => d.id)}
              strategy={verticalListSortingStrategy}
            >
              <KanbanColumn stage={stage} deals={deals[stage]} activeId={activeId} />
            </SortableContext>
          ))}
        </div>
      </div>

      <DragOverlay>
        {activeId ? (
          <KanbanCard
            deal={Object.values(deals)
              .flat()
              .find(d => d.id === activeId)!}
          />
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
