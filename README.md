# Marketing Campaign Planner

Live Demo: https://campaign-workspace.vercel.app

Category: Marketing & Strategy Automation Platform

Stack: React 19 Â· TypeScript Â· Python 3.11 Â· Workflow Engine Â· Vite Â· Tailwind CSS

## Overview

Marketing Campaign Planner is an enterprise-grade, full-stack workspace for end-to-end campaign planning through a guided, phased workflow. The platform orchestrates five sequential stages â€” discovery, planning (brand + channel in parallel), integration, content generation, and finalization â€” using specialized workflow modules that collaborate to produce brand creatives, channel strategies, and unified campaign plans. Human-in-the-loop review is embedded at every phase, allowing stakeholders to approve, regenerate, or rollback outputs before advancing.

The system combines a React frontend with real-time SSE streaming, session-persistent state, and Python-based service orchestration to deliver a resilient, production-ready planning environment.

## Features

- **5-Phase Orchestrated Workflow** â€” Discovery, brand/channel planning (parallel), integration, content synthesis, and finalization with structured state routing and phase-gate approvals.
- **Human-in-the-Loop Controls** â€” Approve, regenerate, and rollback actions at every stage with comparison views for iterative refinement without restarting the workflow.
- **Real-Time Streaming Experience** â€” Server-sent events (SSE) stream service reasoning and structured card outputs to the UI with live phase progress tracking.
- **Session Persistence & Sticky Routing** â€” Conversation state survives instance restarts via store-backed recovery and conversation-scoped sticky routing.
- **Modular Service Architecture** â€” Specialized services for market analysis, brand & creative, channel planning, integration strategy, and content production, each with isolated responsibilities.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript 5.6, Vite 8, Tailwind CSS 4 |
| Streaming | SSE (Server-Sent Events), Custom hooks (useSSE, useHistory) |
| Backend Services | Python 3.11, Workflow Engine (Flows, Crews), Platform Services |
| Runtime | EdgeOne Makers, Cloud Functions (Python) |
| Internationalization | i18n (zh/en), Markdown export |
| Build | Vite, npm |

## Project Structure

```
marketing-campaign/
â”œâ”€â”€ services/                         # Service orchestration (Python) â€” formerly agents/
â”‚   â”œâ”€â”€ stream.py                     # POST /stream â€” main SSE entry point
â”‚   â”œâ”€â”€ _lib/
â”‚   â”‚   â”œâ”€â”€ flow.py                   # MarketingCampaignFlow (5-step orchestration)
â”‚   â”‚   â”œâ”€â”€ persistence.py            # FlowPersistence + store synchronization
â”‚   â”‚   â”œâ”€â”€ feedback_provider.py      # Human feedback provider bridge
â”‚   â”‚   â”œâ”€â”€ llm.py                    # Platform Services initialization helper
â”‚   â”‚   â””â”€â”€ logger.py                # Structured logger
â”‚   â””â”€â”€ _crews/
â”‚       â”œâ”€â”€ discovery_crew/           # Market analysis â€” audience & insights
â”‚       â”œâ”€â”€ brand_creative_crew/      # Brand strategy â€” visual & messaging identity
â”‚       â”œâ”€â”€ channel_planning_crew/    # Channel planning â€” media mix & budget
â”‚       â”œâ”€â”€ integration_crew/         # Integration â€” unified campaign plan
â”‚       â””â”€â”€ content_crew/             # Content production â€” final deliverables
â”œâ”€â”€ cloud-functions/                  # Auxiliary HTTP endpoints (Python)
â”‚   â”œâ”€â”€ history.py                    # POST /history â€” load conversation history
â”‚   â”œâ”€â”€ delete.py                     # POST /delete â€” delete a conversation
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ src/                              # React + TypeScript frontend
â”‚   â”œâ”€â”€ App.tsx                       # Application shell & state management
â”‚   â”œâ”€â”€ components/
â”‚   â”‚   â”œâ”€â”€ cards/                    # Structured output cards
â”‚   â”‚   â”œâ”€â”€ views/                    # Phase-specific views
â”‚   â”‚   â”œâ”€â”€ Header.tsx
â”‚   â”‚   â”œâ”€â”€ PhaseProgress.tsx        # 5-phase progress indicator
â”‚   â”‚   â”œâ”€â”€ InputBar.tsx
â”‚   â”‚   â”œâ”€â”€ StartPanel.tsx
â”‚   â”‚   â””â”€â”€ HistoryPanel.tsx
â”‚   â”œâ”€â”€ hooks/
â”‚   â”‚   â”œâ”€â”€ useSSE.ts
â”‚   â”‚   â””â”€â”€ useHistory.ts
â”‚   â”œâ”€â”€ i18n.ts
â”‚   â”œâ”€â”€ types/index.ts
â”‚   â””â”€â”€ utils/export.ts               # Markdown export
â”œâ”€â”€ edgeone.json                      # Deployment configuration (framework: workflow)
â”œâ”€â”€ package.json
â”œâ”€â”€ requirements.txt
â””â”€â”€ vite.config.ts
```

> Environment variables follow the `SERVICE_*` convention â€” `SERVICE_* (alias for AI_GATEWAY_* for backward compat)` where applicable.

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+

### Installation

```bash
npm install
pip install -r requirements.txt
cp .env.example .env
```

Configure environment variables in `.env`:

```bash
SERVICE_API_KEY=your_service_key
SERVICE_BASE_URL=https://your-gateway-base-url.example.com/v1
# Optional: SERVICE_MODEL=@makers/deepseek-v4-flash
# SERVICE_* (alias for AI_GATEWAY_* for backward compat)
```

### Development

```bash
npm run dev
# Or unified dev with cloud functions and services
edgeone makers dev
```

Visit `http://localhost:8088` for the application. For observability, open `http://localhost:8080/service-metrics` if available.

### Build

```bash
npm run build
```

Outputs production assets to `dist/`.

## Deployment

### EdgeOne Makers

`edgeone.json` is preconfigured with `framework: workflow` and `dir: services`. Connect the repository to EdgeOne Makers â€” build command `npm run build`, output directory `dist`, services directory `services`. Sticky routing is handled automatically for conversation persistence.

### GitHub Pages (Frontend Preview)

For static frontend preview:

```bash
npm run build
# Deploy dist/ to gh-pages branch or configure Pages source
```

Live demo served at `https://campaign-workspace.vercel.app`.

### Custom Hosting

Deploy `dist/` to any static host (Vercel, Netlify, Cloudflare Pages) and host `services/` + `cloud-functions/` on your Python runtime. Ensure `SERVICE_*` variables are set on the server.

## Customization

- **Workflow Phases** â€” Edit `services/_lib/flow.py` to adjust phase sequence, routing decorators (`@start`, `@listen`, `@router`), and feedback gates.
- **Service Crews** â€” Update definitions under `services/_crews/` (discovery, brand_creative, channel_planning, integration, content) to tailor roles and outputs.
- **UI Cards & Views** â€” Modify `src/components/cards/` and `src/components/views/` to change card layouts or add new phase visualizations.
- **Theming & i18n** â€” Adjust Tailwind config and `src/i18n.ts` for brand palette and language support.
- **Export & Persistence** â€” Extend `src/utils/export.ts` and `services/_lib/persistence.py` for custom formats or external storage.

## License

MIT
