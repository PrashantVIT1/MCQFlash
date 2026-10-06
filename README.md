# MCQFlash

**Snap. Solve. Instantly.**

MCQFlash is a fast MCQ answer-checking web application. Capture MCQs with your phone, and get instant answers powered by AI.

## Features

- **Dual Image Capture**: Upload or capture up to two images for complex MCQs
- **Mobile-First Design**: Optimized for phone camera capture with rear camera support
- **Fast Workflow**: Capture → Solve → Answer → Next Question in seconds
- **Clean UI**: Modern, minimal interface inspired by modern AI workspaces
- **Responsive**: Works seamlessly on mobile, tablet, and desktop

## Tech Stack

- **Frontend**: React 19.2.8 with Vite 8.3.0
- **Styling**: Tailwind CSS 4.3.3
- **Icons**: Lucide React 1.52.0
- **Build Tool**: Vite

## Project Structure

```
MCQ Flash/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx          # Navigation with New Session & References
│   │   ├── Header.jsx           # Branding header
│   │   ├── ImageUploadCard.jsx   # Dual image upload/capture cards
│   │   ├── SolveButton.jsx       # Primary action button
│   │   ├── AnswerCard.jsx        # Answer display with metrics
│   │   └── NextQuestionButton.jsx # Reset workflow button
│   ├── App.jsx                   # Main application component
│   ├── main.jsx                  # React entry point
│   └── index.css                 # Tailwind CSS imports
├── postcss.config.js             # PostCSS configuration for Tailwind v4
└── package.json                  # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to the URL shown (typically `http://localhost:5173`)

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Usage

1. **Add Images**: Click on either image card to capture or upload an MCQ image
   - On mobile: Opens rear camera for capture
   - On desktop: Opens file picker
   - Supports up to two images for complex questions

2. **Solve MCQ**: Click the "Solve MCQ" button to analyze the question
   - Requires at least one image
   - Shows loading state during analysis

3. **View Answer**: See the answer with confidence score and response time
   - Answer letter (e.g., "C")
   - Answer text (e.g., "LED")
   - Confidence percentage
   - Response time

4. **Next Question**: Click "Next Question" to clear everything and start fresh

5. **New Session**: Use the sidebar's "New Session" button to reset the entire workflow

## Component Overview

### Sidebar
- Navigation menu with "New Session" and "References"
- Collapses to hamburger menu on mobile
- "References" is a placeholder for future features

### ImageUploadCard
- Large upload/capture cards with "+" icon
- Supports camera capture (`capture="environment"`)
- Image preview with remove button
- Side-by-side on desktop, stacked on mobile

### SolveButton
- Primary action button with loading state
- Disabled when no images are selected
- Hover and active states

### AnswerCard
- Displays answer with prominent typography
- Shows confidence percentage and response time
- Clean card design with metrics

### NextQuestionButton
- Resets all state for next MCQ
- Primary action after viewing answer
- Arrow icon for visual cue

## Design System

- **Primary Color**: Indigo (#4f46e5)
- **Background**: Light gray (#f9fafb)
- **Border Radius**: xl (12px)
- **Typography**: System sans-serif fonts
- **Spacing**: Consistent padding/margins for visual rhythm

## Responsive Breakpoints

- **Mobile**: < 768px (stacked cards, hamburger menu)
- **Tablet**: 768px - 1024px (reduced spacing)
- **Desktop**: > 1024px (sidebar fixed, side-by-side cards)

## Future Backend Integration

The frontend is designed for easy backend integration. The `handleSolve` function in `App.jsx` will be replaced with:

```javascript
const response = await fetch('/api/solve', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ image1, image2 })
});
```

The mock data structure matches the expected API response format.

## Development Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run Oxlint linter

## License

Proprietary - All rights reserved
