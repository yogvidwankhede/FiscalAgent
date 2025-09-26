import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

import pandas as pd
import matplotlib.pyplot as plt
from rapidfuzz import process, fuzz

# Directory to store generated plots
PLOTS_DIR = Path(__file__).resolve().parent.parent / "static" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


class FinancialChatbot:
    """
    Analytics / Q&A bot for a financial CSV with columns:
    Year, Total Revenue, Net Income, Total Assets, Total Liabilities,
    Cash Flow from Operating Activities, Company
    """

    def __init__(self, csv_path: Union[str, Path]) -> None:
        # Load and normalize column names
        self.df = pd.read_csv(csv_path)
        self.df.columns = [c.strip().lower().replace(" ", "_") for c in self.df.columns]

        # Ensure numeric columns are numeric
        num_cols = [
            "year",
            "total_revenue",
            "net_income",
            "total_assets",
            "total_liabilities",
            "cash_flow_from_operating_activities",
        ]
        for col in num_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        # Unique company list for matching
        self.companies = sorted(self.df["company"].dropna().unique().tolist())

    # ---------- Internal helpers ----------

    def _best_company_match(self, name: str, threshold: int = 65) -> Optional[str]:
        if not name:
            return None
        result = process.extractOne(name, self.companies, scorer=fuzz.token_sort_ratio)
        return result[0] if result and result[1] >= threshold else None

    @staticmethod
    def _parse_years(text: str) -> List[int]:
        """
        Capture any 4-digit year starting with 19 or 20.
        """
        return [int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b", text)]

    @staticmethod
    def _safe_pct_change(old: float, new: float) -> float:
        if old == 0:
            return float("inf") if new != 0 else 0.0
        return (new - old) / abs(old) * 100.0

    # ---------- Core metrics ----------

    def total_revenue(self, company: str, year: Optional[int] = None) -> Optional[float]:
        df = self.df[self.df["company"].str.lower() == company.lower()]
        if year:
            df = df[df["year"] == year]
        return None if df.empty else float(df["total_revenue"].sum())

    def net_income_change(
        self, company: str, year1: int, year2: int
    ) -> Optional[Dict[str, float]]:
        df = self.df[self.df["company"].str.lower() == company.lower()]
        v1 = df.loc[df["year"] == year1, "net_income"]
        v2 = df.loc[df["year"] == year2, "net_income"]
        if v1.empty or v2.empty:
            return None
        val1, val2 = float(v1.iloc[0]), float(v2.iloc[0])
        return {
            "year1": year1,
            "year2": year2,
            "val1": val1,
            "val2": val2,
            "pct_change": self._safe_pct_change(val1, val2),
        }

    def compare_companies(
        self, company_a: str, company_b: str, metric: str, year: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Compare a metric (total_revenue or net_income) for two companies.
        """
        metric = metric.lower()
        if metric not in ["total_revenue", "net_income"]:
            return None
        df_a = self.df[self.df["company"].str.lower() == company_a.lower()]
        df_b = self.df[self.df["company"].str.lower() == company_b.lower()]
        if year:
            df_a = df_a[df_a["year"] == year]
            df_b = df_b[df_b["year"] == year]
        if df_a.empty or df_b.empty:
            return None
        a_val, b_val = float(df_a[metric].iloc[0]), float(df_b[metric].iloc[0])
        return {
            "company_a": company_a,
            "company_b": company_b,
            "metric": metric,
            "year": year,
            "a_val": a_val,
            "b_val": b_val,
            "diff": a_val - b_val,
            "pct_diff": self._safe_pct_change(b_val, a_val),
        }

    def trend_plot(self, company: str, metric: str) -> Optional[str]:
        """
        Generate a line plot of a metric across years for a company.
        Returns the relative path to the saved PNG.
        """
        metric = metric.lower()
        if metric not in self.df.columns:
            return None
        df = (
            self.df[self.df["company"].str.lower() == company.lower()]
            .dropna(subset=[metric, "year"])
            .sort_values("year")
        )
        if df.empty:
            return None
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(df["year"], df[metric], marker="o", color="tab:blue")
        ax.set_title(f"{company} — {metric.replace('_', ' ').title()} Trend")
        ax.set_xlabel("Year")
        ax.set_ylabel(metric.replace("_", " ").title())
        ax.grid(True, linestyle="--", alpha=0.6)
        fname = f"{company.replace(' ', '_')}_{metric}_{int(datetime.utcnow().timestamp())}.png"
        path = PLOTS_DIR / fname
        fig.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close(fig)
        return f"/static/plots/{fname}"

    # ---------- Simple text interface ----------

    def interpret(self, text: str, session: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Rudimentary intent handler:
        e.g. 'Total revenue for Apple in 2023'
        """
        session = session or {}
        t = text.lower()

        # Detect company (exact match or fuzzy)
        company = next((c for c in self.companies if c.lower() in t), None)
        if not company:
            m = re.search(r"for\s+([A-Za-z0-9 &._-]+)", text, re.I)
            if m:
                company = self._best_company_match(m.group(1).strip())

        years = self._parse_years(text)

        # Detect metric
        if "revenue" in t:
            metric = "total_revenue"
        elif "net income" in t or "profit" in t:
            metric = "net_income"
        else:
            metric = None

        # Total revenue intent
        if metric == "total_revenue" and ("total" in t or "sum" in t or "overall" in t):
            if not company:
                return {"text": "Which company?", "image": None, "session": session}
            year = years[0] if years else None
            val = self.total_revenue(company, year)
            if val is None:
                return {"text": "No data found.", "image": None, "session": session}
            return {
                "text": f"Total revenue for {company}{' in ' + str(year) if year else ''} is ${val:,.0f}.",
                "image": None,
                "session": session,
            }

        # Net income change intent
        if metric == "net_income" and "change" in t and len(years) >= 2:
            if not company:
                return {"text": "Which company?", "image": None, "session": session}
            res = self.net_income_change(company, years[0], years[1])
            if not res:
                return {"text": "No data for those years.", "image": None, "session": session}
            sign = "increased" if res["pct_change"] > 0 else "decreased"
            return {
                "text": f"{company}'s net income {sign} from ${res['val1']:,} in {res['year1']} "
                        f"to ${res['val2']:,} in {res['year2']} "
                        f"({res['pct_change']:.2f}% change).",
                "image": None,
                "session": session,
            }

        # Trend / plot intent
        if "trend" in t or "plot" in t or "chart" in t:
            if not company:
                return {"text": "Which company's trend?", "image": None, "session": session}
            if not metric:
                metric = "total_revenue"
            img = self.trend_plot(company, metric)
            return {
                "text": f"Here's the {metric.replace('_', ' ')} trend for {company}.",
                "image": img,
                "session": session,
            }

        # Fallback
        return {
            "text": "Sorry, I can answer things like:\n"
                    "- 'Total revenue for Apple in 2023'\n"
                    "- 'Net income change for Microsoft between 2022 and 2024'\n"
                    "- 'Show revenue trend for Tesla'",
            "image": None,
            "session": session,
        }
