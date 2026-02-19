Quantitative Options Scalping System – Refined Design Document

Incorporating Adaptive AI, Enhanced Risk, and Phased Deployment

Version: 2.0
Date: 2026-02-19
Author: Quantitative Options Scalping AI Agent

---

Table of Contents

1. Introduction
      1.1 Objectives
      1.2 Scope
2. System Architecture
      2.1 High-Level Block Diagram
      2.2 Component Interaction
3. Detailed Component Design
      3.1 Market Data Engine
      3.2 Strategy Engine
         3.2.1 Built-in Strategy Library
      3.3 AI Decision Layer
         3.3.1 Market Regime Classification
         3.3.2 Adaptive Risk Adjustment
         3.3.3 Performance Monitoring
      3.4 Risk Management Engine
         3.4.1 Static Risk Limits
         3.4.2 Dynamic Risk Rules
         3.4.3 Kill Switch
      3.5 Execution Simulator
      3.6 Trade Journal & Analytics
      3.7 Backend API & WebSocket
      3.8 Frontend Dashboard
      3.9 Database & Caching
4. Core Logic Functions
      4.1 Market Data Processing
      4.2 Strategy Execution
         4.2.1 Momentum Breakout Strategy
         4.2.2 VWAP Reversal Strategy
         4.2.3 Gamma Scalping Window Strategy
      4.3 AI Decision Logic
         4.3.1 Regime Detection
         4.3.2 Volatility Scaling
         4.3.3 Consecutive Loss Cooldown
      4.4 Order Placement & Fill Simulation
      4.5 Position & P&L Tracking
      4.6 Risk Checks
5. Data Flow Examples
      5.1 Live Scalping Trade with AI Adaptation
      5.2 Backtesting a Strategy
6. Technology Stack
7. Security Considerations
8. Error Handling & Logging
9. Performance & Scalability
10. Deployment Lifecycle
11. Future Enhancements
12. Conclusion

---

1. Introduction

This document presents a refined design for a quantitative options scalping system that combines the robust, multi‑user paper trading platform architecture (originally detailed for Angel One SmartConnect API) with an adaptive AI layer, concrete strategy templates, and enhanced risk management inspired by a second conceptual design. The result is a scalable, intelligent system suitable for both research and eventual live trading.

1.1 Objectives

· Provide a production‑grade paper trading platform for multiple users to develop and test options scalping strategies.
· Incorporate an AI Decision Layer that dynamically adjusts risk parameters, detects market regimes, and optimises strategy selection based on real‑time performance.
· Support short‑duration scalping (30 seconds to 5 minutes) with realistic market data, order simulation, and execution costs.
· Enable thorough backtesting and forward testing with comprehensive analytics.
· Ensure strict risk discipline through static and adaptive controls.

1.2 Scope

The system includes:

· Real‑time market data ingestion from Angel One (and potentially other brokers).
· User‑defined and built‑in scalping strategies running in sandboxed environments.
· An AI meta‑layer for adaptive risk and regime classification.
· Simulated order execution with partial fills, slippage, and brokerage.
· Full trade journaling, performance analytics, and visualisation.
· Phased deployment from local paper trading to live capital.

---

2. System Architecture

The architecture follows an event‑driven microservices pattern, with each component communicating via message queues and Redis pub/sub. The key addition is the AI Decision Layer, which sits above the Strategy Engine and Risk Manager, feeding adaptive parameters into the system.

2.1 High-Level Block Diagram

```
+-------------------+        +-------------------+        +-------------------+
|                   |        |                   |        |                   |
|   React Frontend  | <----> |   Backend API     | <----> |   Paper Trading   |
|   (Web Browser)   |  REST/ |   (FastAPI)       |  gRPC/ |   Engine (Python) |
|                   |  WS    |                   |  Redis |                   |
+-------------------+        +-------------------+        +-------------------+
                                   |                           |
                                   |                      +-----------+
                                   |                      |  Strategy |
                                   |                      |  Engine   |
                                   |                      +-----+-----+
                                   |                            |
                                   |                      +-----v-----+
                                   |                      |    AI     |
                                   |                      | Decision  |
                                   |                      |   Layer   |
                                   |                      +-----+-----+
                                   |                            |
                                   +-------------+--------------+
                                                 |
                                         [Angel One API]
                                         (Market Data + Orders)
```

2.2 Component Interaction

· Frontend communicates via REST and WebSocket for real‑time updates.
· Backend API handles user management, strategy CRUD, and routes paper trading requests.
· Paper Trading Engine (PTE) maintains order books, positions, and executes fill simulations. It receives ticks from the Market Data Engine and sends orders to the Execution Simulator.
· Market Data Engine connects to Angel One WebSocket, normalises ticks, and publishes to Redis.
· Strategy Engine runs user strategies in isolated containers; each strategy subscribes to its required symbols and can generate orders via Redis.
· AI Decision Layer consumes performance data from PTE and the Trade Journal, and periodically updates risk parameters (position size multipliers, strategy weights, etc.) which are read by the Strategy Engine and Risk Manager.
· All events are persisted in PostgreSQL; high‑frequency data is cached in Redis.

---

3. Detailed Component Design

3.1 Market Data Engine

· WebSocket Manager: Maintains persistent connection to Angel One, subscribes to symbols requested by active strategies.
· Tick Normaliser: Converts raw feed to a standard JSON format with LTP, bid, ask, volume, open interest, timestamp.
· Candle Builder: Aggregates ticks into 1‑second and 1‑minute OHLC candles; keeps rolling buffers (last 500 candles) for indicator computation.
· Indicator Engine: Computes EMA, VWAP, RSI, ATR, Bollinger Bands, Supertrend on every candle update; publishes indicator values alongside ticks.
· Latency Monitor: Ticks are timestamped on arrival; if delay exceeds threshold (e.g., 500 ms), reconnection is triggered.

3.2 Strategy Engine

· Sandboxed Containers: Each user strategy runs in a Docker container with resource limits and restricted system calls.
· Event Loop: On each tick (or candle), the strategy’s on_tick or on_candle function is called.
· Order Interface: Strategies can call place_order(...) which publishes to Redis orders:incoming.
· State Management: Strategies can maintain persistent state via Redis (key‑value store) with user‑defined keys.

3.2.1 Built-in Strategy Library

The system includes pre‑coded, parameterisable strategies (see Section 4.2 for logic details):

· Momentum Breakout
· VWAP Reversal
· Gamma Scalping Window

3.3 AI Decision Layer

This new component continuously monitors system performance and market conditions to adapt risk and strategy behaviour.

3.3.1 Market Regime Classification

· Uses indicators like ADX, volatility percentile, and price‑action patterns to classify the market as trending, ranging, or high‑volatility.
· The classification is published every minute and consumed by strategies to enable/disable certain logic (e.g., momentum strategies only in trending regimes).

3.3.2 Adaptive Risk Adjustment

· Tracks rolling win rate, Sharpe ratio, and maximum drawdown over configurable windows (e.g., last 20 trades).
· Dynamically adjusts:
  · Position size multiplier: scales base risk per trade up/down based on recent performance.
  · Stop‑loss distance: widens or tightens based on volatility (ATR) and win rate.
  · Strategy weight: if multiple strategies are active, allocates capital proportionally to their recent performance.

3.3.3 Performance Monitoring

· Listens to trade events from the Trade Journal.
· Maintains per‑strategy and overall statistics.
· Triggers alerts or cooldowns when thresholds are breached (e.g., consecutive losses).

3.4 Risk Management Engine

The Risk Manager enforces both static and dynamic limits. It intercepts every order before execution.

3.4.1 Static Risk Limits (User‑configurable)

· Max loss per trade (% of capital)
· Max daily loss (%)
· Max position size (lots)
· Max gross exposure (₹)
· Max net delta

3.4.2 Dynamic Risk Rules

· Consecutive loss cooldown: After N losses (e.g., 4), trading is paused for a period (e.g., 15 minutes).
· Volatility‑adjusted position sizing: Position size = (Risk per trade) / (ATR × lot size × delta) — using current ATR.
· Daily loss halt: If daily loss exceeds limit, all strategies are deactivated until next day.

3.4.3 Kill Switch

Triggers an immediate square‑off of all positions and halt of trading if:

· Drawdown exceeds 5% (configurable) in a session.
· Angel One WebSocket disconnects for more than 10 seconds.
· Bid‑ask spread widens beyond a threshold (e.g., 5% of LTP) for illiquid options.

3.5 Execution Simulator

· Order Book: Maintains per‑symbol limit/stop orders in priority queues.
· Fill Algorithm: For each tick, checks for stop triggers, matches limit orders against bid/ask, simulates partial fills based on available volume (estimated from tick volume).
· Slippage & Costs: Market orders incur slippage proportional to spread; brokerage, STT, GST, exchange fees are deducted from trade proceeds.
· Order Types Supported: Market, Limit, Stop‑Loss, Stop‑Loss Market, Bracket Orders.

3.6 Trade Journal & Analytics

· Trade Storage: Each executed trade is stored with:
  · Entry/exit timestamps, price, quantity, side.
  · Entry reason (e.g., “Momentum breakout signal”)
  · Exit reason (e.g., “Target hit”, “Stop loss”)
  · Strategy tag, session ID.
· Analytics Engine: Computes win rate, profit factor, Sharpe ratio, max drawdown, expectancy, etc., in real‑time and on demand.
· Reporting: Generates daily PDF summaries with equity curve, trade list, and performance metrics.

3.7 Backend API & WebSocket

· REST Endpoints: User management, strategy CRUD, order placement (manual), backtest triggers, portfolio queries.
· WebSocket: Pushes real‑time ticks, order updates, position changes, AI state (current regime, risk multiplier) to frontend.

3.8 Frontend Dashboard

· Live Charts: Price chart with indicators, positions marked.
· AI Dashboard: Displays current regime, adaptive risk parameters, win rate, drawdown.
· Trade History: Filterable by strategy, date, symbol.
· Session Summary: Daily P&L, equity curve, downloadable reports.

3.9 Database & Caching

· PostgreSQL: Stores users, strategies, orders, trades, ticks (partitioned), backtest jobs, analytics snapshots.
· Redis: Caches latest ticks, positions, order books, AI state; pub/sub for real‑time events.

---

4. Core Logic Functions

4.1 Market Data Processing

· Ticks are published to Redis channel market:ticks.
· Candle builder consumes ticks, emits 1‑sec and 1‑min candles to market:candles.
· Indicator calculator subscribes to candles and publishes indicator values.

4.2 Strategy Execution

Each built‑in strategy is implemented as a Python class with standard methods. Users can modify parameters via the UI.

4.2.1 Momentum Breakout Strategy

· Entry Conditions:
  · 9‑EMA crosses above 21‑EMA.
  · Price breaks above VWAP + 0.5%.
  · Volume > 1.5 × average volume (20‑period).
  · RSI (14) between 50 and 70.
· Exit: Take profit at 0.5% or stop loss at 0.3% (ATR‑adjusted).
· Timeout: 2 minutes.

4.2.2 VWAP Reversal Strategy

· Entry:
  · Price trades below VWAP – 0.3% and RSI < 30.
  · Volume spike ( > 2× average) indicates absorption.
· Exit: Target VWAP, stop at 0.2% below entry.

4.2.3 Gamma Scalping Window Strategy

· Entry:
  · Detect high‑volatility window (e.g., first 30 minutes after market open or major news).
  · Buy near‑ATM options when IV > 90th percentile of recent 5‑day range.
· Exit: After 1% move in underlying or after 5 minutes.

4.3 AI Decision Logic

4.3.1 Regime Detection

· Compute ADX(14) on 1‑minute candles.
  · ADX > 25 → trending; else ranging.
· Also compute volatility percentile (ATR(14) relative to 50‑day range).
· Publish regime to Redis ai:regime.

4.3.2 Volatility Scaling

· Base risk per trade = 1% of capital.
· Scale factor = 1 / (ATR / average ATR) — i.e., reduce size when volatility high.
· Final position size = base risk × scale factor × win‑rate multiplier (if win rate > 60%, increase up to 1.5×; if < 40%, reduce to 0.5×).

4.3.3 Consecutive Loss Cooldown

· AI tracks consecutive losses per strategy.
· If ≥ 4, that strategy is paused for 15 minutes; overall system may also pause if all strategies are paused.

4.4 Order Placement & Fill Simulation

(Detailed in Document A – remains unchanged)

4.5 Position & P&L Tracking

(Detailed in Document A – remains unchanged, but now Greeks are computed for options)

4.6 Risk Checks

· Pre‑trade: static limits + dynamic multipliers.
· Real‑time: daily loss limit, drawdown kill switch.

---

5. Data Flow Examples

5.1 Live Scalping Trade with AI Adaptation

1. Market Data: Tick for NIFTY option arrives; candle updated; regime detected as “trending”.
2. AI Decision Layer: Publishes regime = trending, risk multiplier = 1.2 (due to recent high win rate).
3. Strategy Engine: Momentum Breakout strategy receives tick, sees EMA crossover and volume spike → generates BUY order with quantity = base_lot × 1.2.
4. Risk Manager: Validates order against daily loss limit (currently OK) and passes.
5. Execution Simulator: Fills order at ask + slippage; updates position.
6. Trade Journal: Records trade with entry reason “Momentum breakout”.
7. AI Layer updates win rate; if this trade later becomes a loss, consecutive loss counter increments.

5.2 Backtesting a Strategy

(Similar to Document A, but backtest can also simulate AI adaptation by replaying historical regime decisions.)

---

6. Technology Stack

Component Technology
Frontend React + TypeScript, Vite, MUI, Socket.IO
Backend API FastAPI (Python)
Paper Trading Engine Python 3.11 + asyncio
Strategy Sandbox Docker + restricted Python environment
AI Decision Layer Python (scikit‑learn for classifiers)
Database PostgreSQL 15 + TimescaleDB (for time‑series)
Cache / Message Bus Redis 7
Message Queue RabbitMQ
Broker Integration Angel One SmartConnect Python SDK
Monitoring Prometheus + Grafana
Container Orchestration Docker Compose (dev), Kubernetes (prod)

---

7. Security Considerations

· API keys encrypted with AES‑256‑GCM.
· HTTPS with TLS 1.3.
· Docker sandboxing with seccomp, no network except Redis.
· Rate limiting on API endpoints.
· Audit logs for all order actions.

---

8. Error Handling & Logging

· Structured JSON logging.
· Centralised log aggregation (ELK).
· Alerts on critical failures (feed disconnect, high rejection rate).
· Automatic retries with exponential backoff for transient errors.

---

9. Performance & Scalability

· Tick processing pipeline designed for <10 ms latency.
· Horizontal scaling of stateless components via Kubernetes.
· Database partitioning and connection pooling.
· Redis for low‑latency state.

---

10. Deployment Lifecycle

The system will be rolled out in three phases:

Phase 1: Local Paper Trading

· Single user, simulated data (or limited live feed).
· Validate strategy execution, order simulation, and AI adaptation.

Phase 2: Cloud Forward Testing

· Multi‑user, live market data (paper execution).
· Monitor AI performance, risk controls, and system scalability.

Phase 3: Controlled Live Trading

· Small capital, real orders with broker.
· Gradually increase capital based on performance metrics.
· Full monitoring and kill switch in place.

---

11. Future Enhancements

· Reinforcement Learning for dynamic strategy selection.
· Order Book Imbalance ML Model to predict short‑term price direction.
· Real‑time Implied Volatility Surface for more accurate options pricing.
· Multi‑Broker Abstraction (Zerodha, Upstox, etc.).
· Portfolio‑Level Risk Netting across multiple strategies.

---

12. Conclusion

This refined design merges the comprehensive technical foundation of Document A with the adaptive intelligence and practical risk rules of Document B. The resulting system is a powerful, scalable platform for quantitative options scalping—suitable for both research and eventual live deployment. By incorporating an AI Decision Layer, concrete strategy templates, enhanced logging, and a phased rollout plan, the system is well‑positioned to evolve into a production‑grade trading engine.

---