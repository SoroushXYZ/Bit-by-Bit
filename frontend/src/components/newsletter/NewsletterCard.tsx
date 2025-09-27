import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ExternalLink, Calendar, TrendingUp } from "lucide-react";

interface Article {
  rank: number;
  title: string;
  summary: string;
  word_count: number;
  source: string;
  url: string;
  quality_score: number;
  quality_level: string;
  content_source: string;
  fallback_used: boolean;
}

interface NewsletterCardProps {
  article: Article;
  category: "headlines" | "secondary" | "optional";
}

export default function NewsletterCard({ article, category }: NewsletterCardProps) {
  const getCategoryColor = (category: string) => {
    switch (category) {
      case "headlines":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "secondary":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "optional":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const getQualityColor = (score: number) => {
    if (score >= 90) return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    if (score >= 80) return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
  };

  return (
    <Card className="h-full hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Badge className={getCategoryColor(category)}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </Badge>
              <Badge variant="outline" className={getQualityColor(article.quality_score)}>
                <TrendingUp className="w-3 h-3 mr-1" />
                {article.quality_score}
              </Badge>
            </div>
            <CardTitle className="text-lg leading-tight line-clamp-2">
              {article.title}
            </CardTitle>
          </div>
        </div>
        <CardDescription className="text-sm text-muted-foreground">
          {article.source} • {article.word_count} words
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
          {article.summary}
        </p>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="w-3 h-3" />
            <span>Rank #{article.rank}</span>
          </div>
          <Button size="sm" variant="outline" asChild>
            <a href={article.url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="w-3 h-3 mr-1" />
              Read
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
