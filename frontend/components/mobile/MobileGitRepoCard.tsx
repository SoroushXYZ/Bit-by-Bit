import React from 'react';
import { Card, CardContent, Typography, Box, useTheme, alpha } from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';
import { GitRepoComponent } from '@/types/components';

interface MobileGitRepoCardProps {
  component: GitRepoComponent;
}

export default function MobileGitRepoCard({ component }: MobileGitRepoCardProps) {
  const theme = useTheme();
  const { name, stars, description } = component;

  const formatStars = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  const handleClick = () => {
    if (component.clickable && component.url) {
      window.open(component.url, '_blank', 'noopener,noreferrer');
    }
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
        bgcolor: theme.palette.mode === 'dark'
          ? alpha('#26a69a', 0.15)  // Soft teal for git repos
          : alpha('#e0f2f1', 0.8),
        border: 1,
        borderColor: 'divider',
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
          <GitHubIcon 
            sx={{ 
              width: 20, 
              height: 20, 
              mr: 1,
              color: 'text.primary',
            }} 
          />
          <Typography
            variant="h6"
            component="h3"
            sx={{
              fontWeight: 600,
              fontSize: '1rem',
              lineHeight: 1.3,
              color: 'text.primary',
              flex: 1,
            }}
          >
            {name}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
            <Typography variant="caption" sx={{ fontSize: '0.875rem', mr: 0.5 }}>⭐</Typography>
            <Typography variant="body2" sx={{ fontSize: '0.875rem', fontWeight: 600 }}>
              {formatStars(stars)}
            </Typography>
          </Box>
        </Box>

        {description && (
          <Typography
            variant="body2"
            sx={{
              color: 'text.secondary',
              lineHeight: 1.6,
              fontSize: '0.9rem',
            }}
          >
            {description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

