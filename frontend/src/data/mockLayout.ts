import { NewsletterLayout, Component } from '@/types/components';

export const mockNewsletterLayout: NewsletterLayout = {
  gridConfig: {
    columns: 12,
    rows: 16,
    cellSize: 48
  },
  components: [
    // BIT - 2x2 branding
    {
      id: 'bit-1',
      type: 'branding',
      position: { row: 1, column: 1, width: 2, height: 2 },
      clickable: false,
      text: 'BIT',
      variant: 'bit'
    },
    
    // Headline news - 8x3
    {
      id: 'headline-1',
      type: 'headline',
      position: { row: 1, column: 3, width: 6, height: 4 },
      clickable: true,
      url: 'https://example.com/headline-1',
      title: 'OpenAI Releases GPT-5 with Revolutionary Reasoning Capabilities',
      description: 'The new model shows unprecedented logical reasoning and can solve complex problems previously thought impossible for AI. This breakthrough represents a significant leap forward in artificial intelligence research.',
      source: 'TechCrunch',
      publishedAt: '2025-01-27T10:00:00Z',
      priority: 1
    },
    
    // BY - 2x2 branding (moved to avoid overlap)
    {
      id: 'by',
      type: 'branding',
      position: { row: 4, column: 10, width: 2, height: 2 },
      clickable: false,
      text: 'BY',
      variant: 'by'
    },
    
    // Secondary news - 6x2
    {
      id: 'secondary-1',
      type: 'secondary',
      position: { row: 5, column: 1, width: 6, height: 3 },
      clickable: true,
      url: 'https://example.com/secondary-1',
      title: 'Tesla Announces Fully Autonomous Driving Rollout',
      description: 'Level 5 autonomy now available in major cities w autonomy now available in major cities w autonomy now available in major cities w autonomy now available in major cities with regulatory approval.',
      source: 'Reuters',
      publishedAt: '2025-01-27T09:30:00Z',
      priority: 2
    },
    
    // Quick Link - 4x1
    {
      id: 'quicklink-1',
      type: 'quickLink',
      position: { row: 10, column: 1, width: 6, height: 1 },
      clickable: true,
      url: 'https://example.com/quicklink',
      title: 'Hugging Face Releases Smol2Operator: GUI Training Pipeline'
    },
    
    // BIT (final) - 2x2 branding
    {
      id: 'bit-final',
      type: 'branding',
      position: { row: 10, column: 7, width: 2, height: 2 },
      clickable: false,
      text: 'BIT',
      variant: 'bit-final'
    }
  ]
};
