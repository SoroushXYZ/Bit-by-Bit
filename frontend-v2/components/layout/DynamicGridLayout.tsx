import React from 'react';
import { Box } from '@mui/material';
import ComponentRenderer from '@/components/grid/ComponentRenderer';
import { NewsletterLayout } from '@/types/components';

interface Props {
  layout: NewsletterLayout;
}

export default function DynamicGridLayout({ layout }: Props) {
  const { gridConfig, components } = layout;
  
  const gap = 6; // 0.375rem = 6px
  const padding = 16; // 1rem = 16px
  const totalWidth = gridConfig.columns * gridConfig.cellSize + (gridConfig.columns - 1) * gap + padding * 2;
  const totalHeight = gridConfig.rows * gridConfig.cellSize + (gridConfig.rows - 1) * gap + padding * 2;

  return (
    <Box
      sx={{
        bgcolor: 'background.paper',
        border: 1,
        borderColor: 'divider',
        borderRadius: 2,
        boxShadow: 3,
        p: 2,
        display: 'grid',
        gridTemplateColumns: `repeat(${gridConfig.columns}, minmax(0, 1fr))`,
        gridTemplateRows: `repeat(${gridConfig.rows}, minmax(0, 1fr))`,
        gap: `${gap}px`,
        width: `${totalWidth}px`,
        height: `${totalHeight}px`,
        margin: '0 auto',
      }}
    >
      {components.map((component) => (
        <ComponentRenderer key={component.id} component={component} />
      ))}
    </Box>
  );
}

