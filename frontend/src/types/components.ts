export interface GridPosition {
  row: number;
  column: number;
  width: number;
  height: number;
}

export interface BaseComponent {
  id: string;
  type: 'headline' | 'secondary' | 'quickLinks' | 'branding' | 'stock' | 'image' | 'icon';
  position: GridPosition;
  clickable: boolean;
  url?: string;
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
  description?: string;
}

export interface BrandingComponent extends BaseComponent {
  type: 'branding';
  text: string;
  variant: 'bit' | 'by' | 'bit-final';
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

export type Component = 
  | HeadlineComponent 
  | SecondaryComponent 
  | QuickLinkComponent 
  | BrandingComponent
  | StockComponent
  | ImageComponent
  | IconComponent;

export interface NewsletterLayout {
  components: Component[];
  gridConfig: {
    columns: number;
    rows: number;
    cellSize: number;
  };
}
