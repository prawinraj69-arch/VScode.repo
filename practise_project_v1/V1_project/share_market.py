"""
Indian Stock Market Analysis & Investment Recommendation System

Analyzes top Indian stocks and recommends the best 5 to invest today.
Run this script anytime to get fresh recommendations based on current market data.
"""

from __future__ import annotations

import warnings
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────
#  NIFTY 50 STOCKS (top Indian companies)
# ─────────────────────────────────────────────────────────────
NIFTY_50_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "HDFC.NS", "BAJAJFINSV.NS", "MARUTI.NS", "AXISBANK.NS", "ITC.NS",
    "HDFCBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ASIANPAINT.NS", "SUNPHARMA.NS",
    "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "KOTAKBANK.NS", "DMART.NS", "M_MFIN.NS", "LT.NS", "HEROMOTOCO.NS",
    "NESTLEIND.NS", "ADANIPORTS.NS", "TATASTEEL.NS", "TECHM.NS", "EICHERMOT.NS",
    "HCLTECH.NS", "HINDALCO.NS", "GAIL.NS", "GBPINFRA.NS", "SHREECEM.NS",
    "TITAN.NS", "BAJAJ_AUTO.NS", "DRREDDY.NS", "BANDHANBNK.NS", "COLPAL.NS",
    "INDIGO.NS", "IDFCBANK.NS", "MCDOWELL_N.NS", "CIPLA.NS", "LUPIN.NS",
    "INDUSTOWER.NS", "AMBUJACEM.NS", "ACC.NS", "PEL.NS", "GODREJCP.NS",
]


class StockAnalyzer:
    """Analyzes Indian stocks and recommends top 5 for investment."""

    def __init__(self):
        self.stocks = NIFTY_50_STOCKS
        self.analysis_results = []

    def fetch_stock_data(self) -> dict:
        """Fetch last 1 month stock data for analysis."""
        print(f"\n{'='*70}")
        print(f"  INDIAN STOCK MARKET ANALYSIS")
        print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        print("[*] Fetching market data for 50 NIFTY stocks...")
        data = {}
        valid_stocks = 0

        for stock in self.stocks:
            try:
                hist = yf.download(
                    stock,
                    period="1mo",
                    interval="1d",
                    progress=False
                )

                if len(hist) > 0:
                    # Flatten MultiIndex columns if present (yfinance >= 0.2 returns MultiIndex)
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = hist.columns.droplevel(1)
                    
                    # Convert Series to scalar values
                    close_series = hist["Close"]
                    volume_series = hist["Volume"]
                    
                    current_price = float(close_series.iloc[-1])
                    previous_close = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
                    month_high = float(close_series.max())
                    month_low = float(close_series.min())
                    volume = float(volume_series.iloc[-1])
                    avg_volume = float(volume_series.mean())

                    data[stock] = {
                        "current_price": current_price,
                        "previous_close": previous_close,
                        "month_high": month_high,
                        "month_low": month_low,
                        "volume": volume,
                        "avg_volume": avg_volume,
                        "history": hist,
                    }
                    valid_stocks += 1
            except Exception as e:
                pass

        print(f"[OK] Successfully fetched data for {valid_stocks}/50 stocks\n")
        return data

    def calculate_score(self, stock_code: str, data: dict) -> dict:
        """Calculate investment score based on multiple factors."""
        if stock_code not in data or len(data[stock_code]["history"]) < 5:
            return None

        stock_data = data[stock_code]
        hist = stock_data["history"]

        # 1. Price momentum (5-day trend)
        close_series = hist["Close"]
        price_5d_ago = float(close_series.iloc[-5])
        current_price = float(stock_data["current_price"])
        momentum_pct = ((current_price - price_5d_ago) / price_5d_ago) * 100

        # 2. Monthly trend
        month_start = float(close_series.iloc[0])
        month_trend = ((current_price - month_start) / month_start) * 100

        # 3. Relative strength vs Month high/low
        month_high = float(stock_data["month_high"])
        month_low = float(stock_data["month_low"])
        range_position = ((current_price - month_low) / (month_high - month_low)) * 100 if (month_high - month_low) > 0 else 50

        # 4. Volume trend (current vs average)
        volume_ratio = float(stock_data["volume"]) / float(stock_data["avg_volume"]) if float(stock_data["avg_volume"]) > 0 else 1

        # 5. Daily momentum
        daily_change = ((current_price - float(stock_data["previous_close"])) / float(stock_data["previous_close"])) * 100

        # Calculate composite score
        score = (
            momentum_pct * 0.25 +
            month_trend * 0.20 +
            range_position * 0.20 +
            (volume_ratio - 1) * 50 * 0.20 +
            daily_change * 0.15
        )

        return {
            "stock": stock_code.replace(".NS", ""),
            "current_price": current_price,
            "score": score,
            "momentum_pct": momentum_pct,
            "month_trend": month_trend,
            "daily_change": daily_change,
            "range_position": range_position,
            "volume_ratio": volume_ratio,
        }

    def analyze_and_recommend(self, data: dict) -> list:
        """Analyze all stocks and return top 5 recommendations."""
        print("[*] Analyzing stocks based on:")
        print("   • 5-day price momentum")
        print("   • Monthly trend analysis")
        print("   • Volume patterns")
        print("   • Daily price action")
        print("   • Price positioning\n")

        scores = []
        for stock in self.stocks:
            result = self.calculate_score(stock, data)
            if result:
                scores.append(result)

        # Sort by score (highest first)
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:5]

    def display_recommendations(self, top_5: list) -> None:
        """Display top 5 stock recommendations with details."""
        print(f"\n{'='*70}")
        print("  *** TOP 5 STOCKS TO INVEST TODAY ***")
        print(f"{'='*70}\n")

        for rank, stock in enumerate(top_5, 1):
            print(f"#{rank}. {stock['stock']}")
            print(f"    Current Price     : ₹ {stock['current_price']:.2f}")
            print(f"    Investment Score  : {stock['score']:.2f}/100")
            print(f"    Daily Change      : {stock['daily_change']:+.2f}%")
            print(f"    5-Day Momentum    : {stock['momentum_pct']:+.2f}%")
            print(f"    Monthly Trend     : {stock['month_trend']:+.2f}%")
            print(f"    Volume Ratio      : {stock['volume_ratio']:.2f}x average")
            print()

    def run(self) -> None:
        """Execute full analysis."""
        try:
            data = self.fetch_stock_data()

            if not data:
                print("[ERROR] Could not fetch any stock data. Please check your internet connection.")
                return

            top_5 = self.analyze_and_recommend(data)
            self.display_recommendations(top_5)

            print(f"{'='*70}")
            print("[WARNING] DISCLAIMER:")
            print("   This analysis is for educational purposes only.")
            print("   Not financial advice. Do your own research before investing.")
            print("   Past performance does not guarantee future results.")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"[ERROR] Error during analysis: {e}")
            print("Please check your internet connection and try again.")


def main():
    analyzer = StockAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
