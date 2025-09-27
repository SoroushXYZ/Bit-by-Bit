import Layout from "@/components/layout/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, BarChart3, Users, Clock, Target, Zap } from "lucide-react";

// Sample analytics data
const analyticsData = {
  pipeline: {
    total_runs: 45,
    success_rate: 98.2,
    avg_processing_time: "12.5 minutes",
    articles_processed: 1080,
    quality_threshold: 75.0
  },
  content: {
    total_feeds: 80,
    active_feeds: 78,
    avg_articles_per_feed: 6.8,
    top_sources: [
      { name: "TechCrunch", articles: 45, quality: 92.1 },
      { name: "The Verge", articles: 38, quality: 89.7 },
      { name: "Ars Technica", articles: 35, quality: 91.2 },
      { name: "WIRED", articles: 32, quality: 88.9 }
    ]
  },
  quality: {
    avg_quality_score: 88.7,
    high_quality_percentage: 85.0,
    quality_distribution: {
      excellent: 45,
      good: 35,
      average: 15,
      poor: 5
    }
  },
  performance: {
    gpu_acceleration: "9.1x faster",
    memory_usage: "2.3 GB",
    processing_efficiency: 96.3
  }
};

export default function Analytics() {
  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2">
            <BarChart3 className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold">Analytics Dashboard</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Comprehensive insights into the Bit-by-Bit AI Newsletter pipeline performance, 
            content quality, and processing efficiency.
          </p>
        </div>

        {/* Pipeline Performance */}
        <section className="space-y-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Zap className="w-6 h-6 text-yellow-500" />
            Pipeline Performance
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.pipeline.total_runs}</div>
                <p className="text-xs text-muted-foreground">Pipeline executions</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{analyticsData.pipeline.success_rate}%</div>
                <p className="text-xs text-muted-foreground">Reliable processing</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg Processing Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.pipeline.avg_processing_time}</div>
                <p className="text-xs text-muted-foreground">Per newsletter</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Articles Processed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.pipeline.articles_processed.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total curated</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Content Sources */}
        <section className="space-y-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Users className="w-6 h-6 text-blue-500" />
            Content Sources
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Feed Statistics</CardTitle>
                <CardDescription>RSS feed performance overview</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Total Feeds</span>
                  <Badge variant="outline">{analyticsData.content.total_feeds}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Active Feeds</span>
                  <Badge variant="secondary">{analyticsData.content.active_feeds}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Avg Articles per Feed</span>
                  <Badge variant="outline">{analyticsData.content.avg_articles_per_feed}</Badge>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Top Performing Sources</CardTitle>
                <CardDescription>Highest quality content providers</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {analyticsData.content.top_sources.map((source, index) => (
                  <div key={source.name} className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{source.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{source.articles} articles</Badge>
                      <Badge variant="secondary">{source.quality}</Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Quality Metrics */}
        <section className="space-y-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Target className="w-6 h-6 text-green-500" />
            Quality Metrics
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Quality Overview</CardTitle>
                <CardDescription>Content quality assessment</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Average Quality Score</span>
                  <Badge variant="outline" className="text-green-600">
                    {analyticsData.quality.avg_quality_score}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">High Quality Articles</span>
                  <Badge variant="secondary" className="text-green-600">
                    {analyticsData.quality.high_quality_percentage}%
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Quality Threshold</span>
                  <Badge variant="outline">
                    {analyticsData.pipeline.quality_threshold}+
                  </Badge>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Quality Distribution</CardTitle>
                <CardDescription>Articles by quality level</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(analyticsData.quality.quality_distribution).map(([level, count]) => (
                  <div key={level} className="flex justify-between items-center">
                    <span className="text-sm capitalize">{level}</span>
                    <Badge variant="outline">{count}%</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Performance Metrics */}
        <section className="space-y-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Clock className="w-6 h-6 text-purple-500" />
            Performance Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">GPU Acceleration</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{analyticsData.performance.gpu_acceleration}</div>
                <p className="text-xs text-muted-foreground">vs CPU processing</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analyticsData.performance.memory_usage}</div>
                <p className="text-xs text-muted-foreground">Peak usage</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Processing Efficiency</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">{analyticsData.performance.processing_efficiency}%</div>
                <p className="text-xs text-muted-foreground">Data reduction</p>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </Layout>
  );
}
