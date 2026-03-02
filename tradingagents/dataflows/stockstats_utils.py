import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
    ):
        config = get_config()

        today_date = pd.Timestamp.today()
        curr_date_dt = pd.to_datetime(curr_date)

        end_date = today_date
        start_date = today_date - pd.DateOffset(years=15)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Ensure cache directory exists
        os.makedirs(config["data_cache_dir"], exist_ok=True)

        data_file = os.path.join(
            config["data_cache_dir"],
            f"{symbol}-YFin-data-{start_date_str}-{end_date_str}.csv",
        )

        if os.path.exists(data_file):
            data = pd.read_csv(data_file)
            data["Date"] = pd.to_datetime(data["Date"])
        else:
            # Get stock info to find the actual listing date
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info or {}

            # Check for listing date: prefer firstTradeDate, fallback to ipoExpectedDate
            first_trade_date = info.get("firstTradeDate")
            ipo_date = None
            if first_trade_date:
                ipo_date = pd.to_datetime(first_trade_date, unit="s")
            elif info.get("ipoExpectedDate"):
                ipo_date = pd.to_datetime(info.get("ipoExpectedDate"))

            # Use the earlier of: 15 years ago or the stock's first trade date
            effective_start_date = start_date
            if ipo_date is not None and ipo_date > start_date:
                effective_start_date = ipo_date

            data = yf.download(
                symbol,
                start=effective_start_date.strftime("%Y-%m-%d"),
                end=end_date_str,
                multi_level_index=False,
                progress=False,
                auto_adjust=True,
            )

            # Handle empty DataFrame (e.g., stock not found or no data available)
            if data.empty:
                raise ValueError(
                    f"No data available for symbol '{symbol}'. "
                    "The symbol may be invalid or not listed on the specified date range."
                )

            data = data.reset_index()
            data.to_csv(data_file, index=False)

        df = wrap(data)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        curr_date_str = curr_date_dt.strftime("%Y-%m-%d")

        df[indicator]  # trigger stockstats to calculate the indicator
        matching_rows = df[df["Date"].str.startswith(curr_date_str)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A: Not a trading day (weekend or holiday)"
