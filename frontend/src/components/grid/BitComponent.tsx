import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { BitComponent as BitComponentType } from '@/types/components';

interface Props {
  component: BitComponentType;
}

export default function BitComponent({ component }: Props) {
  const display = component.value === 1 ? '1' : '0';

  return (
    <BaseGridComponent component={component}>
      <div className="flex h-full items-center justify-center">
        <span className="text-5xl font-bold leading-none">
          {display}
        </span>
      </div>
    </BaseGridComponent>
  );
}


