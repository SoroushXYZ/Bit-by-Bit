import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { HeadlineComponent as HeadlineComponentType } from '@/types/components';
import { Typography, Box, Theme } from '@mui/material';

interface Props {
  component: HeadlineComponentType;
}

export default function HeadlineComponent({ component }: Props) {
  const { title, description, source } = component;

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
          mb: 0.25, 
          fontSize: '0.75rem',
          lineHeight: 1.2,
          display: '-webkit-box',
          WebkitLineClamp: 3,
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
          mb: 0, 
          fontSize: '0.625rem',
          lineHeight: 1.2,
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          flex: 1,
        }}
      >
        {description}
      </Typography>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 'auto', mb: 0.5 }}>
        <Typography 
          variant="caption" 
          color="text.secondary"
          sx={{ 
            fontSize: '0.75rem',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            lineHeight: 1,
          }}
        >
          {source}
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

