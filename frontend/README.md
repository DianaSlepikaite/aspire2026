# Frontend

## Quick start

```sh
npm i
npm run dev
```

The app runs on the Vite default port (typically `http://localhost:8080`).

## Common scripts

```sh
npm run dev       # start dev server
npm run build     # production build
npm run preview   # preview production build
npm run lint      # lint (if configured)
npm run test      # vitest in watch mode
npm run test -- --run   # run tests once
```

## Project structure

- `src/components/layout/` — main layout sections (Business/Career pages)
- `src/components/layout/darkSidebar/` — chat sidebar UI
- `src/components/layout/core/` — Core profile sections and fields
- `src/components/cards/` — reusable card components
- `src/hooks/` — data hooks and UI logic
- `src/lib/` — API clients and helpers

## Environment

The frontend expects API base URLs via `.env` (see `frontend/.env` and `frontend/.env.example`).

## Testing

This repo uses **Vitest** + **React Testing Library**.

```sh
npm run test -- --run
```

## Tech stack

- Vite
- TypeScript
- React
- Tailwind CSS
- shadcn-ui
