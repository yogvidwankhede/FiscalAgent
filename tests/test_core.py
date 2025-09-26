# tests/test_core.py
import os
from chatbot.core import FinancialChatbot

# Adjust this path if your CSV is stored elsewhere
CSV_PATH = os.path.join("data", "financials.csv")


def test_total_revenue_apple_2023():
    bot = FinancialChatbot(CSV_PATH)
    val = bot.total_revenue("Apple", year=2023)
    # from your CSV: Apple 2023 total revenue = 383285
    assert val is not None
    assert abs(val - 383285) < 1e-6


def test_total_revenue_microsoft_2024():
    bot = FinancialChatbot(CSV_PATH)
    val = bot.total_revenue("Microsoft", year=2024)
    # expected: 245122
    assert val is not None
    assert abs(val - 245122) < 1e-6


def test_net_income_change_tesla_2022_2023():
    bot = FinancialChatbot(CSV_PATH)
    resp = bot.net_income_change("Tesla", 2022, 2023)
    # Tesla 2022: 12556 ; 2023: 14997
    assert resp is not None
    assert "pct_change" in resp
    expected_pct = (14997 - 12556) / 12556 * 100
    assert abs(resp["pct_change"] - expected_pct) < 1e-6


def test_compare_companies_revenue_2023():
    bot = FinancialChatbot(CSV_PATH)
    comp = bot.compare_companies("Apple", "Microsoft", metric="total_revenue", year=2023)
    assert comp is not None
    assert comp["metric"] == "total_revenue"
    # Apple 2023 revenue > Microsoft 2023 revenue
    assert comp["a_val"] > comp["b_val"]


def test_trend_plot_returns_path():
    bot = FinancialChatbot(CSV_PATH)
    path = bot.trend_plot("Apple", "total_revenue")
    assert path is not None
    assert path.endswith(".png")
