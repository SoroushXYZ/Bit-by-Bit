import { useDevice } from '@/hooks/useDevice';
import MobileLayout from '@/components/layout/MobileLayout';
import DesktopLayout from '@/components/layout/DesktopLayout';
import MobileHome from '@/components/mobile/MobileHome';
import DesktopHome from '@/components/desktop/DesktopHome';

/**
 * Home page with completely different mobile and desktop experiences
 * Uses device detection to render appropriate layout and content
 */
export default function Home() {
  const { isMobile } = useDevice();

  // Completely separate experiences based on device type
  if (isMobile) {
    return (
      <MobileLayout>
        <MobileHome />
      </MobileLayout>
    );
  }

  return (
    <DesktopLayout>
      <DesktopHome />
    </DesktopLayout>
  );
}
