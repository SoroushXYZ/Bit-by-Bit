import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/layout/Layout";
import LetterLayout from "@/components/layout/LetterLayout";
import NewsletterCard from "@/components/newsletter/NewsletterCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Calendar, TrendingUp, Newspaper, Clock } from "lucide-react";
import { newsletterAPI, NewsletterData } from "@/lib/api";

interface NewsletterViewerProps {
  initialDate?: string;
}

export default function NewsletterViewer({ initialDate }: NewsletterViewerProps) {
  const router = useRouter();
  const [currentDate, setCurrentDate] = useState(initialDate || new Date().toISOString().split('T')[0]);
  const [newsletterData, setNewsletterData] = useState<NewsletterData | null>(null);
  const [archiveData, setArchiveData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load newsletter data
  useEffect(() => {
    const loadNewsletterData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Load current newsletter
        const data = await newsletterAPI.getNewsletterByDate(currentDate);
        setNewsletterData(data);
        
        // Load archive for navigation
        try {
          const archive = await newsletterAPI.getNewsletterArchive();
          setArchiveData(archive);
        } catch (archiveErr) {
          console.error('Error loading archive:', archiveErr);
          // Continue without archive data
          setArchiveData([]);
        }
      } catch (err) {
        console.error('Error loading newsletter:', err);
        // If specific date not found, try to load latest
        if (currentDate !== new Date().toISOString().split('T')[0]) {
          try {
            const latestData = await newsletterAPI.getLatestNewsletter();
            setNewsletterData(latestData);
            setCurrentDate(new Date().toISOString().split('T')[0]);
          } catch (latestErr) {
            setError('Failed to load newsletter data');
          }
        } else {
          setError('Failed to load newsletter data');
        }
      } finally {
        setLoading(false);
      }
    };

    loadNewsletterData();
  }, [currentDate]);

  // Navigation handler
  const handleNavigate = (date: string) => {
    setCurrentDate(date);
    // Update URL without page reload
    router.push(`/?date=${date}`, undefined, { shallow: true });
  };

  // Get previous and next newsletters
  const currentIndex = archiveData.findIndex(item => item.date === currentDate);
  const previousNewsletter = currentIndex > 0 ? archiveData[currentIndex - 1] : null;
  const nextNewsletter = currentIndex < archiveData.length - 1 ? archiveData[currentIndex + 1] : null;
  const isFirstNewsletter = currentIndex === 0;
  const isCurrentDay = currentDate === new Date().toISOString().split('T')[0];

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading newsletter...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !newsletterData) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-center">Error</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-muted-foreground mb-4">
                {error || 'Newsletter not found'}
              </p>
              <Button onClick={() => router.push('/')}>
                Return to Home
              </Button>
            </CardContent>
          </Card>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <LetterLayout
        currentDate={currentDate}
        previousNewsletter={previousNewsletter ? {
          date: previousNewsletter.date,
          title: previousNewsletter.title,
          articles_count: previousNewsletter.articles_count,
          quality_score: previousNewsletter.quality_score,
          headlines: [] // Would need to load actual headlines
        } : undefined}
        nextNewsletter={nextNewsletter ? {
          date: nextNewsletter.date,
          title: nextNewsletter.title,
          articles_count: nextNewsletter.articles_count,
          quality_score: nextNewsletter.quality_score,
          headlines: [] // Would need to load actual headlines
        } : undefined}
        isFirstNewsletter={isFirstNewsletter}
        isCurrentDay={isCurrentDay}
        onNavigate={handleNavigate}
      >
        <div className="space-y-8">
          {/* Header Section */}
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <Newspaper className="w-8 h-8 text-primary" />
              <h1 className="text-4xl font-bold">{newsletterData.newsletter?.title || 'Bit-by-Bit Tech Newsletter'}</h1>
            </div>
            <div className="flex items-center justify-center gap-4 text-muted-foreground">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>{newsletterData.newsletter?.date || 'Unknown Date'}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>Generated at {newsletterData.newsletter?.generated_at ? new Date(newsletterData.newsletter.generated_at).toLocaleTimeString() : 'Unknown Time'}</span>
              </div>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Articles Processed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(newsletterData.statistics?.headlines_count || 0) + 
                   (newsletterData.statistics?.secondary_count || 0) + 
                   (newsletterData.statistics?.optional_count || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {newsletterData.statistics?.data_reduction_percentage || 0}% reduction from raw feeds
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Average Quality</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{newsletterData.statistics?.average_quality_score || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {newsletterData.statistics?.high_quality_percentage || 0}% high quality articles
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Pipeline Version</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{newsletterData.newsletter?.pipeline_version || '1.0.0'}</div>
                <p className="text-xs text-muted-foreground">
                  AI-powered curation
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Headlines Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-red-500" />
              <h2 className="text-2xl font-bold">Top Headlines</h2>
              <Badge variant="destructive">{newsletterData.content?.headlines?.length || 0}</Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {(newsletterData.content?.headlines || []).map((article) => (
                <NewsletterCard key={article.rank} article={article} category="headlines" />
              ))}
            </div>
          </section>

          <Separator />

          {/* Secondary Articles Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2">
              <Newspaper className="w-5 h-5 text-blue-500" />
              <h2 className="text-2xl font-bold">Important News</h2>
              <Badge variant="secondary">{newsletterData.content?.secondary?.length || 0}</Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {(newsletterData.content?.secondary || []).map((article) => (
                <NewsletterCard key={article.rank} article={article} category="secondary" />
              ))}
            </div>
          </section>

          <Separator />

          {/* Optional Articles Section */}
          <section className="space-y-4">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-500" />
              <h2 className="text-2xl font-bold">Additional Stories</h2>
              <Badge variant="outline">{newsletterData.content?.optional?.length || 0}</Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {(newsletterData.content?.optional || []).map((article) => (
                <NewsletterCard key={article.rank} article={article} category="optional" />
              ))}
            </div>
          </section>
        </div>
      </LetterLayout>
    </Layout>
  );
}
