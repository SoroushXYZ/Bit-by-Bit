import React from 'react';
import { Component } from '@/types/components';
import HeadlineComponent from './HeadlineComponent';
import SecondaryComponent from './SecondaryComponent';
import QuickLinkComponent from './QuickLinkComponent';
import BrandingComponent from './BrandingComponent';
import GitRepoComponent from './GitRepoComponent';
import BitComponent from './BitComponent';
import StockComponent from './StockComponent';
import DayComponent from './DayComponent';
import { Box, Typography, Theme } from '@mui/material';

interface Props {
  component: Component;
}

export default function ComponentRenderer({ component }: Props) {
  switch (component.type) {
    case 'headline':
      return <HeadlineComponent component={component} />;
    
    case 'secondary':
      return <SecondaryComponent component={component} />;
    
    case 'quickLink':
      return <QuickLinkComponent component={component} />;
    
    case 'branding':
      return <BrandingComponent component={component} />;
    
    case 'gitRepo':
      return <GitRepoComponent component={component} />;
    
    case 'bit':
      return <BitComponent component={component} />;
    
    case 'stock':
      return <StockComponent component={component} />;
    
    case 'day':
      return <DayComponent component={component} />;
    
    default: {
      const unknownComponent = component as Component & { type: string };
      console.warn(`Unknown component type: ${unknownComponent.type}`);
      return (
        <Box
          sx={{
            gridArea: `${unknownComponent.position.row} / ${unknownComponent.position.column} / ${unknownComponent.position.row + unknownComponent.position.height} / ${unknownComponent.position.column + unknownComponent.position.width}`,
            bgcolor: (theme: Theme) => theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'grey.200',
            border: 1,
            borderColor: 'divider',
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            Unknown component: {unknownComponent.type}
          </Typography>
        </Box>
      );
    }
  }
}

