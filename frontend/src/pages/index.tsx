import Layout from "@/components/layout/Layout";
import DynamicGridLayout from "@/components/layout/DynamicGridLayout";
import { parsePipelineLayout } from "@/lib/parsePipelineLayout";
import type { NewsletterLayout } from "@/types/components";
import { mockNewsletterLayout } from "@/data/mockLayout";
import fs from "fs";
import path from "path";

interface HomeProps {
  layout: NewsletterLayout;
}

export default function Home({ layout }: HomeProps) {
  return (
    <Layout>
      <DynamicGridLayout layout={layout} />
    </Layout>
  );
}

export async function getServerSideProps() {
  try {
    const gridJson = process.env.GRID_JSON;
    if (gridJson) {
      const parsed = JSON.parse(gridJson);
      const layout = parsePipelineLayout(parsed);
      return { props: { layout } };
    }
    // Fallback: read from public/grid.json if present
    const filePath = path.join(process.cwd(), "public", "grid.json");
    if (fs.existsSync(filePath)) {
      const file = fs.readFileSync(filePath, "utf-8");
      const parsed = JSON.parse(file);
      const layout = parsePipelineLayout(parsed);
      return { props: { layout } };
    }
  } catch (e) {
    // fall through to mock
  }
  return { props: { layout: mockNewsletterLayout } };
}