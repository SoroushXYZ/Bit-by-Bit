import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { BrandingComponent as BrandingComponentType } from '@/types/components';

interface Props {
  component: BrandingComponentType;
}

export default function BrandingComponent({ component }: Props) {
  const { text, variant } = component;
  
  const variantColors = {
    bit: 'bg-red-500',
    by: 'bg-blue-500',
    'bit-final': 'bg-green-500'
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
