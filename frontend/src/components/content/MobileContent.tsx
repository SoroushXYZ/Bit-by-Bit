import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import ArticleCard from './ArticleCard';
import { NewsletterContent } from '@/types/newsletter';

interface MobileContentProps {
  content: NewsletterContent;
}

export default function MobileContent({ content }: MobileContentProps) {
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
          {content.headlines.map((article) => (
            <ArticleCard 
              key={article.id}
              article={article} 
              size="medium" 
              variant="headlines" 
            />
          ))}
        </div>

        {/* Secondary News */}
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-blue-500">Important News</h2>
          {content.secondary.map((article) => (
            <ArticleCard 
              key={article.id}
              article={article} 
              size="small" 
              variant="secondary" 
            />
          ))}
        </div>

        {/* Quick Links */}
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-amber-500">Quick Links</h2>
          <Card className="bg-amber-50 border-amber-200">
            <CardContent className="p-4">
              <div className="space-y-2">
                {content.quickLinks.map((link, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                    <div>
                      <div className="text-sm font-semibold">{link.title}</div>
                      {link.description && (
                        <div className="text-xs text-muted-foreground">{link.description}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Optional Articles */}
        <div className="space-y-2">
          <h2 className="text-lg font-bold text-gray-500">Additional Stories</h2>
          {content.optional.map((article) => (
            <ArticleCard 
              key={article.id}
              article={article} 
              size="small" 
              variant="optional" 
            />
          ))}
        </div>

      </div>
    </div>
  );
}
