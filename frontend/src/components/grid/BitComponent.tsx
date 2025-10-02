import React, { useState, useEffect } from 'react';
import { BitComponent as BitComponentType } from '@/types/components';

interface Props {
  component: BitComponentType;
}

export default function BitComponent({ component }: Props) {
  const display = component.value === 1 ? '1' : '0';
  const { position } = component;
  const gridArea = `${position.row} / ${position.column} / ${position.row + position.height} / ${position.column + position.width}`;
  
  const [isVisible, setIsVisible] = useState(() => Math.random() > 0.5);
  const [animationDelay, setAnimationDelay] = useState(0);
  const [animationDuration, setAnimationDuration] = useState(0);

  useEffect(() => {
    // Random delay between 0-2 seconds
    const delay = Math.random() * 2000;
    setAnimationDelay(delay);
    
    // Random duration between 1-3 seconds
    const duration = 1000 + Math.random() * 2000;
    setAnimationDuration(duration);
  }, []);

  useEffect(() => {
    // Random interval for fade in/out cycle
    const interval = setInterval(() => {
      setIsVisible(prev => !prev);
    }, animationDuration);
    
    return () => clearInterval(interval);
  }, [animationDuration]);

  return (
    <div 
      className="flex h-full items-center justify-center"
      style={{ gridArea }}
    >
      <span 
        className={`text-5xl leading-none text-gray-300 transition-opacity duration-[2250ms] ${
          isVisible ? 'opacity-100' : 'opacity-0'
        }`}
        style={{ 
          fontFamily: '"Pixelify Sans", system-ui, sans-serif',
          transitionDelay: `${animationDelay}ms`
        }}
      >
        {display}
      </span>
    </div>
  );
}


