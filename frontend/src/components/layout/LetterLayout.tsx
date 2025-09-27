import { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronLeft, ChevronRight, Calendar, Newspaper, TrendingUp } from "lucide-react";

interface NewsletterPreview {
  date: string;
  title: string;
  articles_count: number;
  quality_score: number;
  headlines: Array<{
    title: string;
    source: string;
  }>;
}

interface LetterLayoutProps {
  children: ReactNode;
  currentDate: string;
  previousNewsletter?: NewsletterPreview;
  nextNewsletter?: NewsletterPreview;
  isFirstNewsletter?: boolean;
  isCurrentDay?: boolean;
  onNavigate: (date: string) => void;
}

export default function LetterLayout({
  children,
  currentDate,
  previousNewsletter,
  nextNewsletter,
  isFirstNewsletter = false,
  isCurrentDay = false,
  onNavigate
}: LetterLayoutProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDateShort = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* US Letter Layout Container */}
      <div className="flex justify-center p-4">
        <div className="flex gap-6 max-w-7xl w-full">
          
          {/* Left Sidebar */}
          <div className="w-80 flex-shrink-0">
            {isFirstNewsletter ? (
              <Card className="h-fit sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Newspaper className="w-5 h-5 text-primary" />
                    First Edition
                  </CardTitle>
                  <CardDescription>
                    Welcome to Bit-by-Bit AI Newsletter
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-sm text-muted-foreground">
                    <p>This is our very first AI-curated tech newsletter, powered by advanced machine learning and natural language processing.</p>
                  </div>
                  <div className="space-y-2">
                    <Badge variant="outline" className="w-full justify-start">
                      <TrendingUp className="w-3 h-3 mr-2" />
                      80+ RSS Feeds
                    </Badge>
                    <Badge variant="outline" className="w-full justify-start">
                      <Calendar className="w-3 h-3 mr-2" />
                      Daily Curation
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ) : previousNewsletter ? (
              <Card className="h-fit sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                  </CardTitle>
                  <CardDescription>
                    {formatDate(previousNewsletter.date)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {previousNewsletter.articles_count} articles
                    </Badge>
                    <Badge variant="secondary">
                      {previousNewsletter.quality_score} quality
                    </Badge>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="font-medium text-sm">Top Headlines:</h4>
                    {previousNewsletter.headlines.slice(0, 3).map((headline, index) => (
                      <div key={index} className="text-sm">
                        <p className="font-medium line-clamp-2">{headline.title}</p>
                        <p className="text-muted-foreground text-xs">{headline.source}</p>
                      </div>
                    ))}
                  </div>
                  
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => onNavigate(previousNewsletter.date)}
                  >
                    <ChevronLeft className="w-4 h-4 mr-2" />
                    View {formatDateShort(previousNewsletter.date)}
                  </Button>
                </CardContent>
              </Card>
            ) : null}
          </div>

          {/* Main Content - US Letter Size */}
          <div className="flex-1 max-w-4xl">
            <div className="bg-card border rounded-lg shadow-lg p-8 min-h-[11in]">
              {children}
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="w-80 flex-shrink-0">
            {isCurrentDay ? (
              <Card className="h-fit sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-primary" />
                    Today's Edition
                  </CardTitle>
                  <CardDescription>
                    Latest AI-curated tech news
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-sm text-muted-foreground">
                    <p>This is today's edition of the Bit-by-Bit newsletter, featuring the most important technology news curated by our AI pipeline.</p>
                  </div>
                  <div className="space-y-2">
                    <Badge variant="outline" className="w-full justify-start">
                      <TrendingUp className="w-3 h-3 mr-2" />
                      Real-time Processing
                    </Badge>
                    <Badge variant="outline" className="w-full justify-start">
                      <Newspaper className="w-3 h-3 mr-2" />
                      AI-Powered Curation
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ) : nextNewsletter ? (
              <Card className="h-fit sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </CardTitle>
                  <CardDescription>
                    {formatDate(nextNewsletter.date)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {nextNewsletter.articles_count} articles
                    </Badge>
                    <Badge variant="secondary">
                      {nextNewsletter.quality_score} quality
                    </Badge>
                  </div>
                  
                  <div className="space-y-3">
                    <h4 className="font-medium text-sm">Top Headlines:</h4>
                    {nextNewsletter.headlines.slice(0, 3).map((headline, index) => (
                      <div key={index} className="text-sm">
                        <p className="font-medium line-clamp-2">{headline.title}</p>
                        <p className="text-muted-foreground text-xs">{headline.source}</p>
                      </div>
                    ))}
                  </div>
                  
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => onNavigate(nextNewsletter.date)}
                  >
                    View {formatDateShort(nextNewsletter.date)}
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
