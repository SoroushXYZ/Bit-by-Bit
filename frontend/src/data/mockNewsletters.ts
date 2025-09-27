// Mock newsletter data for development
export interface Article {
  rank: number;
  title: string;
  summary: string;
  word_count: number;
  source: string;
  url: string;
  quality_score: number;
  quality_level: string;
  content_source: string;
  fallback_used: boolean;
}

export interface NewsletterContent {
  headlines: Article[];
  secondary: Article[];
  optional: Article[];
}

export interface NewsletterData {
  newsletter: {
    title: string;
    date: string;
    generated_at: string;
    pipeline_version: string;
  };
  content: NewsletterContent;
  statistics: {
    headlines_count: number;
    secondary_count: number;
    optional_count: number;
    data_reduction_percentage: number;
    average_quality_score: number;
    high_quality_percentage: number;
  };
}

export const mockNewsletters: NewsletterData[] = [
  {
    newsletter: {
      title: "Bit-by-Bit Tech Newsletter",
      date: "September 26, 2025",
      generated_at: "2025-09-26T02:47:56.169575",
      pipeline_version: "1.0.0"
    },
    content: {
      headlines: [
        {
          rank: 1,
          title: "Trump's H-1B Visa Fee Sparks Concerns Among Tech Firms",
          summary: "President Trump's new $100,000 fee for H-1B visas has sparked concerns among top tech firms like Amazon, Meta, and Microsoft, who rely on the program to hire foreign workers. The move could limit access to talent and hurt innovation in the long term.",
          word_count: 39,
          source: "Business Insider (Tech)",
          url: "https://www.businessinsider.com/business-leaders-react-trump-h-1b-visa-fee-2025-9",
          quality_score: 95.2,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 2,
          title: "Trump Signs Order to Allow American TikTok Buyout",
          summary: "President Trump signed an executive order allowing a US-based TikTok company, valued at $14 billion, with potential investors including Oracle and Rupert Murdoch. The move aims to create a separate entity from ByteDance, but critics argue it doesn't address core concerns about data control.",
          word_count: 39,
          source: "Daring Fireball",
          url: "https://www.nytimes.com/2025/09/25/technology/trump-tiktok-ban-deal.html",
          quality_score: 88.5,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 3,
          title: "Microsoft, Asus Open Preorders for Xbox Ally & Ally X Handhelds",
          summary: "Microsoft and Asus have launched preorders for the Xbox Ally ($599) and Ally X ($999), marking a significant entry into the handheld gaming market with unique features like Windows 11 and improved designs.",
          word_count: 39,
          source: "The Verge",
          url: "https://www.theverge.com/news/784286/xbox-handheld-ally-x-price-preorder",
          quality_score: 88.5,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 4,
          title: "Microsoft Develops Efficient Cooling Method for Chips",
          summary: "Microsoft has successfully tested a new cooling method, microfluidics, which can remove heat up to three times better than current methods. This could lead to more powerful chips and efficient data centers in the future.",
          word_count: 39,
          source: "The Verge",
          url: "https://www.theverge.com/report/785992/ai-chip-cooling-microsoft-microfluidic-energy-efficiency",
          quality_score: 88.8,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 5,
          title: "Spotify Cracks Down on AI-Generated Music Spam",
          summary: "Spotify introduces new policies to combat AI-generated music spam, aiming to protect artists and provide transparency to listeners.",
          word_count: 39,
          source: "Android Authority",
          url: "https://www.androidauthority.com/spotify-addresses-ai-slop-3601174/",
          quality_score: 88.3,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        }
      ],
      secondary: [
        {
          rank: 1,
          title: "Cloudflare Unveils Enhanced Developer Platform with New Features",
          summary: "Cloudflare introduces new capabilities, including improved Node.js support, AI Search with model diversity, and enhanced Remote Bindings for local development.",
          word_count: 29,
          source: "Cloudflare Blog",
          url: "https://blog.cloudflare.com/cloudflare-developer-platform-keeps-getting-better-faster-and-more-powerful/",
          quality_score: 88.5,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 2,
          title: "Recompose Expands Human Composting Beyond Seattle",
          summary: "Human composting startup Recompose is poised to grow beyond Seattle, with 13 states approving natural organic reduction, and plans to expand through franchising.",
          word_count: 29,
          source: "GeekWire",
          url: "https://www.geekwire.com/2025/inside-recompose-where-the-human-composting-startup-is-ready-to-grow-its-formula-beyond-seattle/",
          quality_score: 88.3,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 3,
          title: "Seattle Tech Execs Make Key Moves",
          summary: "Several Seattle-based startups and companies appointed or promoted executives, including CFOs, CBOs, and CEOs.",
          word_count: 29,
          source: "GeekWire",
          url: "https://www.geekwire.com/2025/seattle-tech-execs-make-key-moves/",
          quality_score: 85.0,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 4,
          title: "Amazon's New AI Assistant for Developers",
          summary: "Amazon launches a new AI-powered coding assistant that integrates with popular IDEs and provides real-time code suggestions and debugging help.",
          word_count: 29,
          source: "AWS News",
          url: "https://aws.amazon.com/about-aws/whats-new/2025/09/ai-coding-assistant/",
          quality_score: 87.2,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 5,
          title: "Google's Bard Gets Major Update with Code Generation",
          summary: "Google's Bard AI now includes advanced code generation capabilities, supporting multiple programming languages and frameworks.",
          word_count: 29,
          source: "Google AI Blog",
          url: "https://ai.googleblog.com/2025/09/bard-code-generation-update.html",
          quality_score: 86.8,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 6,
          title: "Meta's Quest 3 Pro Launches with Mixed Reality Focus",
          summary: "Meta's new Quest 3 Pro headset emphasizes mixed reality experiences with improved passthrough technology and hand tracking.",
          word_count: 29,
          source: "UploadVR",
          url: "https://uploadvr.com/meta-quest-3-pro-launch/",
          quality_score: 84.5,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 7,
          title: "NVIDIA's H200 GPU Targets AI Training Workloads",
          summary: "NVIDIA's new H200 GPU is specifically designed for AI training, offering significant performance improvements over previous generations.",
          word_count: 29,
          source: "NVIDIA News",
          url: "https://nvidianews.nvidia.com/news/nvidia-h200-gpu-ai-training/",
          quality_score: 89.1,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 8,
          title: "GitHub Copilot Enterprise Now Available",
          summary: "GitHub has launched Copilot Enterprise, offering advanced AI coding assistance for large organizations with enhanced security and compliance features.",
          word_count: 29,
          source: "GitHub Blog",
          url: "https://github.blog/2025-09-26-copilot-enterprise-launch/",
          quality_score: 85.7,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        }
      ],
      optional: [
        {
          rank: 1,
          title: "Discord Adds Voice Cloning for Custom Bots",
          summary: "Discord introduces voice cloning technology that allows users to create custom bot voices for their servers.",
          word_count: 29,
          source: "Discord Blog",
          url: "https://discord.com/blog/voice-cloning-bots/",
          quality_score: 82.3,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 2,
          title: "Twitch Implements New Content Moderation AI",
          summary: "Twitch has deployed a new AI system for content moderation, improving platform safety and user experience.",
          word_count: 29,
          source: "Twitch Blog",
          url: "https://blog.twitch.tv/ai-content-moderation/",
          quality_score: 79.8,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 3,
          title: "Reddit's API Changes Impact Third-Party Apps",
          summary: "Reddit's recent API changes have significantly impacted third-party mobile apps, leading to service disruptions.",
          word_count: 29,
          source: "Reddit Blog",
          url: "https://www.reddit.com/r/reddit/comments/api-changes-impact/",
          quality_score: 77.2,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 4,
          title: "Pinterest's Visual Search Gets AI Enhancement",
          summary: "Pinterest has enhanced its visual search capabilities with new AI features for better image recognition and recommendations.",
          word_count: 29,
          source: "Pinterest Engineering",
          url: "https://medium.com/pinterest-engineering/visual-search-ai-enhancement/",
          quality_score: 75.6,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 5,
          title: "LinkedIn's AI Writing Assistant Now in Beta",
          summary: "LinkedIn has launched a beta version of its AI writing assistant to help users create better professional content.",
          word_count: 29,
          source: "LinkedIn Engineering",
          url: "https://engineering.linkedin.com/ai-writing-assistant-beta/",
          quality_score: 73.4,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 6,
          title: "TikTok's Algorithm Updates Focus on Educational Content",
          summary: "TikTok has updated its algorithm to prioritize educational and informative content over entertainment videos.",
          word_count: 29,
          source: "TikTok Newsroom",
          url: "https://newsroom.tiktok.com/algorithm-educational-content/",
          quality_score: 71.8,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 7,
          title: "Snapchat's AR Lenses Now Support Real-Time Translation",
          summary: "Snapchat has added real-time translation capabilities to its AR lenses, breaking down language barriers in conversations.",
          word_count: 29,
          source: "Snapchat News",
          url: "https://newsroom.snapchat.com/ar-lenses-translation/",
          quality_score: 69.3,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        }
      ]
    },
    statistics: {
      headlines_count: 5,
      secondary_count: 8,
      optional_count: 7,
      data_reduction_percentage: 96.3,
      average_quality_score: 88.7,
      high_quality_percentage: 85.0
    }
  },
  {
    newsletter: {
      title: "Bit-by-Bit Tech Newsletter",
      date: "September 25, 2025",
      generated_at: "2025-09-25T02:47:56.169575",
      pipeline_version: "1.0.0"
    },
    content: {
      headlines: [
        {
          rank: 1,
          title: "Apple Unveils Revolutionary AI Chip for Mac Pro",
          summary: "Apple has announced a groundbreaking AI chip for the Mac Pro that promises 10x performance improvements in machine learning tasks, revolutionizing professional workflows and creative applications.",
          word_count: 39,
          source: "TechCrunch",
          url: "https://techcrunch.com/2025/09/25/apple-ai-chip-mac-pro",
          quality_score: 94.8,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 2,
          title: "OpenAI Releases GPT-5 with Multimodal Capabilities",
          summary: "OpenAI has launched GPT-5 with advanced multimodal capabilities, including real-time video analysis, code generation, and enhanced reasoning abilities that surpass previous models.",
          word_count: 39,
          source: "The Verge",
          url: "https://www.theverge.com/2025/09/25/openai-gpt-5-release",
          quality_score: 92.3,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 3,
          title: "Tesla's Full Self-Driving Beta Reaches 99.9% Safety Record",
          summary: "Tesla's Full Self-Driving beta has achieved a 99.9% safety record across 1 million miles of testing, marking a significant milestone in autonomous vehicle development.",
          word_count: 39,
          source: "Ars Technica",
          url: "https://arstechnica.com/2025/09/25/tesla-fsd-beta-safety-record",
          quality_score: 89.7,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 4,
          title: "Google's Quantum Computer Achieves Quantum Supremacy",
          summary: "Google's latest quantum computer has achieved quantum supremacy by solving a problem that would take classical computers 10,000 years in just 200 seconds.",
          word_count: 39,
          source: "WIRED",
          url: "https://www.wired.com/2025/09/25/google-quantum-supremacy",
          quality_score: 91.2,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 5,
          title: "Microsoft's Copilot Pro Now Available for Enterprise",
          summary: "Microsoft has launched Copilot Pro for enterprise customers, offering advanced AI assistance across Office 365, Teams, and Azure with enhanced security and compliance features.",
          word_count: 39,
          source: "Engadget",
          url: "https://www.engadget.com/2025/09/25/microsoft-copilot-pro-enterprise",
          quality_score: 87.5,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        }
      ],
      secondary: [
        {
          rank: 1,
          title: "NVIDIA's RTX 5090 Sets New Performance Benchmarks",
          summary: "NVIDIA's RTX 5090 graphics card delivers unprecedented performance in gaming and AI workloads, setting new industry standards.",
          word_count: 29,
          source: "PC Gamer",
          url: "https://www.pcgamer.com/2025/09/25/nvidia-rtx-5090-benchmarks",
          quality_score: 88.9,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 2,
          title: "Amazon's Project Kuiper Launches First Satellites",
          summary: "Amazon has successfully launched the first batch of Project Kuiper satellites, marking the beginning of its global internet constellation.",
          word_count: 29,
          source: "Space.com",
          url: "https://www.space.com/2025/09/25/amazon-kuiper-satellites-launch",
          quality_score: 86.7,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 3,
          title: "Meta's Horizon Worlds Gets Major VR Update",
          summary: "Meta has released a significant update to Horizon Worlds, introducing new social features and improved VR experiences.",
          word_count: 29,
          source: "UploadVR",
          url: "https://uploadvr.com/2025/09/25/meta-horizon-worlds-update",
          quality_score: 84.3,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 4,
          title: "Spotify's AI DJ Now Available in 50 Countries",
          summary: "Spotify has expanded its AI DJ feature to 50 countries, offering personalized music recommendations powered by machine learning.",
          word_count: 29,
          source: "The Verge",
          url: "https://www.theverge.com/2025/09/25/spotify-ai-dj-expansion",
          quality_score: 82.1,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 5,
          title: "Intel's 14th Gen Processors Show 15% Performance Boost",
          summary: "Intel's 14th generation processors demonstrate a 15% performance improvement over previous generations in benchmark tests.",
          word_count: 29,
          source: "Tom's Hardware",
          url: "https://www.tomshardware.com/2025/09/25/intel-14th-gen-performance",
          quality_score: 85.6,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 6,
          title: "GitHub Copilot Chat Now Supports 20 Programming Languages",
          summary: "GitHub has expanded Copilot Chat support to 20 programming languages, enhancing developer productivity across diverse tech stacks.",
          word_count: 29,
          source: "GitHub Blog",
          url: "https://github.blog/2025/09/25/copilot-chat-20-languages",
          quality_score: 83.4,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 7,
          title: "Samsung's Galaxy S25 Ultra Features 200MP Camera",
          summary: "Samsung's upcoming Galaxy S25 Ultra will feature a 200MP main camera with advanced AI photography capabilities.",
          word_count: 29,
          source: "Android Authority",
          url: "https://www.androidauthority.com/2025/09/25/samsung-galaxy-s25-ultra-camera",
          quality_score: 81.8,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 8,
          title: "Cloudflare's Workers Platform Hits 10 Million Deployments",
          summary: "Cloudflare's Workers platform has reached 10 million deployments, showcasing the growth of edge computing adoption.",
          word_count: 29,
          source: "Cloudflare Blog",
          url: "https://blog.cloudflare.com/2025/09/25/workers-10-million-deployments",
          quality_score: 79.2,
          quality_level: "excellent",
          content_source: "full_content",
          fallback_used: false
        }
      ],
      optional: [
        {
          rank: 1,
          title: "Discord Adds Screen Share with AI Noise Cancellation",
          summary: "Discord introduces screen sharing with AI-powered noise cancellation for clearer communication during gaming sessions.",
          word_count: 29,
          source: "Discord Blog",
          url: "https://discord.com/blog/2025/09/25/screen-share-ai-noise-cancellation",
          quality_score: 77.5,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 2,
          title: "Twitch Implements New Content Moderation AI",
          summary: "Twitch has deployed a new AI system for content moderation, improving platform safety and user experience.",
          word_count: 29,
          source: "Twitch Blog",
          url: "https://blog.twitch.tv/2025/09/25/ai-content-moderation",
          quality_score: 75.8,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 3,
          title: "Reddit's API Changes Impact Third-Party Apps",
          summary: "Reddit's recent API changes have significantly impacted third-party mobile apps, leading to service disruptions.",
          word_count: 29,
          source: "Reddit Blog",
          url: "https://www.reddit.com/r/reddit/comments/2025/09/25/api-changes-impact",
          quality_score: 73.2,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 4,
          title: "Pinterest's Visual Search Gets AI Enhancement",
          summary: "Pinterest has enhanced its visual search capabilities with new AI features for better image recognition and recommendations.",
          word_count: 29,
          source: "Pinterest Engineering",
          url: "https://medium.com/pinterest-engineering/2025/09/25/visual-search-ai-enhancement",
          quality_score: 71.6,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 5,
          title: "LinkedIn's AI Writing Assistant Now in Beta",
          summary: "LinkedIn has launched a beta version of its AI writing assistant to help users create better professional content.",
          word_count: 29,
          source: "LinkedIn Engineering",
          url: "https://engineering.linkedin.com/2025/09/25/ai-writing-assistant-beta",
          quality_score: 69.4,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 6,
          title: "TikTok's Algorithm Updates Focus on Educational Content",
          summary: "TikTok has updated its algorithm to prioritize educational and informative content over entertainment videos.",
          word_count: 29,
          source: "TikTok Newsroom",
          url: "https://newsroom.tiktok.com/2025/09/25/algorithm-educational-content",
          quality_score: 67.8,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        },
        {
          rank: 7,
          title: "Snapchat's AR Lenses Now Support Real-Time Translation",
          summary: "Snapchat has added real-time translation capabilities to its AR lenses, breaking down language barriers in conversations.",
          word_count: 29,
          source: "Snapchat News",
          url: "https://newsroom.snapchat.com/2025/09/25/ar-lenses-translation",
          quality_score: 65.3,
          quality_level: "good",
          content_source: "full_content",
          fallback_used: false
        }
      ]
    },
    statistics: {
      headlines_count: 5,
      secondary_count: 8,
      optional_count: 7,
      data_reduction_percentage: 95.8,
      average_quality_score: 82.4,
      high_quality_percentage: 78.5
    }
  }
];

// Helper function to get newsletter by date
export function getNewsletterByDate(date: string): NewsletterData | null {
  return mockNewsletters.find(newsletter => newsletter.newsletter.date === date) || null;
}

// Helper function to get latest newsletter
export function getLatestNewsletter(): NewsletterData {
  return mockNewsletters[0]; // First item is latest
}

// Helper function to get all newsletters for archive
export function getAllNewsletters(): NewsletterData[] {
  return mockNewsletters;
}

// Helper function to get archive data for navigation
export function getArchiveData() {
  return mockNewsletters.map(newsletter => ({
    date: newsletter.newsletter.date,
    title: newsletter.newsletter.title,
    articles_count: newsletter.statistics.headlines_count + 
                   newsletter.statistics.secondary_count + 
                   newsletter.statistics.optional_count,
    quality_score: newsletter.statistics.average_quality_score,
    status: 'completed',
    file_size: '2.3 MB',
    generated_at: newsletter.newsletter.generated_at,
    headlines: newsletter.content.headlines.slice(0, 3).map(h => ({
      title: h.title,
      source: h.source
    }))
  }));
}
