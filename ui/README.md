# Synth Bot UI

Frontend for Synth Bot -- a RAG-powered chatbot for synthesizer manuals. Upload your synth manuals (PDF), ask questions about your gear, and get answers with page-level citations sourced from the actual documentation.

## Tech Stack

- React 19 + TypeScript
- Vite (dev server and build)
- Tailwind CSS 3.4 with shadcn/ui components
- Prompt Kit (prompt-kit.com) for AI chat UI components
- TanStack React Query for server state
- React Router v6
- Lucide React for icons

## Prompt Kit

This project uses [Prompt Kit](https://www.prompt-kit.com) -- a component library purpose-built for AI chat interfaces. Components are installed via the shadcn CLI and live in `src/components/ui/`.

Components used:

- `PromptInput` -- Auto-resizing textarea with submit actions, used for the chat input area
- `Message` -- Message layout with avatar, markdown content, and action buttons
- `Markdown` -- Memoized markdown renderer with GFM support and syntax-highlighted code blocks via Shiki
- `CodeBlock` -- Syntax-highlighted code display powered by Shiki
- `Loader` -- Typing indicator animation shown while waiting for AI responses
- `PromptSuggestion` -- Clickable prompt suggestion pills displayed on the welcome screen

To install a Prompt Kit component:

```bash
npx shadcn@latest add "https://prompt-kit.com/c/<component-name>.json"
```

## shadcn/ui Components

Standard shadcn/ui components: button, card, input, textarea, avatar, tooltip, dialog, sidebar, dropdown-menu, separator, badge, sheet, skeleton.

## Project Structure

```
src/
  api/              API client and typed endpoints (chat, conversations, documents)
  components/
    ui/             shadcn/ui + Prompt Kit components
    theme-toggle.tsx
  hooks/            Custom hooks (useTheme, useMobile)
  lib/              Utilities (cn)
  pages/
    ChatPage.tsx    AI chat interface with conversation support
    DocumentsPage.tsx  Manual upload and management
  App.tsx           App shell with sidebar layout and routing
  main.tsx          Entry point
  index.css         Tailwind directives + CSS variables (shadcn zinc theme)
public/
  logo.png          Synth Bot logo
```

## Features

- Conversation-based chat with sidebar history
- Markdown rendering with syntax-highlighted code blocks
- Citations with page numbers and relevance scores from the RAG pipeline
- Expandable citation content -- click a source pill to see the referenced text
- Manual (PDF) upload with processing indicator
- Dark/light theme using shadcn zinc palette
- Collapsible sidebar with responsive mobile layout

## API Endpoints

The frontend proxies `/api` to the backend (default `http://localhost:8000`). Configurable in `vite.config.ts`.

Chat:
- `POST /chat/` -- Send a message (with optional conversation_id)
- `GET /conversations/` -- List conversations (sidebar history)
- `GET /conversations/:id` -- Full conversation with chat history and citations
- `DELETE /conversations/:id` -- Delete a conversation

Manuals:
- `GET /documents/` -- List uploaded manuals
- `POST /documents/upload` -- Upload a manual (multipart/form-data)
- `DELETE /documents/:id` -- Delete a manual

## Development

```bash
npm install
npm run dev       # Dev server on http://localhost:3000
npm run build     # TypeScript check + production build
npm run preview   # Preview production build
```

Requires the backend API running on `http://localhost:8000`.
