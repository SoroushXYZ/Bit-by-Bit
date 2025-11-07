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
          mb: 0.5,
          py: 0.5,
          fontSize: '0.9rem',
          lineHeight: 1.3,
          wordBreak: 'break-word',
          overflowWrap: 'break-word',
        }}
      >
        {title}
      </Typography>
      
      <Typography 
        variant="caption" 
        color="text.secondary"
        sx={{ 
          mb: 0, 
          fontSize: '0.75rem',
          lineHeight: 1.3,
          flex: 1,
          wordBreak: 'break-word',
          overflowWrap: 'break-word',
          overflow: 'hidden',
        }}
      >
        {description}
      </Typography>
      
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 'auto', pt: 0.25 }}>
        <Typography 
          variant="caption" 
          color="text.secondary"
          sx={{ 
            fontSize: '0.7rem',
            lineHeight: 1.2,
            textAlign: 'right',
            wordBreak: 'break-word',
            overflowWrap: 'break-word',
          }}
        >
          {source}
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

