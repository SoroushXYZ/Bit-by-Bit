import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { SecondaryComponent as SecondaryComponentType } from '@/types/components';
import { Typography, Box, Theme } from '@mui/material';

interface Props {
  component: SecondaryComponentType;
}

export default function SecondaryComponent({ component }: Props) {
  const { title, description, source } = component;

  return (
    <BaseGridComponent 
      component={component} 
      sx={{ 
        bgcolor: (theme: Theme) => theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'grey.50',
        borderColor: 'divider',
      }}
    >
      <Typography 
        variant="body2" 
        fontWeight={600}
        sx={{ 
          mb: 0.5, 
          fontSize: '0.875rem',
          lineHeight: 1.2,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {title}
      </Typography>
      
      <Typography 
        variant="caption" 
        color="text.secondary"
        sx={{ 
          mb: 1, 
          fontSize: '0.75rem',
          lineHeight: 1.2,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          flex: 1,
        }}
      >
        {description}
      </Typography>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 'auto' }}>
        <Typography 
          variant="caption" 
          color="text.secondary"
          sx={{ 
            fontSize: '0.75rem',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {source}
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

