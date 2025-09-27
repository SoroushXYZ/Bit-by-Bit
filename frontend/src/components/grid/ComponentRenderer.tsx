import React from 'react';
import { Component } from '@/types/components';
import HeadlineComponent from './HeadlineComponent';
import SecondaryComponent from './SecondaryComponent';
import QuickLinkComponent from './QuickLinkComponent';
import BrandingComponent from './BrandingComponent';

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
    
    // Future component types will be added here
    case 'stock':
    case 'image':
    case 'icon':
    default:
      console.warn(`Unknown component type: ${component.type}`);
      return (
        <div className="bg-gray-200 border border-gray-300 p-4 rounded text-center">
          <span className="text-sm text-gray-500">
            Unknown component: {component.type}
          </span>
        </div>
      );
  }
}
