import { NewsletterContent, Article } from '@/types/newsletter';

const mockArticles: Article[] = [
  // Headlines
  {
    id: 'h1',
    title: 'OpenAI Releases GPT-5 with Revolutionary Reasoning Capabilities',
    source: 'TechCrunch',
    url: 'https://example.com',
    summary: 'The new model shows unprecedented logical reasoning and can solve complex problems previously thought impossible for AI.',
    publishedAt: '2025-01-27T10:00:00Z',
    category: 'headlines',
    priority: 1
  },
  {
    id: 'h2',
    title: 'Tesla Announces Fully Autonomous Driving Rollout in Major Cities',
    source: 'Reuters',
    url: 'https://example.com',
    summary: 'Level 5 autonomy now available in San Francisco, Austin, and Phoenix with regulatory approval.',
    publishedAt: '2025-01-27T09:30:00Z',
    category: 'headlines',
    priority: 2
  },
  {
    id: 'h3',
    title: 'Microsoft Acquires Leading AI Startup for $50 Billion',
    source: 'Bloomberg',
    url: 'https://example.com',
    summary: 'Major consolidation in the AI space as Microsoft expands its AI capabilities.',
    publishedAt: '2025-01-27T08:15:00Z',
    category: 'headlines',
    priority: 3
  },

  // Secondary
  {
    id: 's1',
    title: 'New Quantum Computing Breakthrough Achieves 1000-Qubit System',
    source: 'Nature',
    url: 'https://example.com',
    summary: 'Researchers demonstrate stable quantum operations at unprecedented scale.',
    publishedAt: '2025-01-27T07:45:00Z',
    category: 'secondary',
    priority: 4
  },
  {
    id: 's2',
    title: 'Apple Unveils Revolutionary AR Glasses with Neural Interface',
    source: 'The Verge',
    url: 'https://example.com',
    summary: 'Next-generation wearable combines augmented reality with direct neural input.',
    publishedAt: '2025-01-27T06:30:00Z',
    category: 'secondary',
    priority: 5
  },
  {
    id: 's3',
    title: 'Google Launches Advanced AI-Powered Search Engine',
    source: 'Wired',
    url: 'https://example.com',
    summary: 'New search capabilities understand context and intent like never before.',
    publishedAt: '2025-01-27T05:20:00Z',
    category: 'secondary',
    priority: 6
  },
  {
    id: 's4',
    title: 'SpaceX Successfully Tests Starship Mars Mission Prototype',
    source: 'Space.com',
    url: 'https://example.com',
    summary: 'Major milestone in humanity\'s journey to become a multi-planetary species.',
    publishedAt: '2025-01-27T04:10:00Z',
    category: 'secondary',
    priority: 7
  },

  // Optional
  {
    id: 'o1',
    title: 'AI-Generated Art Wins International Photography Award',
    source: 'ArtNews',
    url: 'https://example.com',
    summary: 'Controversial win sparks debate about the nature of creativity and authorship.',
    publishedAt: '2025-01-27T03:00:00Z',
    category: 'optional',
    priority: 8
  },
  {
    id: 'o2',
    title: 'Startup Creates AI That Can Predict Stock Market Movements',
    source: 'Forbes',
    url: 'https://example.com',
    summary: 'Algorithm shows 85% accuracy in predicting market trends over 30-day periods.',
    publishedAt: '2025-01-27T02:15:00Z',
    category: 'optional',
    priority: 9
  },
  {
    id: 'o3',
    title: 'New Study Shows AI Can Detect Diseases Earlier Than Doctors',
    source: 'Medical Journal',
    url: 'https://example.com',
    summary: 'Machine learning models identify patterns invisible to human observation.',
    publishedAt: '2025-01-27T01:30:00Z',
    category: 'optional',
    priority: 10
  },
  {
    id: 'o4',
    title: 'Robotic Chef Opens Restaurant in Tokyo with Zero Human Staff',
    source: 'Japan Times',
    url: 'https://example.com',
    summary: 'Fully automated dining experience showcases the future of food service.',
    publishedAt: '2025-01-27T00:45:00Z',
    category: 'optional',
    priority: 11
  }
];

export const mockNewsletterContent: NewsletterContent = {
  headlines: mockArticles.filter(article => article.category === 'headlines'),
  secondary: mockArticles.filter(article => article.category === 'secondary'),
  optional: mockArticles.filter(article => article.category === 'optional'),
  quickLinks: [
    {
      title: 'AI Research Papers',
      url: 'https://example.com',
      description: 'Latest academic publications'
    },
    {
      title: 'Tech Job Board',
      url: 'https://example.com',
      description: 'Find your next role'
    },
    {
      title: 'Developer Resources',
      url: 'https://example.com',
      description: 'Tools and tutorials'
    },
    {
      title: 'Industry Reports',
      url: 'https://example.com',
      description: 'Market analysis and trends'
    }
  ]
};
