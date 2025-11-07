import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { BrandingComponent as BrandingComponentType } from '@/types/components';
import { Typography, Box, Theme } from '@mui/material';

interface Props {
  component: BrandingComponentType;
}

export default function BrandingComponent({ component }: Props) {
  const { text, variant } = component;

  return (
    <BaseGridComponent 
      component={component} 
      sx={{ 
        bgcolor: (theme: Theme) => theme.palette.mode === 'dark' ? 'primary.dark' : 'grey.800',
        color: 'white',
        '&:hover': {
          transform: 'scale(1.05)',
        },
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100%' 
      }}>
        <Typography 
          variant="h4" 
          fontWeight="bold"
          sx={{ fontSize: '2rem' }}
        >
          {text}
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

