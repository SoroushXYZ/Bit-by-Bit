import React from 'react';
import { Card, CardContent } from '@mui/material';
import { BaseComponent } from '@/types/components';

interface BaseGridComponentProps {
  component: BaseComponent;
  children: React.ReactNode;
  className?: string;
  sx?: any;
}

export default function BaseGridComponent({ 
  component, 
  children, 
  className = '',
  sx = {}
}: BaseGridComponentProps) {
  const { position, clickable, url } = component;
  
  const gridArea = `${position.row} / ${position.column} / ${position.row + position.height} / ${position.column + position.width}`;
  
  const handleClick = () => {
    if (clickable && url) {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <Card
      sx={{
        gridArea,
        height: '100%',
        cursor: clickable ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        '&:hover': clickable ? {
          transform: 'scale(1.02)',
          boxShadow: 4,
        } : {},
        ...sx,
      }}
      onClick={handleClick}
      className={className}
    >
      <CardContent sx={{ px: 0.75, pt: 0.75, pb: 0, height: '100%', display: 'flex', flexDirection: 'column', '&:last-child': { pb: 0 } }}>
        {children}
      </CardContent>
    </Card>
  );
}

