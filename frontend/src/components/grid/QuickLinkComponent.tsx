import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { QuickLinkComponent as QuickLinkComponentType } from '@/types/components';

interface Props {
  component: QuickLinkComponentType;
}

export default function QuickLinkComponent({ component }: Props) {
  const { title } = component;

  return (
    <BaseGridComponent 
      component={component} 
      className="bg-amber-50 border-amber-200 hover:border-amber-300"
    >
      <h3 className="text-xs font-bold text-amber-800 line-clamp-2 flex-1 flex items-center">
        {title}
      </h3>
    </BaseGridComponent>
  );
}
