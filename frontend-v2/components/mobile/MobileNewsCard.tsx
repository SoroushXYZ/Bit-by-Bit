import React from 'react';
import { Card, CardContent, Typography, Box, useTheme, alpha } from '@mui/material';
import { HeadlineComponent, SecondaryComponent, QuickLinkComponent } from '@/types/components';

interface MobileNewsCardProps {
  component: HeadlineComponent | SecondaryComponent | QuickLinkComponent;
}

export default function MobileNewsCard({ component }: MobileNewsCardProps) {
  const theme = useTheme();
  const isHeadline = component.type === 'headline';
  const isQuickLink = component.type === 'quickLink';

  const handleClick = () => {
    if (component.clickable && component.url) {
      window.open(component.url, '_blank', 'noopener,noreferrer');
    }
  };

  // Better color scheme: subtle background tints
  const getBackgroundColor = () => {
    if (isHeadline) {
      return theme.palette.mode === 'dark' 
        ? alpha('#4a90e2', 0.15)  // Soft blue for headlines
        : alpha('#e3f2fd', 0.8);
    }
    if (isQuickLink) {
      return theme.palette.mode === 'dark'
        ? alpha('#9c27b0', 0.15)  // Soft purple for quicklinks
        : alpha('#f3e5f5', 0.8);
    }
    // Secondary articles - neutral
    return theme.palette.mode === 'dark'
      ? alpha('#616161', 0.1)
      : alpha('#f5f5f5', 0.8);
  };

  return (
    <Card
      sx={{
        mb: 2,
        cursor: component.clickable ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        '&:hover': component.clickable ? {
          transform: 'translateY(-2px)',
          boxShadow: 4,
        } : {},
        bgcolor: getBackgroundColor(),
        border: 1,
        borderColor: 'divider',
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 2.5 }}>

        <Typography
          variant="h6"
          component="h3"
          sx={{
            fontWeight: isHeadline ? 700 : 600,
            fontSize: isHeadline ? '1.1rem' : '1rem',
            mb: 1.5,
            lineHeight: 1.3,
            color: 'text.primary',
          }}
        >
          {component.title}
        </Typography>

        {'description' in component && component.description && (
          <Typography
            variant="body2"
            sx={{
              mb: 2,
              color: 'text.secondary',
              lineHeight: 1.6,
              fontSize: '0.9rem',
            }}
          >
            {component.description}
          </Typography>
        )}

        {isQuickLink && component.summary && (
          <Typography
            variant="body2"
            sx={{
              mb: 2,
              color: 'text.secondary',
              lineHeight: 1.6,
              fontSize: '0.9rem',
            }}
          >
            {component.summary}
          </Typography>
        )}

        {'source' in component && component.source && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Typography
              variant="caption"
              sx={{
                fontSize: '0.75rem',
                color: 'text.secondary',
                fontWeight: 500,
              }}
            >
              {component.source}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

