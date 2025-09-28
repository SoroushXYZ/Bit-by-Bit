import { NewsletterLayout, Component } from '@/types/components';

export const mockNewsletterLayout: NewsletterLayout = {
  "gridConfig": {
    "columns": 12,
    "rows": 16,
    "cellSize": 48
  },
  "components": [
    {
      "id": "headline_1",
      "type": "headline",
      "position": {
        "row": 1,
        "column": 1,
        "width": 5,
        "height": 4
      },
      "clickable": true,
      "url": "https://siliconvalleyjournals.com/anything-raises-11m-series-a-at-100m-valuation/",
      "title": "Anything Raises $11M Series A at $100M Valuation",
      "description": "AI platform Anything raises $11M in Series A funding, valuing it at $100M, as it solves the retention problem common to AI coding tools by shipping apps that launch and scale.",
      "source": "Silicon Valley Journals",
      "publishedAt": "2025-09-27T10:00:00Z",
      "priority": 1
    },
    {
      "id": "headline_2",
      "type": "headline",
      "position": {
        "row": 1,
        "column": 7,
        "width": 5,
        "height": 4
      },
      "clickable": true,
      "url": "https://www.theverge.com/reviews/786538/raleigh-one-e-bike-review-vanmoof-carlier-ties-taco",
      "title": "Raleigh Unveils Raleigh One e-Bike with Anti-Theft Features",
      "description": "The Raleigh One e-bike, developed by VanMoof's founders, offers anti-theft features like GPS tracking and wide tires, making it a commuter's dream. Lessons learned from VanMoof's bankruptcy are applied to create a more serviceable bike.",
      "source": "The Verge",
      "publishedAt": "2025-09-27T09:30:00Z",
      "priority": 1
    },
    {
      "id": "headline_3",
      "type": "headline",
      "position": {
        "row": 5,
        "column": 1,
        "width": 6,
        "height": 4
      },
      "clickable": true,
      "url": "https://tech.slashdot.org/story/25/09/26/1843257/abu-dhabi-royal-family-to-take-stake-in-tiktok-us?utm_source=rss1.0mainlinkanon&utm_medium=feed",
      "title": "TikTok US Under US Ownership After Trump's Executive Order",
      "description": "Abu Dhabi's MGX to take 15% stake in TikTok US, valued at $14 billion. The deal aims to protect American data privacy and ensure secure operation of the platform.",
      "source": "Slashdot",
      "publishedAt": "2025-09-27T08:45:00Z",
      "priority": 1
    },
    {
      "id": "secondary_1",
      "type": "secondary",
      "position": {
        "row": 5,
        "column": 7,
        "width": 6,
        "height": 3
      },
      "clickable": true,
      "url": "https://www.androidauthority.com/google-home-powerful-automations-still-not-using-them-3600343/",
      "title": "Google Home Automation Falls Short Despite New Features",
      "description": "Google's new automation editor offers some improvements, but limitations persist.",
      "source": "Android Authority",
      "publishedAt": "2025-09-27T07:15:00Z",
      "priority": 2
    },
    {
      "id": "secondary_2",
      "type": "secondary",
      "position": {
        "row": 8,
        "column": 7,
        "width": 6,
        "height": 3
      },
      "clickable": true,
      "url": "https://daringfireball.net/2025/09/apple_on_the_digital_markets_act",
      "title": "Apple Faces EU Regulatory Headwinds Under Digital Markets Act",
      "description": "Apple delays features like Live Translation with AirPods due to EU regulatory requirements, sparking concerns over data protection and choice.",
      "source": "Daring Fireball",
      "publishedAt": "2025-09-27T06:30:00Z",
      "priority": 2
    },
    {
      "id": "secondary_3",
      "type": "secondary",
      "position": {
        "row": 9,
        "column": 1,
        "width": 6,
        "height": 3
      },
      "clickable": true,
      "url": "https://www.businessinsider.com/aldi-grocery-outlet-small-supermarkets-are-latest-front-grocery-wars-2025-9",
      "title": "Small Grocery Stores Gain Ground in US Market",
      "description": "Aldi, Grocery Outlet, and other small-format grocers plan hundreds of store openings, focusing on efficiency and curated product selection.",
      "source": "Business Insider",
      "publishedAt": "2025-09-27T05:45:00Z",
      "priority": 2
    },
    {
      "id": "quick_link_1",
      "type": "quickLink",
      "position": {
        "row": 11,
        "column": 7,
        "width": 4,
        "height": 2
      },
      "clickable": true,
      "url": "https://www.marktechpost.com/2025/09/26/how-to-build-an-intelligent-ai-desktop-automation-agent-with-natural-language-commands-and-interactive-simulation/",
      "title": "Build AI Desktop Automation Automation Automation Automation A Automation gent with Natural Language Commands"
    },
    {
      "id": "quick_link_2",
      "type": "quickLink",
      "position": {
        "row": 12,
        "column": 1,
        "width": 5,
        "height": 1
      },
      "clickable": true,
      "url": "https://9to5mac.com/2025/09/26/deals-apple-watch-ultra-3-se-3-series-11-airtag/",
      "title": "Early Launch Discounts"
    },
    {
      "id": "quick_link_3",
      "type": "quickLink",
      "position": {
        "row": 12,
        "column": 7,
        "width": 4,
        "height": 2
      },
      "clickable": true,
      "url": "https://mashable.com/article/alien-earth-xenomorph-design-intervew",
      "title": "Alien: Earth's Revolutionary Xenomorph Design Completely Transforms the Franchise"
    },
    {
      "id": "branding_1",
      "type": "branding",
      "position": {
        "row": 13,
        "column": 1,
        "width": 2,
        "height": 2
      },
      "clickable": false,
      "text": "BIT",
      "variant": "bit"
    },
    {
      "id": "branding_2",
      "type": "branding",
      "position": {
        "row": 13,
        "column": 3,
        "width": 2,
        "height": 2
      },
      "clickable": false,
      "text": "BY",
      "variant": "by"
    },
    {
      "id": "branding_3",
      "type": "branding",
      "position": {
        "row": 13,
        "column": 5,
        "width": 2,
        "height": 2
      },
      "clickable": false,
      "text": "BIT",
      "variant": "bit-final"
    },
    {
      "id": "git_repo_1",
      "type": "gitRepo",
      "position": {
        "row": 9,
        "column": 7,
        "width": 3,
        "height": 3
      },
      "clickable": true,
      "url": "https://github.com/microsoft/vscode",
      "name": "microsoft/vscode",
      "stars": 156000,
      "description": "Visual Studio Code is a lightweight but powerful source code editor which runs on your desktop and is available for Windows, macOS and Linux."
    }
  ]
};
