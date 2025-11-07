# PWA Setup

The app is configured to be installable as a Progressive Web App (PWA). 

## Required Files

To complete the PWA setup, you need to add icon and screenshot files:

1. **Icon files** (place in `public/icons/`):
   - `icon-192x192.png` - 192x192 pixels
   - `icon-512x512.png` - 512x512 pixels

2. **Screenshot files** (place in `public/screenshots/`):
   - `desktop-wide.png` - 1280x720 pixels (required for desktop PWA install UI)
   - `mobile-narrow.png` - 390x844 pixels (optional, for mobile install UI)

You can generate these icons from a single source image using tools like:
- [PWA Asset Generator](https://github.com/onderceylan/pwa-asset-generator)
- [RealFaviconGenerator](https://realfavicongenerator.net/)
- [PWA Builder](https://www.pwabuilder.com/imageGenerator)

For screenshots:
- Take a screenshot of your app in desktop view (1280x720 recommended)
- Take a screenshot of your app in mobile view (390x844 or similar)
- Save as PNG files in `public/screenshots/`

## What's Already Configured

✅ Web App Manifest (`public/manifest.json`)
✅ PWA meta tags in `_document.tsx`
✅ Theme color configuration
✅ Apple iOS meta tags for home screen installation

## Testing PWA Installation

1. **Development**: 
   - Run `npm run dev`
   - Open Chrome DevTools → Application → Manifest
   - Check for any errors

2. **Production**:
   - Build and deploy: `npm run build && npm start`
   - Access via HTTPS (required for PWA installation)
   - On mobile: Look for "Add to Home Screen" prompt
   - On desktop Chrome: Look for install icon in address bar

## Notes

- PWA installation requires HTTPS (except for localhost)
- The app will work offline if a service worker is added (optional)
- Icons should be square PNG files with transparent backgrounds recommended

