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
      className="bg-gray-50 border-gray-200 hover:border-gray-300"
    >
      <h2 className="text-xs font-bold mb-1 line-clamp-3">
        {title}
      </h2>
      
      <p className="text-[10px] text-muted-foreground mb-2 line-clamp-3 flex-1 flex items-center">
        {description}
      </p>
      
      <div className="flex items-center justify-end text-xs text-muted-foreground mt-auto">
        <span className="truncate">{source}</span>
      </div>
    </BaseGridComponent>
  );
}
