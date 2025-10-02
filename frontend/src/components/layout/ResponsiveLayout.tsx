import React, { useState, useEffect } from 'react';
import GridLayout from './GridLayout';
import MobileLayout from './MobileLayout';

export default function ResponsiveLayout() {
  const [isMobile, setIsMobile] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < 768); // md breakpoint
    };

    // Check on mount
    checkIsMobile();
    setIsHydrated(true);

    // Add event listener
    window.addEventListener('resize', checkIsMobile);

    // Cleanup
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  // Show loading state during hydration to prevent mismatch
  if (!isHydrated) {
    return (
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-5xl mx-auto">
          <div className="bg-card border rounded-lg shadow-lg p-6 min-h-[11in] flex items-center justify-center">
            <div className="text-muted-foreground">Loading...</div>
          </div>
        </div>
      </div>
    );
  }

  return isMobile ? <MobileLayout /> : <GridLayout />;
}
