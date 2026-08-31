import type { Locale } from "./types"

type Messages = Record<string, string>

const en: Messages = {
  "app.title": "Marketing Campaign Workbench",
  "app.new": "New",
  "app.history": "History",

  "phase.discovery": "Research",
  "phase.planning": "Planning",
  "phase.integration": "Integration",
  "phase.content": "Content",
  "phase.finalize": "Finalize",

  "action.confirm": "Confirm",
  "action.redo": "Redo",
  "action.rollback": "Go Back",
  "action.finish": "All Done",
  "action.skip_discovery": "Enough info, start planning",
  "action.send": "Send",
  "action.start": "Start Planning",
  "action.continue_edit": "Continue Editing",

  "card.audience": "Audience Profile",
  "card.brand_creative": "Brand Creative",
  "card.channel_plan": "Channel Strategy",
  "card.strategy": "Integrated Strategy",
  "card.copywriting": "Marketing Copy",

  "agent.chief_strategist": "Chief Strategist",
  "agent.market_analyst": "Market Analyst",
  "agent.brand_creative_director": "Creative Director",
  "agent.channel_planner": "Channel Planner",
  "agent.copywriter": "Copywriter",

  "status.generating": "Generating...",
  "status.waiting": "Awaiting action...",
  "status.ready": "Ready",

  "start.title": "Create Marketing Campaign",
  "start.name_placeholder": "Campaign name (e.g., Summer Sale, Product Launch)",
  "start.brief_placeholder": "Describe your marketing needs (product/service, goals, budget range, etc.)",
  "start.examples": "Quick Examples",
  "start.example1": "New beverage brand summer promotion",
  "start.example2": "SaaS product launch campaign",
  "start.example3": "Retail store anniversary event",
  "start.brief1": "New tea brand summer promo targeting young women, $70K budget, primarily online",
  "start.brief2": "B2B SaaS product launch event, targeting SMB CTOs and IT leaders",
  "start.brief3": "Large shopping mall 5th anniversary, targeting families within 3km radius",

  "input.placeholder": "Type your answer or feedback...",
  "input.feedback_placeholder": "Give feedback...",
}

const messages: Record<Locale, Messages> = { en }

let currentLocale: Locale = "en"

export function setLocale(locale: Locale) {
  currentLocale = locale
  localStorage.setItem("marketing-campaign-locale", locale)
}

export function getLocale(): Locale {
  return currentLocale
}

export function initLocale(): Locale {
  const saved = localStorage.getItem("marketing-campaign-locale") as Locale | null
  if (saved && saved === "en") {
    currentLocale = saved
    return saved
  }
  currentLocale = "en"
  return "en"
}

export function t(key: string): string {
  return messages[currentLocale][key] || key
}
