import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { QuickLinkComponent as QuickLinkComponentType } from '@/types/components';

interface Props {
  component: QuickLinkComponentType;
}

export default function QuickLinkComponent({ component }: Props) {
  const { title, description } = component;

  return (
    <BaseGridComponent 
      component={component} 
      className="bg-amber-50 border-amber-200 hover:border-amber-300"
    >
      <h3 className="text-xs font-bold mb-1 text-amber-800 line-clamp-2">
        {title}
      </h3>
      
      {description && (
        <p className="text-xs text-amber-700 line-clamp-2">
          {description}
        </p>
      )}
    </BaseGridComponent>
  );
}
