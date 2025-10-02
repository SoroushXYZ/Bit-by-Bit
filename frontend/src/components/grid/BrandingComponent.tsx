import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { BrandingComponent as BrandingComponentType } from '@/types/components';

interface Props {
  component: BrandingComponentType;
}

export default function BrandingComponent({ component }: Props) {
  const { text, variant } = component;
  
  const variantColors = {
    bit: 'bg-gray-700',
    by: 'bg-gray-700',
    'bit-final': 'bg-gray-700'
  };

  return (
    <BaseGridComponent 
      component={component} 
      className={`${variantColors[variant]} text-white hover:scale-105`}
    >
      <div className="flex items-center justify-center h-full">
        <span className="text-4xl font-bold">
          {text}
        </span>
      </div>
    </BaseGridComponent>
  );
}
