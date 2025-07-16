import yfinance as yf
import pandas as pd

def get_financials(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    try:
        revenue = financials['Total Revenue'].dropna() / 1e9
        net_income = financials['Net Income'].dropna() / 1e9
        return revenue.sort_index(), net_income.sort_index(), stock
    except KeyError:
        return pd.Series(), pd.Series(), None

def project_growth(values, growth_rate, years=4):
    if len(values) == 0:
        return []
    last = values[-1]
    return [last := last * (1 + growth_rate) for _ in range(years)]

def get_historical_prices(stock, start_year, end_year):
    hist = stock.history(start=f"{start_year}-01-01", end=f"{end_year}-12-31")
    return hist['Close'].resample('YE').last()

def export_to_excel(ticker, revenue, net_income, projections, price_hist, price_proj, current_price, shares_out, eps):
    file_name = f"{ticker}_financial_projection.xlsx"
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        # Sheet 1: Historical Financials
        df_hist = pd.DataFrame({
            "Revenue (B)": revenue,
            "Net Income (B)": net_income
        })
        df_hist.index.name = "Year"
        df_hist.to_excel(writer, sheet_name="Financials")

        # Sheet 2: Projections
        years_proj = [revenue.index[-1] + i for i in range(1, 5)]
        df_proj = pd.DataFrame({
            "Projected Revenue (B)": projections["rev_proj"],
            "Projected Net Income (B)": projections["ni_proj"],
            "Price Low": price_proj["low"],
            "Price High": price_proj["high"]
        }, index=years_proj)
        df_proj.index.name = "Year"
        df_proj.to_excel(writer, sheet_name="Projections")

        # Sheet 3: Stock Info
        df_info = pd.DataFrame({
            "Shares Outstanding (B)": [shares_out],
            "EPS (TTM)": [eps],
            "Current Price": [current_price]
        })
        df_info.to_excel(writer, sheet_name="Stock Info", index=False)

        # Sheet 4: Historical Prices
        price_hist.name = "Price (USD)"
        price_hist.index = price_hist.index.year
        price_hist.index.name = "Year"
        price_hist.to_frame().to_excel(writer, sheet_name="Price History")

    print(f"\n✅ Exported all data to '{file_name}'")

def main_excel():
    ticker = input("Enter stock ticker (e.g., AAPL): ").upper()
    revenue, net_income, stock = get_financials(ticker)
    revenue = revenue.tail(4)
    net_income = net_income.tail(4)

    if len(revenue) < 1 or len(net_income) < 1:
        print("⚠️ Not enough data to run projection.")
        return

    try:
        rev_growth = float(input("Estimated revenue growth (e.g., 0.08): "))
        ni_growth = float(input("Estimated net income growth: "))
        pe_low = float(input("Low P/E estimate: "))
        pe_high = float(input("High P/E estimate: "))
    except ValueError:
        print("❌ Invalid input.")
        return

    shares_out = stock.info.get("sharesOutstanding", None)
    eps = stock.info.get("trailingEps", None)
    current_price = stock.info.get("currentPrice", None)

    if not shares_out or not eps or not current_price:
        print("⚠️ Missing share or price data.")
        return

    shares_out_bil = shares_out / 1e9

    rev_proj = project_growth(revenue.values, rev_growth, 4)
    ni_proj = project_growth(net_income.values, ni_growth, 4)

    price_low = [(ni / shares_out_bil) * pe_low for ni in ni_proj]
    price_high = [(ni / shares_out_bil) * pe_high for ni in ni_proj]

    start_year = revenue.index[0].year
    end_year = revenue.index[-1].year
    price_hist = get_historical_prices(stock, start_year, end_year)

    projections = {
        "rev_proj": rev_proj,
        "ni_proj": ni_proj
    }

    price_proj = {
        "low": price_low,
        "high": price_high
    }

    export_to_excel(
        ticker,
        revenue,
        net_income,
        projections,
        price_hist,
        price_proj,
        current_price,
        shares_out_bil,
        eps
    )

if __name__ == "__main__":
    main_excel()
