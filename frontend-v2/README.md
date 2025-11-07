# Bit-by-Bit Newsletter Frontend V2

A modern frontend for the Bit-by-Bit AI Newsletter built with Next.js, TypeScript, and Material UI.

## Tech Stack

- **Next.js 16** - React framework with Pages Router
- **TypeScript** - Type-safe development
- **Material UI (MUI)** - React component library
- **Emotion** - CSS-in-JS styling (required by MUI)

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend-v2/
├── pages/              # Next.js pages (routing)
│   ├── _app.tsx        # App wrapper with theme provider
│   ├── _document.tsx   # Custom document
│   └── index.tsx      # Home page with device detection
├── components/
│   ├── layout/         # Layout components
│   │   ├── MobileLayout.tsx
│   │   └── DesktopLayout.tsx
│   ├── mobile/         # Mobile-specific components
│   │   └── MobileHome.tsx
│   └── desktop/        # Desktop-specific components
│       └── DesktopHome.tsx
├── hooks/              # Custom React hooks
│   └── useDevice.ts    # Device detection hook
├── styles/             # Global styles
└── public/             # Static assets
```

## Features

- ✅ Next.js Pages Router
- ✅ TypeScript
- ✅ Material UI with theme support
- ✅ **Completely separate mobile and desktop experiences**
- ✅ Device detection using MUI breakpoints
- ✅ Dark/Light mode ready (theme can be extended)

## Mobile vs Desktop Architecture

This frontend uses a **completely different experience** for mobile and desktop devices:

- **Mobile**: Optimized for phone screens with vertical scrolling, touch interactions, and simplified navigation
- **Desktop**: Optimized for larger screens with grid layouts, hover interactions, and richer content

The `useDevice()` hook detects the device type using Material UI's breakpoint system (default: `md` = 900px), and the app conditionally renders different layouts and components.

### How It Works

1. **Device Detection**: `hooks/useDevice.ts` uses MUI's `useMediaQuery` to detect mobile vs desktop
2. **Separate Layouts**: `MobileLayout` and `DesktopLayout` provide different container structures
3. **Separate Components**: Mobile and desktop components are in separate directories
4. **Conditional Rendering**: Pages check device type and render appropriate components

## Next Steps

- [ ] Create newsletter layout components (separate mobile/desktop)
- [ ] Integrate with backend API
- [ ] Add date picker for newsletter selection
- [ ] Implement grid layout rendering (desktop)
- [ ] Implement mobile-optimized newsletter view
