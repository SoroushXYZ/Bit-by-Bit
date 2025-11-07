import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { StockComponent as StockComponentType } from '@/types/components';
import { Box, Typography } from '@mui/material';

interface Props {
  component: StockComponentType;
}

export default function StockComponent({ component }: Props) {
  const { symbol, price, change, changePercent } = component;
  const iconPath = `/icons/${symbol}.svg`;
  const isUp = change > 0;
  const isDown = change < 0;
  const changeColor = isUp ? 'success.main' : isDown ? 'error.main' : 'text.secondary';

  return (
    <BaseGridComponent component={component}>
      <Box sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        gap: 0.25,
      }}>
        <Box
          component="img"
          src={iconPath}
          alt={symbol}
          sx={{ width: 32, height: 32, mb: 0.25 }}
          onError={(e: any) => {
            e.target.style.display = 'none';
          }}
        />
        <Typography variant="body2" fontWeight="bold" sx={{ fontSize: '0.875rem', lineHeight: 1 }}>
          {price.toFixed(2)}
        </Typography>
        <Typography variant="caption" sx={{ color: changeColor, fontSize: '0.75rem', lineHeight: 1 }}>
          {isUp ? '+' : ''}{change.toFixed(2)}
        </Typography>
        <Typography variant="caption" sx={{ color: changeColor, fontSize: '0.75rem', lineHeight: 1 }}>
          ({isUp ? '+' : ''}{changePercent.toFixed(2)}%)
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

