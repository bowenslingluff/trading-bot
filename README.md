# Trading Bot AI

An AI-powered algorithmic trading bot built with Python (FastAPI) backend and React frontend, integrating Alpaca Markets API and OpenAI for intelligent trading decisions.

## Features

- **AI-Powered Trading**: Uses OpenAI to analyze market conditions and make trading decisions
- **Real-time Dashboard**: React frontend for monitoring trades and bot performance
- **Strategy Testing**: Jupyter notebooks for prototyping and backtesting strategies
- **RESTful API**: FastAPI backend for easy integration and testing
- **Data Integration**: Direct integration with Alpaca API for account data, positions, and trade history

## API Endpoints

- `GET /status` - Bot status and account information from Alpaca API
- `GET /trades` - Trading history and current positions from Alpaca API
- `POST /trades` - Execute new trades

## Data Flow

1. **Frontend** makes requests to **Backend API**
2. **Backend** fetches data from **Alpaca API** using `alpaca_client.py`
3. **Backend** processes and returns data to **Frontend**
4. **Frontend** displays data in user-friendly format
