export interface Article {
  id: string;
  title: string;
  source: string;
  url: string;
  summary?: string;
  publishedAt: string;
  category: 'headlines' | 'secondary' | 'optional';
  priority: number;
}

export interface NewsletterContent {
  headlines: Article[];
  secondary: Article[];
  optional: Article[];
  quickLinks: {
    title: string;
    url: string;
    description?: string;
  }[];
}

export interface NewsletterData {
  id: string;
  date: string;
  title: string;
  generatedAt: string;
  pipelineVersion: string;
  content: NewsletterContent;
}

export interface GridPosition {
  row: number;
  column: number;
  width: number;
  height: number;
}

export interface ContentBlock {
  id: string;
  type: 'headline' | 'secondary' | 'optional' | 'quickLinks' | 'decoration';
  content: Article | Article[] | any;
  position: GridPosition;
  priority: number;
}
