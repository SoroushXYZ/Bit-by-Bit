export interface GridPosition {
  row: number;
  column: number;
  width: number;
  height: number;
}

export interface BaseComponent {
  id: string;
  type: 'headline' | 'secondary' | 'quickLink' | 'branding' | 'gitRepo' | 'stock' | 'image' | 'icon' | 'bit' | 'day';
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
  data?: any; // For future chart data
}

export interface ImageComponent extends BaseComponent {
  type: 'image';
  src: string;
  alt: string;
  caption?: string;
}

export interface IconComponent extends BaseComponent {
  type: 'icon';
  icon: string; // Icon name or emoji
  label?: string;
  color?: string;
}

export interface BitComponent extends BaseComponent {
  type: 'bit';
  value: 0 | 1;
}

export interface DayComponent extends BaseComponent {
  type: 'day';
  day: string; // e.g., Monday
  number: number; // e.g., 10
}

export type Component = 
  | HeadlineComponent 
  | SecondaryComponent 
  | QuickLinkComponent 
  | BrandingComponent
  | GitRepoComponent
  | StockComponent
  | ImageComponent
  | IconComponent
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
