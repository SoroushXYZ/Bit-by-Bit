import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Path to the pipeline logs directory
    const pipelineLogsDir = path.join(process.cwd(), '..', 'pipeline', 'logs');
    const pipelineOutputDir = path.join(process.cwd(), '..', 'pipeline', 'data', 'output');
    
    // Check if directories exist
    if (!fs.existsSync(pipelineLogsDir) || !fs.existsSync(pipelineOutputDir)) {
      return res.status(404).json({ message: 'Pipeline directories not found' });
    }

    // Get the latest newsletter file to determine last run
    const outputFiles = fs.readdirSync(pipelineOutputDir)
      .filter(file => file.startsWith('newsletter_output_') && file.endsWith('.json'))
      .sort()
      .reverse();

    let lastRun = new Date().toISOString();
    let totalArticlesOutput = 0;
    
    if (outputFiles.length > 0) {
      const latestFile = outputFiles[0];
      const filePath = path.join(pipelineOutputDir, latestFile);
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const newsletterData = JSON.parse(fileContent);
      
      lastRun = newsletterData.newsletter.generated_at;
      totalArticlesOutput = newsletterData.statistics.headlines_count + 
                           newsletterData.statistics.secondary_count + 
                           newsletterData.statistics.optional_count;
    }

    // Sample pipeline status data
    const pipelineStatus = {
      status: {
        current_status: "completed",
        last_run: lastRun,
        total_duration: "94.2s",
        total_articles_input: 546,
        total_articles_output: totalArticlesOutput,
        data_reduction: 96.3,
        gpu_acceleration: "9.1x faster",
        next_scheduled_run: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
      },
      steps: [
        {
          id: "rss_gathering",
          name: "RSS Gathering",
          description: "Collect articles from 80+ tech RSS feeds",
          status: "completed",
          duration: "2.3s",
          articles_processed: 546,
          success_rate: 100
        },
        {
          id: "content_filtering",
          name: "Content Filtering",
          description: "Language detection, word count, quality checks",
          status: "completed",
          duration: "1.8s",
          articles_processed: 523,
          success_rate: 95.8
        },
        {
          id: "ad_detection",
          name: "Ad Detection",
          description: "DistilBERT model filters advertisements",
          status: "completed",
          duration: "4.2s",
          articles_processed: 498,
          success_rate: 95.2
        },
        {
          id: "llm_quality_scoring",
          name: "LLM Quality Scoring",
          description: "Ollama evaluates content quality (1-100 scale)",
          status: "completed",
          duration: "45.7s",
          articles_processed: 387,
          success_rate: 77.7
        },
        {
          id: "deduplication",
          name: "Deduplication",
          description: "Semantic similarity removes duplicate articles",
          status: "completed",
          duration: "8.1s",
          articles_processed: 156,
          success_rate: 40.3
        },
        {
          id: "article_prioritization",
          name: "Article Prioritization",
          description: "LLM categorizes into headlines/secondary/optional",
          status: "completed",
          duration: "12.4s",
          articles_processed: 156,
          success_rate: 100
        },
        {
          id: "summarization",
          name: "Summarization",
          description: "Create newsletter-ready summaries by category",
          status: "completed",
          duration: "18.9s",
          articles_processed: 156,
          success_rate: 100
        },
        {
          id: "newsletter_generation",
          name: "Newsletter Generation",
          description: "Generate final formatted output with metadata",
          status: "completed",
          duration: "0.8s",
          articles_processed: totalArticlesOutput,
          success_rate: 100
        }
      ]
    };

    res.status(200).json(pipelineStatus);
  } catch (error) {
    console.error('Error reading pipeline status:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
