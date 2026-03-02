# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM financial trading framework that simulates a real trading firm. It uses specialized agents (fundamental analysts, sentiment experts, technical analysts, traders, risk management) to collaboratively evaluate market conditions and make trading decisions.

**Key Technologies:**
- LangGraph for agent orchestration
- Multiple LLM providers: OpenAI, Google (Gemini), Anthropic (Claude), xAI (Grok), OpenRouter, Ollama
- Data sources: yfinance (default), Alpha Vantage
- CLI: Chainlit-based with Typer

## Common Commands

```bash
# Run the interactive CLI
python -m cli.main

# Or use the installed CLI command
tradingagents

# Run a simple test (dataflows)
python test.py

# Run main.py example
python main.py
```

## Environment Setup

Copy `.env.example` to `.env` and set required API keys:
```bash
export OPENAI_API_KEY=...      # OpenAI (GPT)
export GOOGLE_API_KEY=...      # Google (Gemini)
export ANTHROPIC_API_KEY=...   # Anthropic (Claude)
export XAI_API_KEY=...         # xAI (Grok)
export OPENROUTER_API_KEY=...  # OpenRouter
```

## Architecture

```
tradingagents/
├── graph/                     # LangGraph orchestration
│   ├── trading_graph.py       # Main TradingAgentsGraph class
│   ├── setup.py               # Graph construction
│   ├── propagation.py        # State propagation
│   └── conditional_logic.py  # Flow control
├── agents/                   # Agent implementations
│   ├── analysts/             # Market, Social, News, Fundamentals analysts
│   ├── researchers/           # Bull/Bear researchers (debate)
│   ├── risk_mgmt/            # Risk management team
│   ├── trader/               # Trader agent
│   └── utils/                # Agent states, tools, memory
├── dataflows/                # Data fetching layer
│   ├── y_finance.py          # yfinance data provider
│   ├── alpha_vantage.py      # Alpha Vantage provider
│   └── config.py             # Data config
├── llm_clients/              # LLM provider clients
│   ├── factory.py            # Client factory
│   ├── openai_client.py
│   ├── anthropic_client.py
│   ├── google_client.py
│   └── base_client.py
└── default_config.py         # Configuration defaults
```

### Agent Flow
1. **Analyst Team**: Market, Social, News, and Fundamentals analysts gather data
2. **Researcher Team**: Bull and Bear researchers debate the findings
3. **Trader**: Composes investment plan based on research
4. **Risk Management**: Evaluates risk (aggressive, conservative, neutral)
5. **Portfolio Manager**: Final approval/rejection of trades

## Configuration

Edit `tradingagents/default_config.py` or create a custom config:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"        # or: google, anthropic, xai, openrouter, ollama
config["deep_think_llm"] = "gpt-5.2"     # Complex reasoning model
config["quick_think_llm"] = "gpt-5-mini"  # Quick tasks model
config["max_debate_rounds"] = 2

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-01-15")
```

## Data Vendors

Configure in `config["data_vendors"]`:
- `core_stock_apis`: yfinance or alpha_vantage
- `technical_indicators`: yfinance or alpha_vantage
- `fundamental_data`: yfinance or alpha_vantage
- `news_data`: yfinance or alpha_vantage
