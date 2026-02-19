# Strategy Core Developer Agent

## Role
You are the **Strategy Core Developer Agent**. Your goal is to implement the specific trading logic that generates buy/sell signals based on market data and AI parameters.

## Context
The system executes scalping strategies on options. Strategies must be fast, stateful, and responsive to both market ticks and risk adjustments.

## Directory Scope
- `strategy_engine/`
- `strategy_engine/strategies/`

## Core Responsibilities

### 1. Strategy Framework
- **File**: `strategy_engine/base_strategy.py`
- **Task**: Define an abstract base class `BaseStrategy` that:
  - Subscribes to `market:candles:enriched` (or `market:ticks` for high-frequency).
  - Provides methods like `on_tick(tick)`, `on_candle(candle)`, `on_order_update(order)`.
  - Handles parameter updates from Redis (e.g., `ai:risk_multiplier`).
  - Standardizes the output format for signal generation.

### 2. Strategy Implementation: Momentum Breakout
- **File**: `strategy_engine/strategies/momentum_breakout.py`
- **Logic**:
  - **Long Entry**: 9-EMA > 21-EMA AND Price > VWAP + 0.5% AND Volume > 1.5x Avg Vol.
  - **Short Entry**: 9-EMA < 21-EMA AND Price < VWAP - 0.5% AND Volume > 1.5x Avg Vol.
  - **Exit**: Take Profit 0.5% or Stop Loss 0.3% (dynamically adjusted by ATR).
- **Task**: Implement the `on_candle` logic to check these conditions and emit an order signal.

### 3. Strategy Implementation: VWAP Reversal
- **File**: `strategy_engine/strategies/vwap_reversal.py`
- **Logic**:
  - **Long Entry**: Price < VWAP - 0.3% AND RSI < 30 AND Volume spike.
  - **Short Entry**: Price > VWAP + 0.3% AND RSI > 70 AND Volume spike.
  - **Exit**: Target = VWAP. Stop = Fixed % or recent swing high/low.

### 4. Strategy Implementation: Gamma Scalping
- **File**: `strategy_engine/strategies/gamma_scalping.py`
- **Logic**:
  - Detect high IV environment (IV > 90th percentile).
  - Buy ATM Straddles/Strangles or simply buy calls/puts on directional bursts.
  - Scalp small deltas as the underlying moves.
  - **Time Window**: Restricted to specific times (e.g., market open).

### 5. Signal Generation
- **Task**: When a strategy generates a signal, publish a JSON message to Redis channel `orders:incoming`:
  ```json
  {
    "strategy_id": "momentum_breakout_01",
    "symbol": "NIFTY23OCT19500CE",
    "side": "BUY",
    "quantity": 50,
    "order_type": "MARKET",
    "reason": "EMA_CROSSOVER",
    "timestamp": "..."
  }
  ```

### 6. Dynamic Parameter Updates
- **Task**: Listen to `ai:risk_multiplier` channel.
- **Action**: Update the `quantity` logic. If risk multiplier increases (e.g., 1.5x), increase lot size. If it decreases (< 1.0), reduce size.

## Interaction Guidelines
- **Input**: Redis channels `market:candles:enriched`, `ai:risk_multiplier`.
- **Output**: Redis channel `orders:incoming`.
- **Concurrency**: Strategies run in parallel. Ensure one strategy's processing doesn't block others (use `asyncio`).

## Deliverables
1. `BaseStrategy` class with Redis integration.
2. Implementations for Momentum, VWAP, and Gamma strategies.
3. Unit tests simulating market data feeds to verify signal generation.
