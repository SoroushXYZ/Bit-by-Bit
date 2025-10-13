import { useState, useEffect } from 'react';
import { NewsletterLayout } from '@/types/components';
import { parsePipelineLayout } from '@/lib/parsePipelineLayout';

interface UseNewsletterDataReturn {
  layout: NewsletterLayout | null;
  availableDates: string[];
  selectedDate: string | null;
  isLoading: boolean;
  error: string | null;
  selectDate: (date: string | null) => void;
  refreshData: () => void;
}

export function useNewsletterData(): UseNewsletterDataReturn {
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
      const data = await response.json();
      setAvailableDates(data.dates || []);
    } catch (err) {
      console.error('Failed to fetch available dates:', err);
      setError('Failed to load available dates');
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
        throw new Error(`Failed to fetch newsletter: ${response.status}`);
      }
      
      const backendData = await response.json();
      const transformedLayout = parsePipelineLayout(backendData);
      setLayout(transformedLayout);
    } catch (err) {
      console.error('Failed to fetch newsletter data:', err);
      setError(`Failed to load newsletter data: ${err instanceof Error ? err.message : 'Unknown error'}`);
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
    layout,
    availableDates,
    selectedDate,
    isLoading,
    error,
    selectDate,
    refreshData
  };
}
