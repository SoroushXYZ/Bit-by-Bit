import React from 'react';
import ComponentRenderer from '@/components/grid/ComponentRenderer';
import { NewsletterLayout } from '@/types/components';

interface Props {
  layout: NewsletterLayout;
}

export default function DynamicGridLayout({ layout }: Props) {
  const { gridConfig, components } = layout;

  return (
    <div 
      className="bg-card border rounded-lg shadow-lg p-4"
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${gridConfig.columns}, minmax(0, 1fr))`,
        gridTemplateRows: `repeat(${gridConfig.rows}, minmax(0, 1fr))`,
        // Slightly reduce the gap between grid items from 8px to 6px
        gap: '0.375rem',
        width: `${gridConfig.columns * gridConfig.cellSize + (gridConfig.columns - 1) * 6 + 32}px`,
        height: `${gridConfig.rows * gridConfig.cellSize + (gridConfig.rows - 1) * 6 + 32}px`,
        margin: '0 auto'
      }}
    >
      {components.map((component) => (
        <ComponentRenderer key={component.id} component={component} />
      ))}
    </div>
  );
}
