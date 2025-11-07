import React, { useState, useEffect } from 'react';
import { BitComponent as BitComponentType } from '@/types/components';
import { Box, Typography, Theme } from '@mui/material';

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
    const delay = Math.random() * 2000;
    setAnimationDelay(delay);
    const duration = 1000 + Math.random() * 2000;
    setAnimationDuration(duration);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsVisible(prev => !prev);
    }, animationDuration);
    
    return () => clearInterval(interval);
  }, [animationDuration]);

  return (
    <Box
      sx={{
        gridArea,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
      }}
    >
      <Typography
        sx={{
          fontSize: '3rem',
          lineHeight: 1,
          color: (theme: Theme) => theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.15)' : 'grey.300',
          fontFamily: '"Pixelify Sans", system-ui, sans-serif',
          opacity: isVisible ? 1 : 0,
          transition: `opacity ${animationDuration}ms ease`,
          transitionDelay: `${animationDelay}ms`,
        }}
      >
        {display}
      </Typography>
    </Box>
  );
}

