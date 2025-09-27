import Layout from "@/components/layout/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, TrendingUp, Newspaper, Clock, Download } from "lucide-react";

// Sample archive data
const archiveData = [
  {
    date: "2025-09-25",
    title: "Bit-by-Bit Tech Newsletter",
    articles_count: 20,
    quality_score: 88.7,
    status: "completed",
    file_size: "2.3 MB"
  },
  {
    date: "2025-09-24",
    title: "Bit-by-Bit Tech Newsletter",
    articles_count: 18,
    quality_score: 87.2,
    status: "completed",
    file_size: "2.1 MB"
  },
  {
    date: "2025-09-23",
    title: "Bit-by-Bit Tech Newsletter",
    articles_count: 22,
    quality_score: 89.1,
    status: "completed",
    file_size: "2.5 MB"
  },
  {
    date: "2025-09-22",
    title: "Bit-by-Bit Tech Newsletter",
    articles_count: 19,
    quality_score: 86.8,
    status: "completed",
    file_size: "2.2 MB"
  },
  {
    date: "2025-09-21",
    title: "Bit-by-Bit Tech Newsletter",
    articles_count: 21,
    quality_score: 88.3,
    status: "completed",
    file_size: "2.4 MB"
  }
];

export default function Archive() {
  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2">
            <Calendar className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold">Newsletter Archive</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Browse through our complete collection of AI-curated tech newsletters. 
            Each edition contains the most important technology news, carefully selected and summarized.
          </p>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Editions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{archiveData.length}</div>
              <p className="text-xs text-muted-foreground">Newsletters published</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Average Articles</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(archiveData.reduce((sum, item) => sum + item.articles_count, 0) / archiveData.length)}
              </div>
              <p className="text-xs text-muted-foreground">Per newsletter</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Quality Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(archiveData.reduce((sum, item) => sum + item.quality_score, 0) / archiveData.length).toFixed(1)}
              </div>
              <p className="text-xs text-muted-foreground">Content quality</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {archiveData.reduce((sum, item) => sum + item.articles_count, 0)}
              </div>
              <p className="text-xs text-muted-foreground">Curated articles</p>
            </CardContent>
          </Card>
        </div>

        {/* Archive List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Recent Editions</h2>
          <div className="grid gap-4">
            {archiveData.map((edition, index) => (
              <Card key={edition.date} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{edition.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {new Date(edition.date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="flex items-center gap-1">
                        <Newspaper className="w-3 h-3" />
                        {edition.articles_count} articles
                      </Badge>
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        {edition.quality_score}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>File size: {edition.file_size}</span>
                      <span>Status: {edition.status}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Load More */}
        <div className="text-center">
          <Button variant="outline" size="lg">
            Load More Archives
          </Button>
        </div>
      </div>
    </Layout>
  );
}
