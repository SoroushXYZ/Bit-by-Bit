import { 
  NewsletterLayout, 
  Component, 
  HeadlineComponent, 
  SecondaryComponent, 
  QuickLinkComponent, 
  BrandingComponent, 
  GitRepoComponent, 
  StockComponent, 
  BitComponent, 
  DayComponent 
} from '@/types/components';

interface BackendComponent {
  id: string;
  type: 'bit' | 'branding' | 'day_number' | 'github_repo' | 'headline' | 'quick_link' | 'stock';
  position: {
    row: number;
    column: number;
    width: number;
    height: number;
  };
  data: any;
}

interface BackendResponse {
  status: string;
  run_id: string;
  date: string;
  grid_data: {
    metadata: {
      generated_at: string;
      grid_config: {
        columns: number;
        rows: number;
        cell_size: number;
      };
      total_components: number;
      efficiency: number;
    };
    components: BackendComponent[];
  };
}

export function parsePipelineLayout(data: BackendResponse): NewsletterLayout {
  const { grid_data } = data;
  
  // Transform grid config
  const gridConfig = {
    columns: grid_data.metadata.grid_config.columns,
    rows: grid_data.metadata.grid_config.rows,
    cellSize: grid_data.metadata.grid_config.cell_size
  };

  // Transform components
  const components: Component[] = grid_data.components.map(transformBackendComponent);

  return {
    gridConfig,
    components
  };
}

function transformBackendComponent(backendComp: BackendComponent): Component {
  const baseComponent = {
    id: backendComp.id,
    position: backendComp.position,
    clickable: !!backendComp.data.url,
    url: backendComp.data.url || null
  };

  switch (backendComp.type) {
    case 'headline':
      return {
        ...baseComponent,
        type: 'headline',
        title: backendComp.data.title || '',
        description: backendComp.data.summary || '',
        source: backendComp.data.source || '',
        publishedAt: new Date().toISOString(),
        priority: 1
      } as HeadlineComponent;

    case 'quick_link':
      return {
        ...baseComponent,
        type: 'quickLink',
        title: backendComp.data.title || '',
        summary: backendComp.data.summary || backendComp.data.description || undefined
      } as QuickLinkComponent;

    case 'branding':
      const brandingText = getBrandingText(backendComp.data.order_id);
      return {
        ...baseComponent,
        type: 'branding',
        text: brandingText,
        variant: getBrandingVariant(backendComp.data.order_id),
        clickable: false,
        url: null
      } as BrandingComponent;

    case 'github_repo':
      return {
        ...baseComponent,
        type: 'gitRepo',
        name: backendComp.data.name || '',
        stars: backendComp.data.stars || 0,
        description: backendComp.data.description || ''
      } as GitRepoComponent;

    case 'stock':
      return {
        ...baseComponent,
        type: 'stock',
        symbol: backendComp.data.symbol || '',
        price: backendComp.data.price || 0,
        change: backendComp.data.change || 0,
        changePercent: backendComp.data.change_percent || 0
      } as StockComponent;

    case 'bit':
      return {
        ...baseComponent,
        type: 'bit',
        value: backendComp.data.value || 0,
        clickable: false,
        url: null
      } as BitComponent;

    case 'day_number':
      return {
        ...baseComponent,
        type: 'day',
        day: backendComp.data.day || 'Monday',
        number: backendComp.data.number || 1,
        clickable: false,
        url: null
      } as DayComponent;

    default:
      console.warn(`Unknown backend component type: ${backendComp.type}`);
      return {
        ...baseComponent,
        type: 'quickLink',
        title: `Unknown: ${backendComp.type}`
      } as QuickLinkComponent;
  }
}

function getBrandingText(orderId: number): string {
  switch (orderId) {
    case 1:
    case 3:
      return 'BIT';
    case 2:
      return 'BY';
    default:
      return 'BIT';
  }
}

function getBrandingVariant(orderId: number): 'bit' | 'by' | 'bit-final' {
  switch (orderId) {
    case 1:
      return 'bit';
    case 2:
      return 'by';
    case 3:
      return 'bit-final';
    default:
      return 'bit';
  }
}

