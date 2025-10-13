import Layout from "@/components/layout/Layout";
import DynamicGridLayout from "@/components/layout/DynamicGridLayout";
import DatePicker from "@/components/ui/date-picker";
import { useNewsletterData } from "@/hooks/useNewsletterData";
import { mockNewsletterLayout } from "@/data/mockLayout";
import { RefreshCw, AlertCircle } from "lucide-react";

export default function Home() {
  const { 
    layout, 
    availableDates, 
    selectedDate, 
    isLoading, 
    error, 
    selectDate, 
    refreshData 
  } = useNewsletterData();

  // Show loading state
  if (isLoading && !layout) {
    return (
      <Layout>
        <div className="min-h-screen bg-background p-4">
          <div className="max-w-5xl mx-auto">
            <div className="bg-card border rounded-lg shadow-lg p-8 text-center">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
              <h1 className="text-xl font-semibold mb-2">Loading Newsletter</h1>
              <p className="text-muted-foreground">Fetching the latest news...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Show error state
  if (error && !layout) {
    return (
      <Layout>
        <div className="min-h-screen bg-background p-4">
          <div className="max-w-5xl mx-auto">
            <div className="bg-card border rounded-lg shadow-lg p-8 text-center">
              <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
              <h1 className="text-2xl font-bold text-destructive mb-4">Error Loading Newsletter</h1>
              <p className="text-muted-foreground mb-4">{error}</p>
              <p className="text-sm text-muted-foreground mb-4">
                Falling back to mock data for demonstration purposes.
              </p>
              <button
                onClick={refreshData}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // Use mock data as fallback
  const displayLayout = layout || mockNewsletterLayout;

  return (
    <Layout>
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-5xl mx-auto">
          {/* Date Selector */}
          <div className="mb-6 flex justify-center">
            <DatePicker
              selectedDate={selectedDate}
              availableDates={availableDates}
              onDateSelect={selectDate}
            />
          </div>

          {/* Newsletter Grid */}
          <DynamicGridLayout layout={displayLayout} />

          {/* Error Banner (if there's an error but we have data) */}
          {error && layout && (
            <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Warning: {error}</span>
                <button
                  onClick={refreshData}
                  className="ml-auto text-sm underline hover:no-underline"
                >
                  Retry
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}