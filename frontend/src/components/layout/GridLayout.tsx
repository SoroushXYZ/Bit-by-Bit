import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

interface GridBoxProps {
  children: React.ReactNode;
  className?: string;
  gridArea?: string;
}

function GridBox({ children, className = '', gridArea }: GridBoxProps) {
  return (
    <Card 
      className={`h-full ${className}`}
      style={gridArea ? { gridArea } : undefined}
    >
      <CardContent className="p-4 h-full flex items-center justify-center">
        {children}
      </CardContent>
    </Card>
  );
}

export default function GridLayout() {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-5xl mx-auto">
        {/* US Letter sized grid container */}
        <div 
          className="bg-card border rounded-lg shadow-lg p-4"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(12, minmax(0, 1fr))',
            gridTemplateRows: 'repeat(16, minmax(0, 1fr))',
            gap: '0.5rem',
            width: '700px',
            height: '933px',
            margin: '0 auto'
          }}
        >
          {/* BIT - 2x2 grid */}
          <GridBox 
            className="bg-red-500 text-white text-4xl font-bold"
            gridArea="1 / 1 / 3 / 3"
          >
            BIT
          </GridBox>

          {/* BY - 2x2 grid */}
          <GridBox 
            className="bg-blue-500 text-white text-4xl font-bold"
            gridArea="3 / 4 / 5 / 6"
          >
            BY
          </GridBox>

          {/* BIT - 2x2 grid */}
          <GridBox 
            className="bg-green-500 text-white text-4xl font-bold"
            gridArea="8 / 7 / 10 / 9"
          >
            BIT
          </GridBox>

          {/* Headline 1 - 4x2 grid */}
          <GridBox 
            className="bg-orange-500 text-white"
            gridArea="1 / 3 / 3 / 7"
          >
            <div className="text-center">
              <div className="text-xs font-semibold mb-1">HEADLINE</div>
              <div className="text-sm">4x2 Grid</div>
            </div>
          </GridBox>

          {/* Headline 2 - 5x2 grid */}
          <GridBox 
            className="bg-purple-500 text-white"
            gridArea="3 / 7 / 5 / 12"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">HEADLINE</div>
              <div className="text-base">5x2 Grid</div>
            </div>
          </GridBox>

          {/* Large Content - 8x3 grid */}
          <GridBox 
            className="bg-emerald-500 text-white"
            gridArea="5 / 1 / 8 / 9"
          >
            <div className="text-center">
              <div className="text-xs font-semibold mb-1">LARGE CONTENT</div>
              <div className="text-sm">8x3 Grid</div>
            </div>
          </GridBox>

          {/* Secondary 1 - 4x1 grid */}
          <GridBox 
            className="bg-yellow-500 text-black"
            gridArea="8 / 1 / 9 / 5"
          >
            <div className="text-center">
              <div className="text-xs font-semibold mb-1">SECONDARY</div>
              <div className="text-xs">4x1 Grid</div>
            </div>
          </GridBox>

          {/* Secondary 2 - 5x1 grid */}
          <GridBox 
            className="bg-pink-500 text-white"
            gridArea="9 / 1 / 10 / 6"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">SECONDARY</div>
              <div className="text-sm">5x1 Grid</div>
            </div>
          </GridBox>

          {/* Secondary 3 - 6x1 grid */}
          <GridBox 
            className="bg-indigo-500 text-white"
            gridArea="10 / 1 / 11 / 7"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">SECONDARY</div>
              <div className="text-sm">6x1 Grid</div>
            </div>
          </GridBox>

          {/* Small boxes - 1x1 grid */}
          <GridBox 
            className="bg-teal-500 text-white"
            gridArea="8 / 9 / 9 / 10"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          <GridBox 
            className="bg-cyan-500 text-white"
            gridArea="8 / 10 / 9 / 11"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          <GridBox 
            className="bg-emerald-500 text-white"
            gridArea="9 / 9 / 10 / 10"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          <GridBox 
            className="bg-lime-500 text-black"
            gridArea="9 / 10 / 10 / 11"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          {/* Quick Links - 7x1 grid */}
          <GridBox 
            className="bg-amber-500 text-black"
            gridArea="11 / 1 / 12 / 8"
          >
            <div className="text-center">
              <div className="text-xs font-semibold">QUICK LINKS</div>
              <div className="text-xs">7x1 Grid</div>
            </div>
          </GridBox>

          {/* More content areas */}
          <GridBox 
            className="bg-rose-500 text-white"
            gridArea="12 / 1 / 14 / 5"
          >
            <div className="text-center">
              <div className="text-xs font-semibold mb-1">CONTENT AREA</div>
              <div className="text-xs">4x2 Grid</div>
            </div>
          </GridBox>

          <GridBox 
            className="bg-violet-500 text-white"
            gridArea="14 / 1 / 16 / 6"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">CONTENT AREA</div>
              <div className="text-sm">5x2 Grid</div>
            </div>
          </GridBox>

          {/* Fill remaining spaces */}
          <GridBox 
            className="bg-slate-500 text-white"
            gridArea="12 / 9 / 14 / 12"
          >
            <div className="text-center">
              <div className="text-xs">3x2</div>
            </div>
          </GridBox>

          <GridBox 
            className="bg-gray-500 text-white"
            gridArea="14 / 9 / 16 / 12"
          >
            <div className="text-center">
              <div className="text-xs">3x2</div>
            </div>
          </GridBox>

          {/* Corner element - 1x1 grid */}
          <GridBox 
            className="bg-red-600 text-white"
            gridArea="16 / 12 / 17 / 13"
          >
            <div className="text-center">
              <div className="text-xs font-bold">★</div>
            </div>
          </GridBox>
        </div>
      </div>
    </div>
  );
}
