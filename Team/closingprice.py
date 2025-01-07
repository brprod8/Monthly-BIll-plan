import csv
import yfinance as yf

def filter_stocks_by_close(symbols, max_price):
    """
    Given a list of symbols and a maximum closing price,
    return a list of (symbol, last_close) where last_close <= max_price.
    """
    results = []
    for symbol in symbols:
        ticker_obj = yf.Ticker(symbol)
        hist = ticker_obj.history(period="1d")  
        
        if hist.empty:
            print(f"No data for {symbol}, skipping...")
            continue
        
        # Get the most recent close
        last_close = hist["Close"].iloc[-1]
        
        if last_close <= max_price:
            results.append((symbol, float(last_close)))
    
    return results

def export_to_csv(stocks, csv_filename):
    """
    Exports a list of (symbol, last_close) as CSV in the format:
        ticker,buy_price
        AAPL,145.32
        MSFT,198.75
    """
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["ticker", "buy_price"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for symbol, close_price in stocks:
            # Write out each row with keys matching the fieldnames
            writer.writerow({"ticker": symbol, "buy_price": close_price})

def import_from_csv(csv_filename):
    """
    Reads a CSV with columns 'ticker' and 'buy_price' and returns
    a list of dicts like:
        [
            {"ticker": "AMZN", "buy_price": 215.0},
            {"ticker": "TGT",  "buy_price": 139.0}
        ]
    """
    companies_list = []
    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert the string 'buy_price' to float
            buy_price = float(row["buy_price"])
            companies_list.append({
                "ticker": row["ticker"],
                "buy_price": buy_price
            })
    return companies_list

def main():
    # 1. Define a list of symbols and a maximum closing price
    companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]
    max_closing_price = 200
    
    # 2. Filter stocks under 'max_closing_price'
    stocks_under_price = filter_stocks_by_close(companies, max_closing_price)
    
    # 3. Export the filtered list to CSV in the format:
    #    ticker,buy_price
    #    AAPL,145.23
    #    MSFT,198.01
    csv_filename = "companies_to_trade.csv"
    export_to_csv(stocks_under_price, csv_filename)
    
    print(f"Filtered stocks saved to '{csv_filename}'.")
    
    # 4. Import from CSV and reconstruct the list of dicts
    reconstructed_list = import_from_csv(csv_filename)
    
    # 5. Print results to confirm the structure
    print("\nReconstructed list from CSV:")
    for item in reconstructed_list:
        print(item)

if __name__ == "__main__":
    main()
