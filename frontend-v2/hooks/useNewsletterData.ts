import { useState, useEffect } from 'react';
import { NewsletterLayout } from '@/types/components';
import { parsePipelineLayout } from '@/lib/parsePipelineLayout';

interface NewsletterData {
  status: string;
  run_id?: string;
  date?: string;
  grid_data?: any;
}

interface UseNewsletterDataReturn {
  data: NewsletterData | null;
  layout: NewsletterLayout | null;
  isLoading: boolean;
  error: string | null;
  refreshData: () => void;
}

/**
 * Hook to fetch newsletter data from backend API
 */
export function useNewsletterData(): UseNewsletterDataReturn {
  const [data, setData] = useState<NewsletterData | null>(null);
  const [layout, setLayout] = useState<NewsletterLayout | null>(null);
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
      
      // Parse the layout if grid_data exists
      if (backendData.grid_data) {
        try {
          const parsedLayout = parsePipelineLayout(backendData);
          setLayout(parsedLayout);
        } catch (parseError) {
          console.error('Failed to parse layout:', parseError);
          setError('Failed to parse newsletter layout');
        }
      }
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
    layout,
    isLoading,
    error,
    refreshData: fetchNewsletterData,
  };
}

