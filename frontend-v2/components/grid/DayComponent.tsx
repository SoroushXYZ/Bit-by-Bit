import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { DayComponent as DayComponentType } from '@/types/components';
import { Box, Typography } from '@mui/material';

interface Props {
  component: DayComponentType;
}

export default function DayComponent({ component }: Props) {
  const { number } = component;
  
  return (
    <BaseGridComponent component={component}>
      <Box sx={{ 
        height: '100%', 
        width: '100%', 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center' 
      }}>
        <Typography variant="h6" fontWeight="bold" sx={{ lineHeight: 1 }}>
          Day {number}
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

