import { useState, useEffect } from 'react';

interface NewsletterData {
  status: string;
  run_id?: string;
  date?: string;
  grid_data?: any;
}

interface UseNewsletterDataReturn {
  data: NewsletterData | null;
  isLoading: boolean;
  error: string | null;
  refreshData: () => void;
}

/**
 * Hook to fetch newsletter data from backend API
 */
export function useNewsletterData(): UseNewsletterDataReturn {
  const [data, setData] = useState<NewsletterData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const fetchNewsletterData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch latest newsletter data
      const response = await fetch(`${apiBaseUrl}/newsletter/grid`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch newsletter: ${response.status} ${response.statusText}`);
      }
      
      const backendData = await response.json();
      setData(backendData);
    } catch (err) {
      console.error('Failed to fetch newsletter data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchNewsletterData();
  }, []);

  return {
    data,
    isLoading,
    error,
    refreshData: fetchNewsletterData,
  };
}

