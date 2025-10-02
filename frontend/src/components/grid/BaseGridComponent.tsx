import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { BaseComponent } from '@/types/components';

interface BaseGridComponentProps {
  component: BaseComponent;
  children: React.ReactNode;
  className?: string;
}

export default function BaseGridComponent({ component, children, className = '' }: BaseGridComponentProps) {
  const { position, clickable, url } = component;
  
  const gridArea = `${position.row} / ${position.column} / ${position.row + position.height} / ${position.column + position.width}`;
  
  const handleClick = () => {
    if (clickable && url) {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  const baseClasses = `
    h-full transition-all duration-200 p-2
    ${clickable ? 'cursor-pointer hover:shadow-lg hover:scale-[1.02]' : ''}
    ${className}
  `.trim();

  return (
    <Card 
      className={baseClasses}
      style={{ gridArea }}
      onClick={handleClick}
    >
      <CardContent className="p-0 h-full flex flex-col">
        {children}
      </CardContent>
    </Card>
  );
}
