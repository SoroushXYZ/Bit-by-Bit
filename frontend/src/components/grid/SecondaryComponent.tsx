import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { SecondaryComponent as SecondaryComponentType } from '@/types/components';

interface Props {
  component: SecondaryComponentType;
}

export default function SecondaryComponent({ component }: Props) {
  const { title, description, source, publishedAt } = component;

  return (
    <BaseGridComponent 
      component={component} 
      className="bg-blue-50 border-blue-200 hover:border-blue-300"
    >
      <h3 className="text-sm font-semibold mb-1 line-clamp-2">
        {title}
      </h3>
      
      <p className="text-xs text-muted-foreground mb-1 line-clamp-2 flex-1 flex items-center">
        {description}
      </p>
      
      <div className="flex items-center justify-end text-xs text-muted-foreground mt-auto">
        <span className="truncate">{source}</span>
      </div>
    </BaseGridComponent>
  );
}
