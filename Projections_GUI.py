import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def get_financials(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    try:
        revenue = financials['Total Revenue'].dropna() / 1e9
        net_income = financials['Net Income'].dropna() / 1e9
        return revenue, net_income, stock
    except KeyError:
        messagebox.showwarning("Data Warning", f"Missing 'Total Revenue' or 'Net Income' for {ticker}.")
        return pd.Series(), pd.Series(), None

def project_growth(values, growth_rate, years=4):
    if len(values) == 0:
        return []
    last = values[-1]
    projections = []
    for _ in range(years):
        last *= (1 + growth_rate)
        projections.append(last)
    return projections

def get_historical_prices(stock, start_year, end_year):
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"
    hist = stock.history(start=start_date, end=end_date)
    yearly = hist['Close'].resample('YE').last()
    yearly.index = yearly.index.year.astype(str)
    return yearly

def update_chart(event=None):
    ticker = ticker_entry.get().upper()
    if not ticker:
        return

    # Get financials: revenue and net income in billions, plus the stock object
    revenue, net_income, stock = get_financials(ticker)
    # Sort oldest to newest and take last 4 years
    revenue = revenue.sort_index().tail(4)
    net_income = net_income.sort_index().tail(4)

    # If no data, clear plots and exit
    if len(revenue) < 1 or len(net_income) < 1:
        ax1.clear()
        ax2.clear()
        canvas.draw()
        return

    # Growth rates and P/E estimates from sliders (convert % to decimal)
    rev_growth = rev_growth_scale.get() / 100
    ni_growth = ni_growth_scale.get() / 100
    pe_low = pe_low_scale.get()
    pe_high = pe_high_scale.get()

    # Retrieve shares outstanding from stock info; warn if missing
    shares_outstanding = stock.info.get("sharesOutstanding", None)
    if shares_outstanding is None:
        messagebox.showwarning("Data Warning", "Could not retrieve shares outstanding.")
        return
    shares_outstanding = shares_outstanding / 1e9  # Convert to billions

    # Get trailing EPS and current price if available to include current estimates
    eps_ttm = stock.info.get('trailingEps', None)
    current_price = stock.info.get('currentPrice', None)
    insert_current = (eps_ttm is not None and current_price is not None)

    # Extract years from financials index for historical data
    hist_years = revenue.index.year.astype(int).tolist()
    last_year = hist_years[-1]
    proj_years = [last_year + i for i in range(1, 5)]  # Next 4 years

    # Convert series values to lists for easier manipulation
    rev_list = list(revenue.values)
    ni_list = list(net_income.values)

    # Get historical stock prices for those years
    price_hist = get_historical_prices(stock, hist_years[0], last_year)
    price_hist_list = [price_hist.get(str(y), None) for y in hist_years]

    if insert_current:
        # Define a half-year index to plot current estimated values
        current_year = last_year + 0.5

        # Calculate current net income from EPS and shares outstanding
        ni_current = eps_ttm * shares_outstanding

        # Estimate current revenue using recent growth if possible
        if len(revenue) >= 2:
            recent_rev_growth = (revenue.values[-1] - revenue.values[-2]) / revenue.values[-2]
            rev_current = revenue.values[-1] * (1 + recent_rev_growth)
        else:
            rev_current = revenue.values[-1]

        # Project future price lows and highs using P/E and projected net income
        price_low_proj = [(ni / shares_outstanding) * pe_low for ni in project_growth([ni_current], ni_growth, years=4)]
        price_high_proj = [(ni / shares_outstanding) * pe_high for ni in project_growth([ni_current], ni_growth, years=4)]

        # Price estimates for current EPS times P/E bounds
        price_low_current = eps_ttm * pe_low
        price_high_current = eps_ttm * pe_high

        # Combine all years for plotting: historical + current + projected
        all_years = hist_years + [current_year] + proj_years
        rev_combined = rev_list + [rev_current] + project_growth([rev_current], rev_growth, years=4)
        ni_combined = ni_list + [ni_current] + project_growth([ni_current], ni_growth, years=4)

        price_low = [None]*len(hist_years) + [price_low_current] + price_low_proj
        price_high = [None]*len(hist_years) + [price_high_current] + price_high_proj
        price_hist_extended = price_hist_list + [current_price] + [None]*len(proj_years)

    else:
        # If no current data, project from historical values only
        all_years = hist_years + proj_years
        rev_combined = rev_list + project_growth(rev_list, rev_growth, years=4)
        ni_combined = ni_list + project_growth(ni_list, ni_growth, years=4)

        price_low_proj = [(ni / shares_outstanding) * pe_low for ni in project_growth(ni_list, ni_growth, years=4)]
        price_high_proj = [(ni / shares_outstanding) * pe_high for ni in project_growth(ni_list, ni_growth, years=4)]
        price_low = [None]*len(hist_years) + price_low_proj
        price_high = [None]*len(hist_years) + price_high_proj
        price_hist_extended = price_hist_list + [None]*len(proj_years)

    # Create readable labels: years or year + 0.5 for current estimate
    all_years_labels = [str(y) if int(y) == y else f"{int(y)}.5" for y in all_years]

    # Clear previous plots
    ax1.clear()
    ax2.clear()

    # X-axis indices for historical, current and projected points
    x_vals = list(range(len(all_years)))
    x_hist = list(range(len(hist_years)))
    x_current = [len(hist_years)] if insert_current else []
    x_proj = list(range(len(hist_years) + (1 if insert_current else 0), len(all_years)))

    # Plot historical revenue and net income with markers
    ax1.plot(x_hist, rev_combined[:len(hist_years)], label="Revenue (Historical)", marker='o', color='tab:blue')
    ax1.plot(x_hist, ni_combined[:len(hist_years)], label="Net Income (Historical)", marker='o', color='tab:orange')

    # --- Draw connection lines for current revenue and net income ---
    if insert_current:
        x_prev = x_hist[-1]
        x_curr = x_current[0]
        x_next = x_proj[0]

        # Revenue connections: solid from last historical to current, dotted from current to projection start
        y_rev_prev = rev_combined[x_prev]
        y_rev_curr = rev_combined[x_curr]
        y_rev_next = rev_combined[x_next]
        ax1.plot([x_prev, x_curr], [y_rev_prev, y_rev_curr], linestyle='-', color='tab:blue', linewidth=1.5)
        ax1.plot([x_curr, x_next], [y_rev_curr, y_rev_next], linestyle=':', color='tab:blue', linewidth=1.5)

        # Net income connections: same style
        y_ni_prev = ni_combined[x_prev]
        y_ni_curr = ni_combined[x_curr]
        y_ni_next = ni_combined[x_next]
        ax1.plot([x_prev, x_curr], [y_ni_prev, y_ni_curr], linestyle='-', color='tab:orange', linewidth=1.5)
        ax1.plot([x_curr, x_next], [y_ni_curr, y_ni_next], linestyle=':', color='tab:orange', linewidth=1.5)

        # Plot markers for current estimates with dotted lines
        ax1.plot(x_current, [rev_combined[len(hist_years)]], label="Revenue (Current, est.)", marker='o', linestyle=':', color='tab:blue')
        ax1.plot(x_current, [ni_combined[len(hist_years)]], label="Net Income (Current, est.)", marker='o', linestyle=':', color='tab:orange')

    # Plot projected revenue and net income with dashed lines
    ax1.plot(x_proj, rev_combined[-len(proj_years):], label="Revenue (Projected)", marker='o', linestyle='--', color='tab:blue')
    ax1.plot(x_proj, ni_combined[-len(proj_years):], label="Net Income (Projected)", marker='o', linestyle='--', color='tab:orange')

    ax1.set_ylabel("Billions USD")
    ax1.set_title(f"{ticker} – Financials: 4-Year History + Current + 4-Year Projection")
    ax1.grid(True)
    ax1.legend()

    # Plot historical prices
    ax2.plot(x_hist, price_hist_extended[:len(hist_years)], label="Historical Price", marker='o', color='blue')

    # Plot current price marker if available
    if insert_current:
        ax2.plot(x_current, [price_hist_extended[len(hist_years)]], label="Current Price (Quote)", marker='o', color='purple')

    # Plot price estimate ranges with different markers and line styles
    ax2.plot(x_proj, price_low[-len(proj_years):], label="Price Low Estimate", marker='x', linestyle='-.', color='red')
    ax2.plot(x_proj, price_high[-len(proj_years):], label="Price High Estimate", marker='x', linestyle='-.', color='green')

    ax2.set_ylabel("Stock Price (USD)")
    ax2.set_title(f"{ticker} – Stock Price: Historical, Current & Projected")
    ax2.grid(True)
    ax2.legend()

    plt.xticks(ticks=x_vals, labels=all_years_labels)

    # Helper function to plot connection lines for price estimates if points exist
    def plot_price_conn(x1, x2, y1, y2, style, color):
        if y1 is not None and y2 is not None:
            ax2.plot([x1, x2], [y1, y2], linestyle=style, color=color, linewidth=1.5)

    # Draw connections from historical price to current price and current to projections
    if insert_current:
        # Connect last historical price to current price
        plot_price_conn(x_hist[-1], x_current[0], price_hist_extended[len(hist_years)-1], price_hist_extended[len(hist_years)], ':', 'purple')

        # Connect current price to first projected price low and high
        if price_low[-len(proj_years)] is not None:
            plot_price_conn(x_current[0], x_proj[0], price_hist_extended[len(hist_years)], price_low[-len(proj_years)], ':', 'red')
        if price_high[-len(proj_years)] is not None:
            plot_price_conn(x_current[0], x_proj[0], price_hist_extended[len(hist_years)], price_high[-len(proj_years)], ':', 'green')

        # --- Annotations for % change between current and first projected high/low ---
        first_proj_high = price_high[-len(proj_years)]
        first_proj_low = price_low[-len(proj_years)]
        current_price_val = price_hist_extended[len(hist_years)]

        if first_proj_high is not None and current_price_val is not None:
            pct_change_high = ((first_proj_high - current_price_val) / current_price_val) * 100
            ax2.annotate(f"{pct_change_high:+.1f}%", 
                         xy=(x_proj[0], first_proj_high), 
                         xytext=(x_proj[0]-0.4, first_proj_high),
                         color='green',
                         fontsize=10,
                         arrowprops=dict(arrowstyle="->", color='green'))

        if first_proj_low is not None and current_price_val is not None:
            pct_change_low = ((first_proj_low - current_price_val) / current_price_val) * 100
            ax2.annotate(f"{pct_change_low:+.1f}%", 
                         xy=(x_proj[0], first_proj_low), 
                         xytext=(x_proj[0]-0.4, first_proj_low),
                         color='red',
                         fontsize=10,
                         arrowprops=dict(arrowstyle="->", color='red'))

    plt.tight_layout()
    canvas.draw()


root = tk.Tk()
root.title("Stock Financials & Price Projection")

# Set a fixed window size or min size (you can adjust these)
root.geometry("1000x700")
root.minsize(900, 600)

# Add padding between widgets with 'padx' and 'pady'
tk.Label(root, text="Stock Ticker:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
ticker_entry = tk.Entry(root)
ticker_entry.grid(row=0, column=1, columnspan=3, sticky="we", padx=5, pady=5)
ticker_entry.bind("<Return>", update_chart)

tk.Label(root, text="Revenue Growth Rate (%)").grid(row=1, column=0, padx=5, pady=5)
rev_growth_scale = tk.Scale(root, from_=0, to=100, resolution=0.1, orient=tk.HORIZONTAL, command=lambda x: update_chart())
rev_growth_scale.set(8)
rev_growth_scale.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Net Income Growth Rate (%)").grid(row=1, column=2, padx=5, pady=5)
ni_growth_scale = tk.Scale(root, from_=0, to=100, resolution=0.1, orient=tk.HORIZONTAL, command=lambda x: update_chart())
ni_growth_scale.set(8)
ni_growth_scale.grid(row=1, column=3, padx=5, pady=5)

tk.Label(root, text="Low P/E Estimate").grid(row=2, column=0, padx=5, pady=5)
pe_low_scale = tk.Scale(root, from_=1, to=800, resolution=0.1, orient=tk.HORIZONTAL, command=lambda x: update_chart())
pe_low_scale.set(10)
pe_low_scale.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="High P/E Estimate").grid(row=2, column=2, padx=5, pady=5)
pe_high_scale = tk.Scale(root, from_=1, to=800, resolution=0.1, orient=tk.HORIZONTAL, command=lambda x: update_chart())
pe_high_scale.set(25)
pe_high_scale.grid(row=2, column=3, padx=5, pady=5)

# Create matplotlib figures and axes
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=3, column=0, columnspan=4, sticky="nsew")

# Make the grid expand properly
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure((0,1,2,3), weight=1)

update_chart()

root.mainloop()
