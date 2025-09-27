import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { HeadlineComponent as HeadlineComponentType } from '@/types/components';

interface Props {
  component: HeadlineComponentType;
}

export default function HeadlineComponent({ component }: Props) {
  const { title, description, source, publishedAt } = component;

  return (
    <BaseGridComponent 
      component={component} 
      className="bg-red-50 border-red-200 hover:border-red-300"
    >
      <h2 className="text-sm font-bold mb-1 line-clamp-2 flex-1">
        {title}
      </h2>
      
      <p className="text-xs text-muted-foreground mb-2 line-clamp-3">
        {description}
      </p>
      
      <div className="flex items-center justify-between text-xs text-muted-foreground mt-auto">
        <span className="truncate">{source}</span>
        <span className="text-xs">{new Date(publishedAt).toLocaleDateString()}</span>
      </div>
    </BaseGridComponent>
  );
}
