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
      className="bg-gray-50 border-gray-200 hover:border-gray-300 py-0"
    >
         <h3 className="text-xs font-bold text-gray-800 line-clamp-2 flex-1 flex items-center justify-center text-center">
           {title}
         </h3>
    </BaseGridComponent>
  );
}
