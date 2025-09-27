import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink } from 'lucide-react';
import { Article } from '@/types/newsletter';

interface ArticleCardProps {
  article: Article;
  size: 'small' | 'medium' | 'large';
  variant: 'headlines' | 'secondary' | 'optional';
}

export default function ArticleCard({ article, size, variant }: ArticleCardProps) {
  const sizeClasses = {
    small: 'p-2 text-xs',
    medium: 'p-3 text-sm',
    large: 'p-4 text-base'
  };

  const variantClasses = {
    headlines: 'border-l-4 border-l-red-500 bg-red-50 dark:bg-red-950/20',
    secondary: 'border-l-4 border-l-blue-500 bg-blue-50 dark:bg-blue-950/20',
    optional: 'border-l-4 border-l-gray-500 bg-gray-50 dark:bg-gray-950/20'
  };

  const priorityColors = {
    1: 'bg-red-500',
    2: 'bg-orange-500',
    3: 'bg-yellow-500',
    4: 'bg-green-500',
    5: 'bg-blue-500'
  };

  return (
    <Card className={`h-full transition-all hover:shadow-md ${variantClasses[variant]}`}>
      <CardContent className={sizeClasses[size]}>
        <div className="flex items-start justify-between mb-2">
          <Badge 
            variant="secondary" 
            className={`${priorityColors[article.priority as keyof typeof priorityColors] || 'bg-gray-500'} text-white text-xs`}
          >
            #{article.priority}
          </Badge>
          <ExternalLink className="w-3 h-3 text-muted-foreground" />
        </div>
        
        <h3 className={`font-semibold mb-2 line-clamp-2 ${size === 'large' ? 'text-lg' : size === 'medium' ? 'text-base' : 'text-sm'}`}>
          {article.title}
        </h3>
        
        <p className="text-muted-foreground text-xs mb-2">
          {article.source}
        </p>
        
        {article.summary && size !== 'small' && (
          <p className="text-muted-foreground text-xs line-clamp-2">
            {article.summary}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
