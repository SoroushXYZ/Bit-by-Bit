import Layout from "@/components/layout/Layout";
import DynamicGridLayout from "@/components/layout/DynamicGridLayout";
import { mockNewsletterLayout } from "@/data/mockLayout";

export default function Home() {
  return (
    <Layout>
      <DynamicGridLayout layout={mockNewsletterLayout} />
    </Layout>
  );
}