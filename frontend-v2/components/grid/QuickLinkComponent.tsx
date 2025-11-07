import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { QuickLinkComponent as QuickLinkComponentType } from '@/types/components';
import { Typography, Theme } from '@mui/material';

interface Props {
  component: QuickLinkComponentType;
}

export default function QuickLinkComponent({ component }: Props) {
  const { title } = component;

  return (
    <BaseGridComponent 
      component={component} 
      sx={{ 
        bgcolor: (theme: Theme) => theme.palette.mode === 'dark' ? 'rgba(100, 120, 150, 0.1)' : 'grey.50',
        borderColor: 'divider',
      }}
    >
      <Typography 
        variant="body2" 
        fontWeight="bold"
        sx={{ 
          fontSize: '0.75rem',
          lineHeight: 1.2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          flex: 1,
          overflow: 'hidden',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
        }}
      >
        {title}
      </Typography>
    </BaseGridComponent>
  );
}

