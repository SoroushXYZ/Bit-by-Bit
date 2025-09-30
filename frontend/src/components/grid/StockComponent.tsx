import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { StockComponent as StockComponentType } from '@/types/components';

interface Props {
  component: StockComponentType;
}

export default function StockComponent({ component }: Props) {
  const { symbol, price, change, changePercent } = component;
  const lower = symbol?.toLowerCase?.() ?? '';
  const iconPath = `/icons/${lower}.svg`;
  const isUp = change > 0;
  const isDown = change < 0;
  const changeColor = isUp ? 'text-emerald-600' : isDown ? 'text-rose-600' : 'text-gray-600';

  return (
    <BaseGridComponent component={component}>
      <div className="h-full flex flex-col items-center justify-center gap-1">
        <div className="flex items-center gap-2">
          <img src={iconPath} alt={symbol} className="w-4 h-4" />
          <span className="text-xs font-semibold tracking-wide">{symbol}</span>
        </div>
        <div className="text-sm font-bold">{price.toFixed(2)}</div>
        <div className={`text-xs ${changeColor}`}>
          {isUp ? '+' : ''}{change.toFixed(2)} ({isUp ? '+' : ''}{changePercent.toFixed(2)}%)
        </div>
      </div>
    </BaseGridComponent>
  );
}


