import { NextApiRequest, NextApiResponse } from 'next';
import { getArchiveData } from '@/data/mockNewsletters';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const archiveData = getArchiveData();
    res.status(200).json(archiveData);
  } catch (error) {
    console.error('Error reading newsletter archive:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}
