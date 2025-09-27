import Layout from "@/components/layout/Layout";
import NewsletterCard from "@/components/newsletter/NewsletterCard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Calendar, TrendingUp, Newspaper, Clock } from "lucide-react";

// Sample data structure based on the newsletter output
const sampleNewsletter = {
  newsletter: {
    title: "Bit-by-Bit Tech Newsletter",
    date: "September 26, 2025",
    generated_at: "2025-09-26T02:47:56.169575",
    pipeline_version: "1.0.0"
  },
  content: {
    headlines: [
      {
        rank: 1,
        title: "Trump's H-1B Visa Fee Sparks Concerns Among Tech Firms",
        summary: "President Trump's new $100,000 fee for H-1B visas has sparked concerns among top tech firms like Amazon, Meta, and Microsoft, who rely on the program to hire foreign workers. The move could limit access to talent and hurt innovation in the long term.",
        word_count: 39,
        source: "Business Insider (Tech)",
        url: "https://www.businessinsider.com/business-leaders-react-trump-h-1b-visa-fee-2025-9",
        quality_score: 95.2,
        quality_level: "excellent",
        content_source: "full_content",
        fallback_used: false
      },
      {
        rank: 2,
        title: "Trump Signs Order to Allow American TikTok Buyout",
        summary: "President Trump signed an executive order allowing a US-based TikTok company, valued at $14 billion, with potential investors including Oracle and Rupert Murdoch. The move aims to create a separate entity from ByteDance, but critics argue it doesn't address core concerns about data control.",
        word_count: 39,
        source: "Daring Fireball",
        url: "https://www.nytimes.com/2025/09/25/technology/trump-tiktok-ban-deal.html",
        quality_score: 88.5,
        quality_level: "excellent",
        content_source: "full_content",
        fallback_used: false
      },
      {
        rank: 3,
        title: "Microsoft, Asus Open Preorders for Xbox Ally & Ally X Handhelds",
        summary: "Microsoft and Asus have launched preorders for the Xbox Ally ($599) and Ally X ($999), marking a significant entry into the handheld gaming market with unique features like Windows 11 and improved designs.",
        word_count: 39,
        source: "The Verge",
        url: "https://www.theverge.com/news/784286/xbox-handheld-ally-x-price-preorder",
        quality_score: 88.5,
        quality_level: "excellent",
        content_source: "full_content",
        fallback_used: false
      }
    ],
    secondary: [
      {
        rank: 1,
        title: "Cloudflare Unveils Enhanced Developer Platform with New Features",
        summary: "Cloudflare introduces new capabilities, including improved Node.js support, AI Search with model diversity, and enhanced Remote Bindings for local development.",
        word_count: 29,
        source: "Cloudflare Blog",
        url: "https://blog.cloudflare.com/cloudflare-developer-platform-keeps-getting-better-faster-and-more-powerful/",
        quality_score: 88.5,
        quality_level: "excellent",
        content_source: "full_content",
        fallback_used: false
      },
      {
        rank: 2,
        title: "Recompose Expands Human Composting Beyond Seattle",
        summary: "Human composting startup Recompose is poised to grow beyond Seattle, with 13 states approving natural organic reduction, and plans to expand through franchising.",
        word_count: 29,
        source: "GeekWire",
        url: "https://www.geekwire.com/2025/inside-recompose-where-the-human-composting-startup-is-ready-to-grow-its-formula-beyond-seattle/",
        quality_score: 88.3,
        quality_level: "excellent",
        content_source: "full_content",
        fallback_used: false
      }
    ],
    optional: [
      {
        rank: 1,
        title: "Seattle Tech Execs Make Key Moves",
        summary: "Several Seattle-based startups and companies appointed or promoted executives, including CFOs, CBOs, and CEOs.",
        word_count: 29,
        source: "GeekWire",
        url: "https://www.geekwire.com/2025/seattle-tech-execs-make-key-moves/",
        quality_score: 85.0,
        quality_level: "good",
        content_source: "full_content",
        fallback_used: false
      }
    ]
  },
  statistics: {
    headlines_count: 5,
    secondary_count: 8,
    optional_count: 7,
    data_reduction_percentage: 96.3,
    average_quality_score: 88.7,
    high_quality_percentage: 85.0
  }
};

export default function Home() {
  return (
    <Layout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2">
            <Newspaper className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold">{sampleNewsletter.newsletter.title}</h1>
          </div>
          <div className="flex items-center justify-center gap-4 text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>{sampleNewsletter.newsletter.date}</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>Generated at {new Date(sampleNewsletter.newsletter.generated_at).toLocaleTimeString()}</span>
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
              <div className="text-2xl font-bold">{sampleNewsletter.statistics.headlines_count + sampleNewsletter.statistics.secondary_count + sampleNewsletter.statistics.optional_count}</div>
              <p className="text-xs text-muted-foreground">
                {sampleNewsletter.statistics.data_reduction_percentage}% reduction from raw feeds
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Average Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{sampleNewsletter.statistics.average_quality_score}</div>
              <p className="text-xs text-muted-foreground">
                {sampleNewsletter.statistics.high_quality_percentage}% high quality articles
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Pipeline Version</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{sampleNewsletter.newsletter.pipeline_version}</div>
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
            <Badge variant="destructive">{sampleNewsletter.content.headlines.length}</Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sampleNewsletter.content.headlines.map((article) => (
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
            <Badge variant="secondary">{sampleNewsletter.content.secondary.length}</Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sampleNewsletter.content.secondary.map((article) => (
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
            <Badge variant="outline">{sampleNewsletter.content.optional.length}</Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sampleNewsletter.content.optional.map((article) => (
              <NewsletterCard key={article.rank} article={article} category="optional" />
            ))}
          </div>
        </section>
    </div>
    </Layout>
  );
}