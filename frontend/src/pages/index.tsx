import { GetServerSideProps } from "next";
import NewsletterViewer from "@/components/newsletter/NewsletterViewer";

interface HomeProps {
  date?: string;
}

export default function Home({ date }: HomeProps) {
  return <NewsletterViewer initialDate={date} />;
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { date } = context.query;
  
  return {
    props: {
      date: date || null,
    },
  };
};