# Marketing Campaign Planner

Live Demo: https://gourab775.github.io/marketing-campaign

Category: Marketing & Strategy Automation Platform

Stack: React 19 · TypeScript · Python 3.11 · Workflow Engine · Vite · Tailwind CSS

## Overview

Marketing Campaign Planner is an enterprise-grade, full-stack workspace for end-to-end campaign planning through a guided, phased workflow. The platform orchestrates five sequential stages — discovery, planning (brand + channel in parallel), integration, content generation, and finalization — using specialized workflow modules that collaborate to produce brand creatives, channel strategies, and unified campaign plans. Human-in-the-loop review is embedded at every phase, allowing stakeholders to approve, regenerate, or rollback outputs before advancing.

The system combines a React frontend with real-time SSE streaming, session-persistent state, and Python-based service orchestration to deliver a resilient, production-ready planning environment.

## Features

- **5-Phase Orchestrated Workflow** — Discovery, brand/channel planning (parallel), integration, content synthesis, and finalization with structured state routing and phase-gate approvals.
- **Human-in-the-Loop Controls** — Approve, regenerate, and rollback actions at every stage with comparison views for iterative refinement without restarting the workflow.
- **Real-Time Streaming Experience** — Server-sent events (SSE) stream service reasoning and structured card outputs to the UI with live phase progress tracking.
- **Session Persistence & Sticky Routing** — Conversation state survives instance restarts via store-backed recovery and conversation-scoped sticky routing.
- **Modular Service Architecture** — Specialized services for market analysis, brand & creative, channel planning, integration strategy, and content production, each with isolated responsibilities.

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
├── services/                         # Service orchestration (Python) — formerly agents/
│   ├── stream.py                     # POST /stream — main SSE entry point
│   ├── _lib/
│   │   ├── flow.py                   # MarketingCampaignFlow (5-step orchestration)
│   │   ├── persistence.py            # FlowPersistence + store synchronization
│   │   ├── feedback_provider.py      # Human feedback provider bridge
│   │   ├── llm.py                    # Platform Services initialization helper
│   │   └── logger.py                # Structured logger
│   └── _crews/
│       ├── discovery_crew/           # Market analysis — audience & insights
│       ├── brand_creative_crew/      # Brand strategy — visual & messaging identity
│       ├── channel_planning_crew/    # Channel planning — media mix & budget
│       ├── integration_crew/         # Integration — unified campaign plan
│       └── content_crew/             # Content production — final deliverables
├── cloud-functions/                  # Auxiliary HTTP endpoints (Python)
│   ├── history.py                    # POST /history — load conversation history
│   ├── delete.py                     # POST /delete — delete a conversation
│   └── requirements.txt
├── src/                              # React + TypeScript frontend
│   ├── App.tsx                       # Application shell & state management
│   ├── components/
│   │   ├── cards/                    # Structured output cards
│   │   ├── views/                    # Phase-specific views
│   │   ├── Header.tsx
│   │   ├── PhaseProgress.tsx        # 5-phase progress indicator
│   │   ├── InputBar.tsx
│   │   ├── StartPanel.tsx
│   │   └── HistoryPanel.tsx
│   ├── hooks/
│   │   ├── useSSE.ts
│   │   └── useHistory.ts
│   ├── i18n.ts
│   ├── types/index.ts
│   └── utils/export.ts               # Markdown export
├── edgeone.json                      # Deployment configuration (framework: workflow)
├── package.json
├── requirements.txt
└── vite.config.ts
```

> Environment variables follow the `SERVICE_*` convention — `SERVICE_* (alias for AI_GATEWAY_* for backward compat)` where applicable.

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

`edgeone.json` is preconfigured with `framework: workflow` and `dir: services`. Connect the repository to EdgeOne Makers — build command `npm run build`, output directory `dist`, services directory `services`. Sticky routing is handled automatically for conversation persistence.

### GitHub Pages (Frontend Preview)

For static frontend preview:

```bash
npm run build
# Deploy dist/ to gh-pages branch or configure Pages source
```

Live demo served at `https://gourab775.github.io/marketing-campaign`.

### Custom Hosting

Deploy `dist/` to any static host (Vercel, Netlify, Cloudflare Pages) and host `services/` + `cloud-functions/` on your Python runtime. Ensure `SERVICE_*` variables are set on the server.

## Customization

- **Workflow Phases** — Edit `services/_lib/flow.py` to adjust phase sequence, routing decorators (`@start`, `@listen`, `@router`), and feedback gates.
- **Service Crews** — Update definitions under `services/_crews/` (discovery, brand_creative, channel_planning, integration, content) to tailor roles and outputs.
- **UI Cards & Views** — Modify `src/components/cards/` and `src/components/views/` to change card layouts or add new phase visualizations.
- **Theming & i18n** — Adjust Tailwind config and `src/i18n.ts` for brand palette and language support.
- **Export & Persistence** — Extend `src/utils/export.ts` and `services/_lib/persistence.py` for custom formats or external storage.

## License

MIT
