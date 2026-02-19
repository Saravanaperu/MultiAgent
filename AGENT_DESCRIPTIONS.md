# Agent Descriptions for Quantitative Options Scalping System

Based on the project's architecture and requirements detailed in `README.md`, the following **6 specialized agents** are required to complete the development end-to-end. Each agent is responsible for a distinct microservice domain, ensuring focused development and clear separation of concerns.

---

## 1. Market Data & Infrastructure Agent

**Focus Area:** `market_data/`, `docker-compose.yml`, Redis, PostgreSQL
**Primary Role:** Establish the foundation of the system by ensuring reliable real-time data flow and robust infrastructure.

**Key Responsibilities (per `README.md` Section 3.1, 3.9):**
*   **WebSocket Management:** Implement `market_data/angel_one_client.py` to maintain a persistent, auto-reconnecting WebSocket connection to the Angel One API.
*   **Data Normalization:** Develop the `Tick Normaliser` to convert raw broker feeds into a standard JSON format (LTP, bid, ask, volume, OI) and publish to Redis channel `market:ticks`.
*   **Candle Building:** Create the logic to aggregate ticks into 1-second and 1-minute OHLC candles and publish to `market:candles`.
*   **Indicator Engine:** Implement real-time calculation of technical indicators (EMA, VWAP, RSI, ATR) on every candle update.
*   **Infrastructure Orchestration:** Maintain and optimize `docker-compose.yml` to ensure all services (Redis, TimescaleDB, API, etc.) start in the correct order and communicate effectively.

---

## 2. Strategy Core Developer Agent

**Focus Area:** `strategy_engine/`, `strategy_engine/strategies/`
**Primary Role:** Implement the trading logic and execution signals for the system's core strategies.

**Key Responsibilities (per `README.md` Section 3.2, 4.2):**
*   **Strategy Implementation:** Develop the Python classes for the three built-in strategies:
    *   **Momentum Breakout:** Logic for EMA crossover, VWAP breaks, and volume spikes (Sec 4.2.1).
    *   **VWAP Reversal:** Logic for mean reversion trades when price extends from VWAP with specific RSI conditions (Sec 4.2.2).
    *   **Gamma Scalping:** Logic for high-volatility window detection and ATM option buying (Sec 4.2.3).
*   **Signal Generation:** Ensure all strategies subscribe to `market:tick` or `market:candles` and publish valid order signals to `orders:incoming` on Redis.
*   **Parameter Management:** Implement mechanisms to allow strategies to accept dynamic parameters (e.g., risk multipliers) from the AI Decision Layer.

---

## 3. AI & Analytics Researcher Agent

**Focus Area:** `ai_decision_layer/`, `trade_journal/`
**Primary Role:** Build the adaptive "brain" of the system and the "memory" for performance tracking.

**Key Responsibilities (per `README.md` Section 3.3, 3.6, 4.3):**
*   **Regime Detection:** Implement the `detect_regime` logic in `ai_decision_layer/main.py` using ADX and volatility percentiles to classify the market as Trending, Ranging, or High Volatility.
*   **Adaptive Risk:** Develop the logic to dynamically adjust the `risk_multiplier` based on recent win rates and drawdown, publishing updates to `ai:risk_multiplier` (Sec 3.3.2).
*   **Trade Journaling:** Implement the `trade_journal` service to listen for executed trades, store them in PostgreSQL/TimescaleDB with full context (entry/exit reasons, timestamps).
*   **Performance Analytics:** Create the analytics engine to compute real-time metrics (Sharpe ratio, max drawdown, win rate) to feed back into the AI layer.

---

## 4. Risk & Execution Specialist Agent

**Focus Area:** `risk_management/`, `execution_simulator/`
**Primary Role:** Ensure system safety through strict risk controls and realistic trade simulation.

**Key Responsibilities (per `README.md` Section 3.4, 3.5, 4.6):**
*   **Risk Validation:** Implement the `Risk Management Engine` to intercept every `orders:incoming` message. Enforce:
    *   **Static Limits:** Max loss per trade, max daily loss, max position size.
    *   **Dynamic Rules:** Volatility-adjusted sizing and consecutive loss cooldowns (Sec 3.4.2).
*   **Kill Switch:** Implement the global kill switch to halt all trading and square off positions if the daily drawdown limit is breached or the data feed disconnects (Sec 3.4.3).
*   **Execution Simulation:** Develop the `Execution Simulator` to match validated orders against the live tick data, simulating realistic slippage, partial fills, and transaction costs (Sec 3.5).

---

## 5. Backend Systems Architect Agent

**Focus Area:** `backend/`, `backend/routers/`
**Primary Role:** Develop the API gateway, user management, and system-wide orchestration.

**Key Responsibilities (per `README.md` Section 3.7):**
*   **API Development:** Expand `backend/main.py` and `routers/` to provide REST endpoints for user authentication, strategy configuration (CRUD), and manual order placement.
*   **WebSocket Gateway:** Enhance the Socket.IO server to push real-time updates (ticks, orders, AI state) to the frontend.
*   **System State Management:** Implement logic to start/stop specific strategies or the entire trading engine based on user requests or risk triggers.
*   **Database Management:** Design and maintain the PostgreSQL schema for users, strategies, and trade history.

---

## 6. Frontend UX Developer Agent

**Focus Area:** `frontend/`
**Primary Role:** Create a high-performance, intuitive dashboard for traders to monitor and control the system.

**Key Responsibilities (per `README.md` Section 3.8):**
*   **Real-time Dashboard:** Build the React application to display live price charts (using a library like Lightweight Charts), active positions, and P&L updates.
*   **AI Visualization:** Create widgets to display the current AI-detected Market Regime and active Risk Multipliers.
*   **Control Panel:** Implement forms and controls for users to configure strategy parameters, toggle strategies on/off, and view detailed trade history.
*   **Connectivity:** Ensure robust Socket.IO integration to handle high-frequency updates without UI lag.
