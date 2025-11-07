import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { GitRepoComponent as GitRepoComponentType } from '@/types/components';
import { Box, Typography, Theme } from '@mui/material';
import GitHubIcon from '@mui/icons-material/GitHub';

interface Props {
  component: GitRepoComponentType;
}

export default function GitRepoComponent({ component }: Props) {
  const { name, stars, description } = component;

  const formatStars = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  return (
    <BaseGridComponent
      component={component}
      sx={{ 
        bgcolor: (theme: Theme) => theme.palette.mode === 'dark' ? 'rgba(100, 120, 150, 0.1)' : 'grey.50',
        borderColor: 'divider',
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', textAlign: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.25 }}>
          <GitHubIcon 
            sx={{ 
              width: 16, 
              height: 16, 
              mr: 0.5, 
              flexShrink: 0,
              color: 'text.primary',
            }} 
          />
          <Typography 
            variant="body2" 
            fontWeight="bold"
            sx={{ 
              fontSize: '0.8rem',
              lineHeight: 1.3,
              textAlign: 'left',
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              overflow: 'hidden',
            }}
          >
            {name}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 0.25 }}>
          <Typography variant="caption" sx={{ fontSize: '0.75rem', mr: 0.5 }}>⭐</Typography>
          <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>
            {formatStars(stars)}
          </Typography>
        </Box>

        <Typography 
          variant="caption" 
          color="text.secondary"
          sx={{ 
            fontSize: '0.7rem',
            flex: 1,
            overflow: 'hidden',
            wordBreak: 'break-word',
            overflowWrap: 'break-word',
            lineHeight: 1.3,
          }}
        >
          {description}
        </Typography>
      </Box>
    </BaseGridComponent>
  );
}

