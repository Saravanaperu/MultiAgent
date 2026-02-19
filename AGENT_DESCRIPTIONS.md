# Agent Descriptions for Quantitative Options Scalping System

The development of this system is driven by **6 specialized agents**, each responsible for a distinct microservice domain. While this document provides a high-level overview, **detailed implementation prompts** for each agent are available in the `agent_prompts/` directory.

To work on a specific module, please refer to the corresponding detailed prompt file.

---

## 1. Market Data & Infrastructure Agent
**Detailed Prompt:** `agent_prompts/market_data_agent.md`

**Focus Area:** `market_data/`, `docker-compose.yml`, Redis, PostgreSQL
**Primary Role:** Establish the foundation of the system by ensuring reliable real-time data flow and robust infrastructure.
**Key Tasks:** WebSocket client, Tick Normalizer, Candle Builder, Indicator Engine.

---

## 2. Strategy Core Developer Agent
**Detailed Prompt:** `agent_prompts/strategy_core_agent.md`

**Focus Area:** `strategy_engine/`, `strategy_engine/strategies/`
**Primary Role:** Implement the trading logic and execution signals for the system's core strategies.
**Key Tasks:** Momentum Breakout, VWAP Reversal, Gamma Scalping strategies.

---

## 3. AI & Analytics Researcher Agent
**Detailed Prompt:** `agent_prompts/ai_analytics_agent.md`

**Focus Area:** `ai_decision_layer/`, `trade_journal/`
**Primary Role:** Build the adaptive "brain" of the system and the "memory" for performance tracking.
**Key Tasks:** Market Regime Detection, Adaptive Risk Multiplier, Trade Journal Service.

---

## 4. Risk & Execution Specialist Agent
**Detailed Prompt:** `agent_prompts/risk_execution_agent.md`

**Focus Area:** `risk_management/`, `execution_simulator/`
**Primary Role:** Ensure system safety through strict risk controls and realistic trade simulation.
**Key Tasks:** Risk Validation Rules, Global Kill Switch, Execution Simulator.

---

## 5. Backend Systems Architect Agent
**Detailed Prompt:** `agent_prompts/backend_architect_agent.md`

**Focus Area:** `backend/`, `backend/routers/`
**Primary Role:** Develop the API gateway, user management, and system-wide orchestration.
**Key Tasks:** FastAPI Server, WebSocket Gateway, User/Strategy CRUD.

---

## 6. Frontend UX Developer Agent
**Detailed Prompt:** `agent_prompts/frontend_ux_agent.md`

**Focus Area:** `frontend/`
**Primary Role:** Create a high-performance, intuitive dashboard for traders to monitor and control the system.
**Key Tasks:** Real-time Dashboard (React), Lightweight Charts, AI Status Widget.
