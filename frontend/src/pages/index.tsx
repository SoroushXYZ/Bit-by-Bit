import Layout from "@/components/layout/Layout";
import DynamicGridLayout from "@/components/layout/DynamicGridLayout";
import { parsePipelineLayout } from "@/lib/parsePipelineLayout";
import type { NewsletterLayout } from "@/types/components";
import { mockNewsletterLayout } from "@/data/mockLayout";

interface HomeProps {
  layout: NewsletterLayout;
  error?: string;
}

export default function Home({ layout, error }: HomeProps) {
  if (error) {
    return (
      <Layout>
        <div className="min-h-screen bg-background p-4">
          <div className="max-w-5xl mx-auto">
            <div className="bg-card border rounded-lg shadow-lg p-8 text-center">
              <h1 className="text-2xl font-bold text-destructive mb-4">Error Loading Newsletter</h1>
              <p className="text-muted-foreground mb-4">{error}</p>
              <p className="text-sm text-muted-foreground">
                Falling back to mock data for demonstration purposes.
              </p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <DynamicGridLayout layout={layout} />
    </Layout>
  );
}

export async function getServerSideProps() {
  try {
    // Try to fetch from backend API first
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${apiBaseUrl}/newsletter/grid`);
    
    if (!response.ok) {
      throw new Error(`Backend API returned ${response.status}: ${response.statusText}`);
    }
    
    const backendData = await response.json();
    const layout = parsePipelineLayout(backendData);
    return { props: { layout } };
    
  } catch (error) {
    console.error('Failed to fetch from backend API:', error);
    
    // Fallback: try to read from environment variable
    try {
      const gridJson = process.env.GRID_JSON;
      if (gridJson) {
        const parsed = JSON.parse(gridJson);
        const layout = parsePipelineLayout(parsed);
        return { props: { layout } };
      }
    } catch (e) {
      console.error('Failed to parse GRID_JSON:', e);
    }
    
    // Final fallback: return mock data with error message
    return { 
      props: { 
        layout: mockNewsletterLayout,
        error: `Unable to connect to backend API. Please ensure the backend is running on ${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}`
      } 
    };
  }
}