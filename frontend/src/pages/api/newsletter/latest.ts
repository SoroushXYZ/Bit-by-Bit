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

    // Read the most recent file
    const latestFile = files[0];
    const filePath = path.join(pipelineOutputDir, latestFile);
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const newsletterData = JSON.parse(fileContent);

    res.status(200).json(newsletterData);
  } catch (error) {
    console.error('Error reading newsletter data:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
