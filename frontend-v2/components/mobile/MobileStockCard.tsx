import React from 'react';
import { Card, CardContent, Typography, Box, useTheme, alpha } from '@mui/material';
import { StockComponent } from '@/types/components';

interface MobileStockCardProps {
  component: StockComponent;
}

export default function MobileStockCard({ component }: MobileStockCardProps) {
  const theme = useTheme();
  const { symbol, price, change, changePercent } = component;
  const iconPath = `/icons/${symbol}.svg`;
  const isUp = change > 0;
  const isDown = change < 0;
  const changeColor = isUp ? 'success.main' : isDown ? 'error.main' : 'text.secondary';

  const handleClick = () => {
    if (component.clickable && component.url) {
      window.open(component.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <Card
      sx={{
        cursor: component.clickable ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        '&:hover': component.clickable ? {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        } : {},
        bgcolor: theme.palette.mode === 'dark'
          ? alpha('#ff9800', 0.15)  // Soft orange for stocks
          : alpha('#fff3e0', 0.8),
        border: 1,
        borderColor: 'divider',
        height: '100%',
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
          <Box
            component="img"
            src={iconPath}
            alt={symbol}
            sx={{ width: 32, height: 32 }}
            onError={(e: any) => {
              e.target.style.display = 'none';
            }}
          />
          <Typography
            variant="body2"
            sx={{
              fontWeight: 700,
              fontSize: '0.875rem',
              lineHeight: 1.2,
              color: 'text.primary',
            }}
          >
            {symbol}
          </Typography>
          <Typography
            variant="body2"
            sx={{
              fontSize: '0.8rem',
              color: 'text.primary',
              fontWeight: 600,
            }}
          >
            ${price.toFixed(2)}
          </Typography>
          <Box sx={{ textAlign: 'center' }}>
            <Typography
              variant="caption"
              sx={{
                color: changeColor,
                fontSize: '0.7rem',
                fontWeight: 600,
                display: 'block',
              }}
            >
              {isUp ? '+' : ''}{change.toFixed(2)}
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: changeColor,
                fontSize: '0.65rem',
              }}
            >
              ({isUp ? '+' : ''}{changePercent.toFixed(2)}%)
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

