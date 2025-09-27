import Layout from "@/components/layout/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { 
  Play, 
  Pause, 
  RotateCcw, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Database, 
  Cpu, 
  Zap,
  TrendingUp,
  Filter,
  Brain,
  Layers,
  FileText,
  BarChart3
} from "lucide-react";

// Sample pipeline data
const pipelineSteps = [
  {
    id: "rss_gathering",
    name: "RSS Gathering",
    description: "Collect articles from 80+ tech RSS feeds",
    status: "completed",
    duration: "2.3s",
    articles_processed: 546,
    success_rate: 100,
    icon: Database
  },
  {
    id: "content_filtering",
    name: "Content Filtering",
    description: "Language detection, word count, quality checks",
    status: "completed",
    duration: "1.8s",
    articles_processed: 523,
    success_rate: 95.8,
    icon: Filter
  },
  {
    id: "ad_detection",
    name: "Ad Detection",
    description: "DistilBERT model filters advertisements",
    status: "completed",
    duration: "4.2s",
    articles_processed: 498,
    success_rate: 95.2,
    icon: Brain
  },
  {
    id: "llm_quality_scoring",
    name: "LLM Quality Scoring",
    description: "Ollama evaluates content quality (1-100 scale)",
    status: "completed",
    duration: "45.7s",
    articles_processed: 387,
    success_rate: 77.7,
    icon: TrendingUp
  },
  {
    id: "deduplication",
    name: "Deduplication",
    description: "Semantic similarity removes duplicate articles",
    status: "completed",
    duration: "8.1s",
    articles_processed: 156,
    success_rate: 40.3,
    icon: Layers
  },
  {
    id: "article_prioritization",
    name: "Article Prioritization",
    description: "LLM categorizes into headlines/secondary/optional",
    status: "completed",
    duration: "12.4s",
    articles_processed: 156,
    success_rate: 100,
    icon: BarChart3
  },
  {
    id: "summarization",
    name: "Summarization",
    description: "Create newsletter-ready summaries by category",
    status: "completed",
    duration: "18.9s",
    articles_processed: 156,
    success_rate: 100,
    icon: FileText
  },
  {
    id: "newsletter_generation",
    name: "Newsletter Generation",
    description: "Generate final formatted output with metadata",
    status: "completed",
    duration: "0.8s",
    articles_processed: 20,
    success_rate: 100,
    icon: FileText
  }
];

const pipelineStatus = {
  current_status: "completed",
  last_run: "2025-09-26T02:47:56.169575",
  total_duration: "94.2s",
  total_articles_input: 546,
  total_articles_output: 20,
  data_reduction: 96.3,
  gpu_acceleration: "9.1x faster",
  next_scheduled_run: "2025-09-27T02:00:00.000Z"
};

export default function Pipeline() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "running":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "failed":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "pending":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4" />;
      case "running":
        return <Clock className="w-4 h-4" />;
      case "failed":
        return <XCircle className="w-4 h-4" />;
      case "pending":
        return <Clock className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2">
            <Cpu className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold">Pipeline Status</h1>
          </div>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Monitor the AI-powered newsletter pipeline in real-time. 
            Track processing steps, performance metrics, and system health.
          </p>
        </div>

        {/* Pipeline Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Current Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Badge className={getStatusColor(pipelineStatus.current_status)}>
                  {pipelineStatus.current_status}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Last run: {new Date(pipelineStatus.last_run).toLocaleString()}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Duration</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pipelineStatus.total_duration}</div>
              <p className="text-xs text-muted-foreground">
                {pipelineStatus.gpu_acceleration} with GPU
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Articles Processed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {pipelineStatus.total_articles_input} → {pipelineStatus.total_articles_output}
              </div>
              <p className="text-xs text-muted-foreground">
                {pipelineStatus.data_reduction}% reduction
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Next Run</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {new Date(pipelineStatus.next_scheduled_run).toLocaleDateString()}
              </div>
              <p className="text-xs text-muted-foreground">
                {new Date(pipelineStatus.next_scheduled_run).toLocaleTimeString()}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Pipeline Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Pipeline Controls</CardTitle>
            <CardDescription>Manage pipeline execution and monitoring</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Button className="flex items-center gap-2">
                <Play className="w-4 h-4" />
                Run Pipeline
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <Pause className="w-4 h-4" />
                Pause
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <RotateCcw className="w-4 h-4" />
                Restart
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Force GPU
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Pipeline Steps */}
        <section className="space-y-4">
          <h2 className="text-2xl font-bold">Processing Steps</h2>
          <div className="space-y-4">
            {pipelineSteps.map((step, index) => {
              const IconComponent = step.icon;
              return (
                <Card key={step.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
                          <IconComponent className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{step.name}</CardTitle>
                          <CardDescription>{step.description}</CardDescription>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(step.status)}>
                          {getStatusIcon(step.status)}
                          <span className="ml-1">{step.status}</span>
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">Duration: {step.duration}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Database className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">Articles: {step.articles_processed}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm">Success: {step.success_rate}%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>

        {/* System Resources */}
        <section className="space-y-4">
          <h2 className="text-2xl font-bold">System Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">GPU Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">78%</div>
                <p className="text-xs text-muted-foreground">NVIDIA GPU active</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">2.3 GB</div>
                <p className="text-xs text-muted-foreground">Peak usage</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">45%</div>
                <p className="text-xs text-muted-foreground">Average load</p>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </Layout>
  );
}
