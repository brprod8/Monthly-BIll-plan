"""
portfolio_gui.py

Example Python script implementing a portfolio movement plan GUI with
calculated potential profits for each proposed trade.
Updates a CSV of companies first (via closingprice.py), then runs the GUI.
"""

import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import closingprice  # <-- Import the separate module

# ---------------------------
# RE-USE YOUR EXISTING LOGIC:
# ---------------------------

def calculate_trades_to_goal(starting_balance: float, risk_per_trade: float, win_rate: float):
    trades_needed = starting_balance / risk_per_trade
    winning_trades = trades_needed * win_rate
    return trades_needed, winning_trades

def risk_to_reward_calculations(risk_amount: float):
    return {
        "1:1": risk_amount * 1,
        "2:1": risk_amount * 2,
        "3:1": risk_amount * 3,
        "4:1": risk_amount * 4
    }

def position_size_by_risk(risk_amount: float, share_price: float):
    return int(risk_amount // share_price)

def calculate_sell_price(buy_price: float, win_rate: float):
    return buy_price + (buy_price * win_rate)

def import_from_csv(csv_filename):
    companies_list = []
    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            buy_price = float(row["buy_price"])
            companies_list.append({"ticker": row["ticker"], "buy_price": buy_price})
    return companies_list

def build_trade_plan(companies, risk_per_company, win_rate):
    plan = []
    for c in companies:
        ticker = c["ticker"]
        buy_price = c["buy_price"]
        
        shares = position_size_by_risk(risk_per_company, buy_price)
        sell_price = calculate_sell_price(buy_price, win_rate)
        profit = (sell_price - buy_price) * shares
        
        plan.append({
            "ticker": ticker,
            "buy_price": buy_price,
            "position_size": shares,
            "sell_price": round(sell_price, 2),
            "profit": round(profit, 2)
        })
    return plan

def match_win_rate_to_bills(
    monthly_bills: float,
    trades_per_month: int,
    risk_per_trade: float,
    reward_to_risk: float
) -> float:
    if trades_per_month <= 0 or risk_per_trade <= 0 or reward_to_risk <= 0:
        raise ValueError("All input parameters must be positive and non-zero.")
    required_win_rate = ((monthly_bills / (trades_per_month * risk_per_trade)) + 1) / (reward_to_risk + 1)
    return required_win_rate

# ---------------------------
# TKINTER FRONTEND CLASS
# ---------------------------

class PortfolioGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Movement Plan")

        # Labels and Entries for parameters
        tk.Label(root, text="Starting Balance:").grid(row=0, column=0, sticky="e")
        tk.Label(root, text="Monthly Bills:").grid(row=1, column=0, sticky="e")
        tk.Label(root, text="Trades (estimate):").grid(row=2, column=0, sticky="e")
        tk.Label(root, text="Max Portfolio Risk (%):").grid(row=3, column=0, sticky="e")
        tk.Label(root, text="Risk per Trade (% of Max):").grid(row=4, column=0, sticky="e")
        tk.Label(root, text="Reward to Risk Ratio:").grid(row=5, column=0, sticky="e")

        self.entry_balance = tk.Entry(root)
        self.entry_balance.insert(0, "35000")
        self.entry_balance.grid(row=0, column=1)

        self.entry_bills = tk.Entry(root)
        self.entry_bills.insert(0, "3500")
        self.entry_bills.grid(row=1, column=1)

        self.entry_trades_needed = tk.Entry(root)
        self.entry_trades_needed.insert(0, "50")
        self.entry_trades_needed.grid(row=2, column=1)

        self.entry_portfolio_risk_pct = tk.Entry(root)
        self.entry_portfolio_risk_pct.insert(0, "0.25")
        self.entry_portfolio_risk_pct.grid(row=3, column=1)

        self.entry_risk_per_trade_pct = tk.Entry(root)
        self.entry_risk_per_trade_pct.insert(0, "0.02")
        self.entry_risk_per_trade_pct.grid(row=4, column=1)

        self.entry_rr_ratio = tk.Entry(root)
        self.entry_rr_ratio.insert(0, "3")
        self.entry_rr_ratio.grid(row=5, column=1)

        # Buttons
        tk.Button(root, text="Select CSV", command=self.select_csv_file).grid(row=6, column=0, pady=5)
        tk.Button(root, text="Calculate Plan", command=self.calculate_plan).grid(row=6, column=1, pady=5)

        # Text widget to display results
        self.result_text = tk.Text(root, width=80, height=20)
        self.result_text.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        # Placeholder for the CSV filename
        self.csv_filename = "companies_to_trade.csv"

    def select_csv_file(self):
        """Let user pick a CSV file with ticker,buy_price columns."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.csv_filename = file_path

    def calculate_plan(self):
        """Perform the core logic and display output in the text box."""
        self.result_text.delete("1.0", tk.END)  # Clear previous results

        try:
            # 1. Get user input
            starting_balance = float(self.entry_balance.get())
            monthly_bills = float(self.entry_bills.get())
            trades_needed = float(self.entry_trades_needed.get())
            max_portfolio_risk_pct = float(self.entry_portfolio_risk_pct.get())
            risk_per_trade_pct = float(self.entry_risk_per_trade_pct.get())
            reward_to_risk = float(self.entry_rr_ratio.get())

            # 2. Derived values
            max_portfolio_risk = starting_balance * max_portfolio_risk_pct
            risk_per_trade = max_portfolio_risk * risk_per_trade_pct

            needed_win_rate = match_win_rate_to_bills(
                monthly_bills,
                int(trades_needed),
                risk_per_trade,
                reward_to_risk,
            )

            trades_needed_calc, winning_trades = calculate_trades_to_goal(
                max_portfolio_risk,
                risk_per_trade,
                needed_win_rate
            )
            max_loss = (trades_needed_calc - winning_trades) * risk_per_trade

            # 3. Import companies from CSV
            companies_to_trade = import_from_csv(self.csv_filename)
            if not companies_to_trade:
                messagebox.showwarning(
                    "No Companies",
                    f"No companies found in '{self.csv_filename}'."
                )
                return

            number_of_companies = len(companies_to_trade)
            risk_per_company = max_portfolio_risk / number_of_companies
            wins_per_trade = needed_win_rate / (number_of_companies / 100.0)

            # 4. Build trade plan
            trade_plan = build_trade_plan(companies_to_trade, risk_per_company, needed_win_rate)

            # 5. Summaries to display
            output_lines = []
            output_lines.append("=== Target Goals Calculation ===")
            output_lines.append(f"Distributed ${max_portfolio_risk:.2f} to cover ${monthly_bills:.2f} in bills")
            output_lines.append(f"Trades Needed to Reach Goal: {trades_needed_calc:.2f}")
            output_lines.append(f"Expected Winning Trades:      {winning_trades:.2f}")
            output_lines.append(f"Max Possible Loss:            ${max_loss:.2f}\n")

            rr_calcs = risk_to_reward_calculations(risk_per_trade)
            output_lines.append("=== Risk to Reward Summary for a Single Trade ===")
            for rr, value in rr_calcs.items():
                output_lines.append(f"{rr} => ${value:.2f}")
            output_lines.append("")

            output_lines.append("=== Portfolio Risk Management ===")
            output_lines.append(f"Max Portfolio Risk ({max_portfolio_risk_pct*100:.0f}%): ${max_portfolio_risk:.2f}")
            output_lines.append(f"Risk per Trade ({risk_per_trade_pct*100:.0f}%):      ${risk_per_trade:.2f}\n")

            output_lines.append("=== Dynamic Allocation Across Companies ===")
            output_lines.append(f"Number of Companies:   {number_of_companies}")
            output_lines.append(f"Risk per Company:      ${risk_per_company:.2f}")
            output_lines.append(f"Forecasted Win Rate:   {wins_per_trade:.2f} (per-company calc)")
            output_lines.append(f"Matches {needed_win_rate:.2f} total win rate across "
                                f"${max_portfolio_risk:.2f} allocated to cover ${monthly_bills:.2f} bills\n")

            output_lines.append("=== Proposed Trade Plan ===")
            total_potential_profit = 0.0
            for trade in trade_plan:
                total_potential_profit += trade["profit"]
                line = (f"Ticker: {trade['ticker']} | "
                        f"Buy Price: ${trade['buy_price']:.2f} | "
                        f"Shares: {trade['position_size']} | "
                        f"Sell Price: ${trade['sell_price']:.2f} | "
                        f"Potential Profit: ${trade['profit']:.2f}")
                output_lines.append(line)

            output_lines.append("\n=== Summary ===")
            output_lines.append(f"Starting Balance:           ${starting_balance:.2f}")
            output_lines.append(f"Trades Needed (Estimate):   {trades_needed_calc:.0f}")
            output_lines.append(f"Expected Winning Trades:    {winning_trades:.1f}")
            output_lines.append(f"Max Portfolio Risk (25%):   ${max_portfolio_risk:.2f}")
            output_lines.append(f"Total Potential Profit:     ${total_potential_profit:.2f}")

            breakeven_str = (
                f"\nTo cover ${monthly_bills:.2f} in bills with {trades_needed_calc:.0f} trades/month, "
                f"risking ${risk_per_trade:.2f} each, at {reward_to_risk:.1f}:1 R:R, "
                f"you need a win rate of at least {needed_win_rate*100:.2f}%.\n"
            )
            output_lines.append(breakeven_str)

            if needed_win_rate > 1.0:
                output_lines.append("Warning: Required win rate is over 100%. This plan is not realistic.")
            elif needed_win_rate < 0.0:
                output_lines.append("Warning: Calculated win rate is negative. Check input assumptions.")
            else:
                output_lines.append("This required win rate is within a feasible 0% to 100% range.")

            output_lines.append("Trade plan is ready for further processing or execution...")

            # 6. Insert output into the text widget
            final_output = "\n".join(output_lines)
            self.result_text.insert(tk.END, final_output)

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

def main():
    """
    In 'main()' we first update the 'companies_to_trade.csv' with the latest
    closing prices, then we start the Tkinter GUI.
    """
    # 1. Tickers you want to track/update
    tickers = ["AMZN", "TGT", "NVDA", "GOOGL", "MSFT"]
    csv_filename = "companies_to_trade.csv"

    # 2. Update the CSV *before* running the GUI
    print(closingprice.import_from_csv(csv_filename))

    # 3. Launch the GUI
    root = tk.Tk()
    gui = PortfolioGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
