export interface GridPosition {
  row: number;
  column: number;
  width: number;
  height: number;
}

export interface BaseComponent {
  id: string;
  type: 'headline' | 'secondary' | 'quickLink' | 'branding' | 'gitRepo' | 'stock' | 'bit' | 'day';
  position: GridPosition;
  clickable: boolean;
  url?: string | null;
}

export interface HeadlineComponent extends BaseComponent {
  type: 'headline';
  title: string;
  description: string;
  source: string;
  publishedAt: string;
  priority: number;
}

export interface SecondaryComponent extends BaseComponent {
  type: 'secondary';
  title: string;
  description: string;
  source: string;
  publishedAt: string;
  priority: number;
}

export interface QuickLinkComponent extends BaseComponent {
  type: 'quickLink';
  title: string;
  summary?: string;
}

export interface BrandingComponent extends BaseComponent {
  type: 'branding';
  text: string;
  variant: 'bit' | 'by' | 'bit-final';
}

export interface GitRepoComponent extends BaseComponent {
  type: 'gitRepo';
  name: string;
  stars: number;
  description: string;
}

export interface StockComponent extends BaseComponent {
  type: 'stock';
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

export interface BitComponent extends BaseComponent {
  type: 'bit';
  value: 0 | 1;
}

export interface DayComponent extends BaseComponent {
  type: 'day';
  day: string;
  number: number;
}

export type Component = 
  | HeadlineComponent 
  | SecondaryComponent 
  | QuickLinkComponent 
  | BrandingComponent
  | GitRepoComponent
  | StockComponent
  | BitComponent
  | DayComponent;

export interface NewsletterLayout {
  components: Component[];
  gridConfig: {
    columns: number;
    rows: number;
    cellSize: number;
  };
}

