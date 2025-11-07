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
├── pages/           # Next.js pages (routing)
│   ├── _app.tsx     # App wrapper with theme provider
│   ├── _document.tsx # Custom document
│   └── index.tsx    # Home page
├── styles/          # Global styles
├── public/          # Static assets
└── ...
```

## Features

- ✅ Next.js Pages Router
- ✅ TypeScript
- ✅ Material UI with theme support
- ✅ Dark/Light mode ready (theme can be extended)

## Next Steps

- [ ] Create newsletter layout components
- [ ] Integrate with backend API
- [ ] Add date picker for newsletter selection
- [ ] Implement grid layout rendering
- [ ] Add responsive design
