import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { QuickLinkComponent as QuickLinkComponentType } from '@/types/components';
import { Typography } from '@mui/material';

interface Props {
  component: QuickLinkComponentType;
}

export default function QuickLinkComponent({ component }: Props) {
  const { title } = component;

  return (
    <BaseGridComponent 
      component={component} 
      sx={{ bgcolor: 'grey.50', borderColor: 'grey.200' }}
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

