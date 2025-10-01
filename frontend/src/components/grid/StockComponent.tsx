import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { StockComponent as StockComponentType } from '@/types/components';

interface Props {
  component: StockComponentType;
}

export default function StockComponent({ component }: Props) {
  const { symbol, price, change, changePercent } = component;
  const iconPath = `/icons/${symbol}.svg`;
  const isUp = change > 0;
  const isDown = change < 0;
  const changeColor = isUp ? 'text-emerald-600' : isDown ? 'text-rose-600' : 'text-gray-600';

  return (
    <BaseGridComponent component={component}>
      <div className="h-full flex flex-col items-center justify-center gap-0">
        <img src={iconPath} alt={symbol} className="w-8 h-8 mb-2" />
        <div className="text-sm font-bold leading-none">{price.toFixed(2)}</div>
        <div className={`text-xs ${changeColor} leading-none`}>
          {isUp ? '+' : ''}{change.toFixed(2)}
        </div>
        <div className={`text-xs ${changeColor} leading-none`}>
          ({isUp ? '+' : ''}{changePercent.toFixed(2)}%)
        </div>
      </div>
    </BaseGridComponent>
  );
}


