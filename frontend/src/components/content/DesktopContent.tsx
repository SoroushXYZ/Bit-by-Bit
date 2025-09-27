import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import ArticleCard from './ArticleCard';
import { NewsletterContent } from '@/types/newsletter';

interface DesktopContentProps {
  content: NewsletterContent;
}

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

export default function DesktopContent({ content }: DesktopContentProps) {
  return (
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

      {/* Headlines */}
      {content.headlines.slice(0, 2).map((article, index) => (
        <GridBox 
          key={article.id}
          className="bg-orange-100 border-orange-200"
          gridArea={index === 0 ? "1 / 3 / 3 / 7" : "3 / 7 / 5 / 12"}
        >
          <ArticleCard 
            article={article} 
            size={index === 0 ? "medium" : "large"} 
            variant="headlines" 
          />
        </GridBox>
      ))}

      {/* Secondary Articles */}
      {content.secondary.slice(0, 3).map((article, index) => (
        <GridBox 
          key={article.id}
          className="bg-blue-100 border-blue-200"
          gridArea={`${8 + index} / 1 / ${9 + index} / ${5 + index}`}
        >
          <ArticleCard 
            article={article} 
            size="small" 
            variant="secondary" 
          />
        </GridBox>
      ))}

      {/* Quick Links */}
      <GridBox 
        className="bg-amber-100 border-amber-200"
        gridArea="11 / 1 / 12 / 8"
      >
        <div className="w-full">
          <h3 className="text-xs font-semibold mb-2">Quick Links</h3>
          <div className="space-y-1">
            {content.quickLinks.slice(0, 3).map((link, index) => (
              <div key={index} className="text-xs text-muted-foreground hover:text-primary cursor-pointer">
                {link.title}
              </div>
            ))}
          </div>
        </div>
      </GridBox>

      {/* Optional Articles */}
      {content.optional.slice(0, 2).map((article, index) => (
        <GridBox 
          key={article.id}
          className="bg-gray-100 border-gray-200"
          gridArea={`${12 + index * 2} / 1 / ${14 + index * 2} / ${5 + index}`}
        >
          <ArticleCard 
            article={article} 
            size="medium" 
            variant="optional" 
          />
        </GridBox>
      ))}

      {/* Fill remaining spaces */}
      <GridBox 
        className="bg-slate-100 border-slate-200"
        gridArea="12 / 9 / 14 / 12"
      >
        <div className="text-center">
          <div className="text-xs">Info</div>
        </div>
      </GridBox>

      <GridBox 
        className="bg-gray-100 border-gray-200"
        gridArea="14 / 9 / 16 / 12"
      >
        <div className="text-center">
          <div className="text-xs">Info</div>
        </div>
      </GridBox>

      {/* Corner element */}
      <GridBox 
        className="bg-red-600 text-white"
        gridArea="16 / 12 / 17 / 13"
      >
        <div className="text-center">
          <div className="text-xs font-bold">★</div>
        </div>
      </GridBox>
    </div>
  );
}
