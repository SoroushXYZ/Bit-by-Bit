import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Path to the pipeline output directory
    const pipelineOutputDir = path.join(process.cwd(), '..', 'pipeline', 'data', 'output');
    
    // Check if the directory exists
    if (!fs.existsSync(pipelineOutputDir)) {
      return res.status(404).json({ message: 'Pipeline output directory not found' });
    }

    // Get all newsletter output files
    const files = fs.readdirSync(pipelineOutputDir)
      .filter(file => file.startsWith('newsletter_output_') && file.endsWith('.json'))
      .sort()
      .reverse(); // Most recent first

    if (files.length === 0) {
      return res.status(404).json({ message: 'No newsletter files found' });
    }

    // Read all files and create archive data
    const archiveData = files.map(file => {
      const filePath = path.join(pipelineOutputDir, file);
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const newsletterData = JSON.parse(fileContent);
      
      // Extract date from filename (newsletter_output_YYYYMMDD_HHMMSS.json)
      const dateMatch = file.match(/newsletter_output_(\d{8})_(\d{6})\.json/);
      const date = dateMatch ? dateMatch[1] : 'unknown';
      
      return {
        date: date,
        title: newsletterData.newsletter.title,
        articles_count: newsletterData.statistics.headlines_count + 
                       newsletterData.statistics.secondary_count + 
                       newsletterData.statistics.optional_count,
        quality_score: newsletterData.statistics.average_quality_score,
        status: 'completed',
        file_size: `${(fs.statSync(filePath).size / 1024 / 1024).toFixed(1)} MB`,
        generated_at: newsletterData.newsletter.generated_at
      };
    });

    res.status(200).json(archiveData);
  } catch (error) {
    console.error('Error reading newsletter archive:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
