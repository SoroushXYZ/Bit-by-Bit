import { NextApiRequest, NextApiResponse } from 'next';
import { getLatestNewsletter } from '@/data/mockNewsletters';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const newsletterData = getLatestNewsletter();
    res.status(200).json(newsletterData);
  } catch (error) {
    console.error('Error reading newsletter data:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
