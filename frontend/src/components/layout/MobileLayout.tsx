import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

interface MobileBoxProps {
  children: React.ReactNode;
  className?: string;
}

function MobileBox({ children, className = '' }: MobileBoxProps) {
  return (
    <Card className={`w-full ${className}`}>
      <CardContent className="p-4">
        {children}
      </CardContent>
    </Card>
  );
}

export default function MobileLayout() {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-md mx-auto space-y-4">
        
        {/* Header Section */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2">
            <span className="text-4xl font-bold text-red-500">BIT</span>
            <span className="text-4xl font-bold text-blue-500">BY</span>
            <span className="text-4xl font-bold text-green-500">BIT</span>
          </div>
          <p className="text-sm text-muted-foreground">AI Newsletter</p>
        </div>

        {/* Headlines Section */}
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-orange-500">Top Headlines</h2>
          <MobileBox className="bg-orange-100 border-orange-200">
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">HEADLINE</div>
              <div className="text-sm">Breaking tech news</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-purple-100 border-purple-200">
            <div className="text-center">
              <div className="text-sm font-semibold mb-1">HEADLINE</div>
              <div className="text-sm">AI developments</div>
            </div>
          </MobileBox>
        </div>

        {/* Secondary News */}
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-blue-500">Important News</h2>
          <MobileBox className="bg-yellow-100 border-yellow-200">
            <div className="text-center">
              <div className="text-sm font-semibold">SECONDARY</div>
              <div className="text-xs">Tech industry updates</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-pink-100 border-pink-200">
            <div className="text-center">
              <div className="text-sm font-semibold">SECONDARY</div>
              <div className="text-xs">Startup news</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-indigo-100 border-indigo-200">
            <div className="text-center">
              <div className="text-sm font-semibold">SECONDARY</div>
              <div className="text-xs">Product launches</div>
            </div>
          </MobileBox>
        </div>

        {/* Quick Links */}
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-amber-500">Quick Links</h2>
          <MobileBox className="bg-amber-100 border-amber-200">
            <div className="text-center">
              <div className="text-sm font-semibold">QUICK LINKS</div>
              <div className="text-xs">Essential resources</div>
            </div>
          </MobileBox>
        </div>

        {/* Additional Content */}
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-rose-500">More Content</h2>
          <MobileBox className="bg-rose-100 border-rose-200">
            <div className="text-center">
              <div className="text-sm font-semibold">CONTENT AREA</div>
              <div className="text-xs">Additional stories</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-violet-100 border-violet-200">
            <div className="text-center">
              <div className="text-sm font-semibold">CONTENT AREA</div>
              <div className="text-xs">Industry insights</div>
            </div>
          </MobileBox>
        </div>

        {/* Small Info Boxes */}
        <div className="grid grid-cols-2 gap-2">
          <MobileBox className="bg-teal-100 border-teal-200">
            <div className="text-center">
              <div className="text-xs font-semibold">INFO</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-cyan-100 border-cyan-200">
            <div className="text-center">
              <div className="text-xs font-semibold">INFO</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-emerald-100 border-emerald-200">
            <div className="text-center">
              <div className="text-xs font-semibold">INFO</div>
            </div>
          </MobileBox>
          <MobileBox className="bg-lime-100 border-lime-200">
            <div className="text-center">
              <div className="text-xs font-semibold">INFO</div>
            </div>
          </MobileBox>
        </div>

      </div>
    </div>
  );
}
