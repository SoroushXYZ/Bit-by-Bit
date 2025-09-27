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
          className="bg-card border rounded-lg shadow-lg p-5"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(10, minmax(0, 1fr))',
            gridTemplateRows: 'repeat(16, minmax(0, 1fr))',
            gap: '0.6rem',
            width: '700px',
            height: '1120px',
            margin: '0 auto'
          }}
        >
          {/* BIT - 2x2 grid */}
          <GridBox 
            className="bg-red-500 text-white text-5xl font-bold"
            gridArea="1 / 1 / 3 / 3"
          >
            BIT
          </GridBox>

          {/* BY - 2x2 grid */}
          <GridBox 
            className="bg-blue-500 text-white text-5xl font-bold"
            gridArea="3 / 4 / 5 / 6"
          >
            BY
          </GridBox>

          {/* BIT - 2x2 grid */}
          <GridBox 
            className="bg-green-500 text-white text-5xl font-bold"
            gridArea="7 / 7 / 9 / 9"
          >
            BIT
          </GridBox>

          {/* Headline 1 - 3x2 grid */}
          <GridBox 
            className="bg-orange-500 text-white"
            gridArea="1 / 3 / 3 / 6"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">HEADLINE</div>
              <div className="text-base">3x2 Grid</div>
            </div>
          </GridBox>

          {/* Headline 2 - 3x2 grid */}
          <GridBox 
            className="bg-purple-500 text-white"
            gridArea="3 / 6 / 5 / 9"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">HEADLINE</div>
              <div className="text-base">3x2 Grid</div>
            </div>
          </GridBox>

          {/* Secondary 1 - 3x1 grid */}
          <GridBox 
            className="bg-yellow-500 text-black"
            gridArea="5 / 1 / 6 / 4"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">SECONDARY</div>
              <div className="text-sm">3x1 Grid</div>
            </div>
          </GridBox>

          {/* Secondary 2 - 3x1 grid */}
          <GridBox 
            className="bg-pink-500 text-white"
            gridArea="6 / 1 / 7 / 4"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">SECONDARY</div>
              <div className="text-sm">3x1 Grid</div>
            </div>
          </GridBox>

          {/* Secondary 3 - 3x1 grid */}
          <GridBox 
            className="bg-indigo-500 text-white"
            gridArea="7 / 1 / 8 / 4"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">SECONDARY</div>
              <div className="text-sm">3x1 Grid</div>
            </div>
          </GridBox>

          {/* Small boxes - 1x1 grid */}
          <GridBox 
            className="bg-teal-500 text-white"
            gridArea="5 / 4 / 6 / 5"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          <GridBox 
            className="bg-cyan-500 text-white"
            gridArea="5 / 5 / 6 / 6"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          <GridBox 
            className="bg-emerald-500 text-white"
            gridArea="6 / 4 / 7 / 5"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          <GridBox 
            className="bg-lime-500 text-black"
            gridArea="6 / 5 / 7 / 6"
          >
            <div className="text-xs text-center">1x1</div>
          </GridBox>

          {/* Quick Links - 2x1 grid */}
          <GridBox 
            className="bg-amber-500 text-black"
            gridArea="8 / 1 / 9 / 3"
          >
            <div className="text-center">
              <div className="text-sm font-semibold">QUICK LINKS</div>
              <div className="text-sm">2x1 Grid</div>
            </div>
          </GridBox>

          {/* More content areas */}
          <GridBox 
            className="bg-rose-500 text-white"
            gridArea="9 / 1 / 11 / 4"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">CONTENT AREA</div>
              <div className="text-sm">3x2 Grid</div>
            </div>
          </GridBox>

          <GridBox 
            className="bg-violet-500 text-white"
            gridArea="11 / 1 / 13 / 4"
          >
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">CONTENT AREA</div>
              <div className="text-sm">3x2 Grid</div>
            </div>
          </GridBox>

          {/* Fill remaining spaces */}
          <GridBox 
            className="bg-slate-500 text-white"
            gridArea="13 / 1 / 15 / 3"
          >
            <div className="text-center">
              <div className="text-sm">2x2</div>
            </div>
          </GridBox>

          <GridBox 
            className="bg-gray-500 text-white"
            gridArea="15 / 1 / 17 / 3"
          >
            <div className="text-center">
              <div className="text-sm">2x2</div>
            </div>
          </GridBox>
        </div>
      </div>
    </div>
  );
}
