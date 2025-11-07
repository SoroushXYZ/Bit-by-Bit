import React, { createContext, useContext, ReactNode } from 'react';
import { useNewsletterData } from '@/hooks/useNewsletterData';

interface NewsletterContextType {
  data: any;
  layout: any;
  availableDates: string[];
  selectedDate: string | null;
  newsletterDate: string | null;
  isLoading: boolean;
  error: string | null;
  selectDate: (date: string | null) => void;
  refreshData: () => void;
}

const NewsletterContext = createContext<NewsletterContextType | undefined>(undefined);

export function NewsletterProvider({ children }: { children: ReactNode }) {
  const newsletterData = useNewsletterData();

  return (
    <NewsletterContext.Provider value={newsletterData}>
      {children}
    </NewsletterContext.Provider>
  );
}

export function useNewsletterContext() {
  const context = useContext(NewsletterContext);
  if (context === undefined) {
    throw new Error('useNewsletterContext must be used within a NewsletterProvider');
  }
  return context;
}

