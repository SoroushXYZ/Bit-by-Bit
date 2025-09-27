import { NextApiRequest, NextApiResponse } from 'next';
import { getNewsletterByDate, getLatestNewsletter } from '@/data/mockNewsletters';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { date } = req.query;

  if (!date || typeof date !== 'string') {
    return res.status(400).json({ message: 'Date parameter is required' });
  }

  try {
    // If date is 'latest', return the most recent newsletter
    if (date === 'latest') {
      const newsletterData = getLatestNewsletter();
      return res.status(200).json(newsletterData);
    }

    // Try to find newsletter by specific date
    const newsletterData = getNewsletterByDate(date);
    
    if (!newsletterData) {
      // If specific date not found, return the latest newsletter
      console.log(`Newsletter not found for date: ${date}, returning latest`);
      const latestData = getLatestNewsletter();
      return res.status(200).json(latestData);
    }

    res.status(200).json(newsletterData);
  } catch (error) {
    console.error('Error reading newsletter data:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
