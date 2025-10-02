import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { DayComponent as DayComponentType } from '@/types/components';

interface Props {
  component: DayComponentType;
}

export default function DayComponent({ component }: Props) {
  const { number } = component;
  return (
    <BaseGridComponent component={component}>
      <div className="h-full w-full flex flex-col items-center justify-center">
        <div className="text-2xl font-bold leading-none">{`Day ${number}`}</div>
      </div>
    </BaseGridComponent>
  );
}


