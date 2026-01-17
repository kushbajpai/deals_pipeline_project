import { DndContext } from "@dnd-kit/core";
import { STAGES } from "../../types/deal";
import Column from "./Column";

export default function Board({ deals, onMove }: any) {
  return (
    <DndContext
      onDragEnd={({ active, over }) => {
        if (over && active.data.current.stage !== over.id) {
          onMove(active.id, over.id);
        }
      }}
    >
      <div style={{ display: "flex", gap: 16 }}>
        {STAGES.map(stage => (
          <Column
            key={stage}
            stage={stage}
            deals={deals.filter((d: any) => d.stage === stage)}
          />
        ))}
      </div>
    </DndContext>
  );
}
