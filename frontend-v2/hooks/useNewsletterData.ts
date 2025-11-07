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
  availableDates: string[];
  selectedDate: string | null;
  isLoading: boolean;
  error: string | null;
  selectDate: (date: string | null) => void;
  refreshData: () => void;
}

/**
 * Hook to fetch newsletter data from backend API
 */
export function useNewsletterData(): UseNewsletterDataReturn {
  const [data, setData] = useState<NewsletterData | null>(null);
  const [layout, setLayout] = useState<NewsletterLayout | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  // Fetch available dates
  const fetchAvailableDates = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/newsletter/dates`);
      if (!response.ok) {
        throw new Error(`Failed to fetch dates: ${response.status}`);
      }
      const result = await response.json();
      setAvailableDates(result.dates || []);
    } catch (err) {
      console.error('Failed to fetch available dates:', err);
      // Don't set error here, just log it
    }
  };

  // Fetch newsletter data for a specific date
  const fetchNewsletterData = async (date: string | null) => {
    try {
      setIsLoading(true);
      setError(null);

      const url = date 
        ? `${apiBaseUrl}/newsletter/grid?date=${date}`
        : `${apiBaseUrl}/newsletter/grid`;
      
      const response = await fetch(url);
      
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

  // Select a date
  const selectDate = (date: string | null) => {
    setSelectedDate(date);
    fetchNewsletterData(date);
  };

  // Refresh data
  const refreshData = () => {
    fetchNewsletterData(selectedDate);
  };

  // Initial load
  useEffect(() => {
    const initializeData = async () => {
      await fetchAvailableDates();
      await fetchNewsletterData(null); // Load latest by default
    };
    
    initializeData();
  }, []);

  return {
    data,
    layout,
    availableDates,
    selectedDate,
    isLoading,
    error,
    selectDate,
    refreshData,
  };
}

