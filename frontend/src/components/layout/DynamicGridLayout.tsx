import React from 'react';
import ComponentRenderer from '@/components/grid/ComponentRenderer';
import { NewsletterLayout } from '@/types/components';

interface Props {
  layout: NewsletterLayout;
}

export default function DynamicGridLayout({ layout }: Props) {
  const { gridConfig, components } = layout;

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-5xl mx-auto">
        <div 
          className="bg-card border rounded-lg shadow-lg p-4"
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${gridConfig.columns}, minmax(0, 1fr))`,
            gridTemplateRows: `repeat(${gridConfig.rows}, minmax(0, 1fr))`,
            gap: '0.5rem',
            width: `${gridConfig.columns * gridConfig.cellSize + (gridConfig.columns - 1) * 8 + 32}px`,
            height: `${gridConfig.rows * gridConfig.cellSize + (gridConfig.rows - 1) * 8 + 32}px`,
            margin: '0 auto'
          }}
        >
          {components.map((component) => (
            <ComponentRenderer key={component.id} component={component} />
          ))}
        </div>
      </div>
    </div>
  );
}
