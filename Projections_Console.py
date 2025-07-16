import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def get_financials(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T  # years as rows
    try:
        revenue = financials['Total Revenue'].dropna() / 1e9  # billions
        net_income = financials['Net Income'].dropna() / 1e9
        return revenue, net_income, stock
    except KeyError:
        print(f"\n⚠️ Missing 'Total Revenue' or 'Net Income' for {ticker}.")
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
    # Resample to get yearly closing price at year-end (adjusted close)
    yearly = hist['Close'].resample('YE').last()
    yearly.index = yearly.index.year.astype(str)
    return yearly

def main():
    ticker = input("Enter stock ticker (e.g., AAPL): ").upper()
    revenue, net_income, stock = get_financials(ticker)

    # Sort oldest to newest, last 4 years
    revenue = revenue.sort_index().tail(4)
    net_income = net_income.sort_index().tail(4)

    if len(revenue) < 1 or len(net_income) < 1:
        print("\n⚠️ Not enough data to run projection.")
        return

    print(f"\nLast 4 Years of Revenue (Billions):\n{revenue}")
    print(f"\nLast 4 Years of Net Income (Billions):\n{net_income}")

    try:
        rev_growth = float(input("\nEstimated annual revenue growth rate (e.g., 0.08 for 8%): "))
        ni_growth = float(input("Estimated annual net income growth rate: "))
        pe_low = float(input("Low P/E estimate: "))
        pe_high = float(input("High P/E estimate: "))
    except ValueError:
        print("\n❌ Invalid input. Use decimal format (e.g., 0.08 for 8%).")
        return

    shares_outstanding = stock.info.get("sharesOutstanding", None)
    if shares_outstanding is None:
        print("⚠️ Could not retrieve shares outstanding from Yahoo Finance.")
        return
    shares_outstanding = shares_outstanding / 1e9  # to billions
    print(f"\n🧾 Shares Outstanding (from Yahoo): {shares_outstanding:.2f} billion")

    eps_ttm = stock.info.get('trailingEps', None)
    current_price = stock.info.get('currentPrice', None)
    if eps_ttm is None or current_price is None:
        print("⚠️ Could not retrieve current EPS TTM or current stock price quote.")
        insert_current = False
    else:
        insert_current = True
        print(f"\n🔎 Current EPS (TTM): {eps_ttm:.4f}")
        print(f"🔎 Current Stock Price Quote: ${current_price:.2f}")

    rev_proj = project_growth(revenue.values, rev_growth, years=4)
    ni_proj = project_growth(net_income.values, ni_growth, years=4)

    hist_years = revenue.index.year.astype(int).tolist()
    last_year = hist_years[-1]
    proj_years = [last_year + i for i in range(1, 5)]

    rev_list = list(revenue.values)
    ni_list = list(net_income.values)

    price_hist = get_historical_prices(stock, hist_years[0], last_year)
    price_hist_list = [price_hist.get(str(y), None) for y in hist_years]

    if insert_current:
        current_year = last_year + 0.5
        ni_current = eps_ttm * shares_outstanding
        if len(revenue) >= 2:
            recent_rev_growth = (revenue.values[-1] - revenue.values[-2]) / revenue.values[-2]
            rev_current = revenue.values[-1] * (1 + recent_rev_growth)
        else:
            rev_current = revenue.values[-1]

        price_low_proj = [(ni / shares_outstanding) * pe_low for ni in ni_proj]
        price_high_proj = [(ni / shares_outstanding) * pe_high for ni in ni_proj]

        price_low_current = eps_ttm * pe_low
        price_high_current = eps_ttm * pe_high

        all_years = hist_years + [current_year] + proj_years
        rev_combined = rev_list + [rev_current] + rev_proj
        ni_combined = ni_list + [ni_current] + ni_proj

        price_low = [None]*len(hist_years) + [price_low_current] + price_low_proj
        price_high = [None]*len(hist_years) + [price_high_current] + price_high_proj
        price_hist_extended = price_hist_list + [current_price] + [None]*len(proj_years)
    else:
        all_years = hist_years + proj_years
        rev_combined = rev_list + rev_proj
        ni_combined = ni_list + ni_proj

        price_low_proj = [(ni / shares_outstanding) * pe_low for ni in ni_proj]
        price_high_proj = [(ni / shares_outstanding) * pe_high for ni in ni_proj]
        price_low = [None]*len(hist_years) + price_low_proj
        price_high = [None]*len(hist_years) + price_high_proj
        price_hist_extended = price_hist_list + [None]*len(proj_years)

    all_years_labels = [str(y) if int(y) == y else f"{int(y)}.5" for y in all_years]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    x_vals = list(range(len(all_years)))
    x_hist = list(range(len(hist_years)))
    x_current = [len(hist_years)] if insert_current else []
    x_proj = list(range(len(hist_years) + (1 if insert_current else 0), len(all_years)))

    ax1.plot(x_hist, rev_combined[:len(hist_years)], label="Revenue (Historical)", marker='o', color='tab:blue')
    ax1.plot(x_hist, ni_combined[:len(hist_years)], label="Net Income (Historical)", marker='o', color='tab:orange')
        # --- Draw connection lines for current revenue and net income ---
    if insert_current:
        x_prev = x_hist[-1]
        x_curr = x_current[0]
        x_next = x_proj[0]

        # Revenue connections
        y_rev_prev = rev_combined[x_prev]
        y_rev_curr = rev_combined[x_curr]
        y_rev_next = rev_combined[x_next]
        ax1.plot([x_prev, x_curr], [y_rev_prev, y_rev_curr], linestyle='-', color='tab:blue', linewidth=1.5)
        ax1.plot([x_curr, x_next], [y_rev_curr, y_rev_next], linestyle=':', color='tab:blue', linewidth=1.5)

        # Net income connections
        y_ni_prev = ni_combined[x_prev]
        y_ni_curr = ni_combined[x_curr]
        y_ni_next = ni_combined[x_next]
        ax1.plot([x_prev, x_curr], [y_ni_prev, y_ni_curr], linestyle='-', color='tab:orange', linewidth=1.5)
        ax1.plot([x_curr, x_next], [y_ni_curr, y_ni_next], linestyle=':', color='tab:orange', linewidth=1.5)

    if insert_current:
        ax1.plot(x_current, [rev_combined[len(hist_years)]], label="Revenue (Current, est.)", marker='o', linestyle=':', color='tab:blue')
        ax1.plot(x_current, [ni_combined[len(hist_years)]], label="Net Income (Current, est.)", marker='o', linestyle=':', color='tab:orange')

    ax1.plot(x_proj, rev_combined[-len(proj_years):], label="Revenue (Projected)", marker='o', linestyle='--', color='tab:blue')
    ax1.plot(x_proj, ni_combined[-len(proj_years):], label="Net Income (Projected)", marker='o', linestyle='--', color='tab:orange')

    ax1.set_ylabel("Billions USD")
    ax1.set_title(f"{ticker} – Financials: 4-Year History + Current + 4-Year Projection")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(x_hist, price_hist_extended[:len(hist_years)], label="Historical Price", marker='o', color='blue')
    if insert_current:
        ax2.plot(x_current, [price_hist_extended[len(hist_years)]], label="Current Price (Quote)", marker='o', color='purple')
    ax2.plot(x_proj, price_low[-len(proj_years):], label="Price Low Estimate", marker='x', linestyle='-.', color='red')
    ax2.plot(x_proj, price_high[-len(proj_years):], label="Price High Estimate", marker='x', linestyle='-.', color='green')

    ax2.set_ylabel("Stock Price (USD)")
    ax2.set_title(f"{ticker} – Stock Price: Historical, Current & Projected")
    ax2.grid(True)
    ax2.legend()

    plt.xticks(ticks=x_vals, labels=all_years_labels)

    def plot_price_conn(x1, y1, x2, y2):
        if y1 is not None and y2 is not None:
            ax2.plot([x1, x2], [y1, y2], color='gray', linestyle=':', linewidth=1)

    if insert_current:
        y_last_hist = price_hist_extended[len(hist_years)-1]
        y_current = price_hist_extended[len(hist_years)]
        y_low_proj0 = price_low_proj[0]
        y_high_proj0 = price_high_proj[0]
        plot_price_conn(x_hist[-1], y_last_hist, x_current[0], y_current)
        plot_price_conn(x_current[0], y_current, x_proj[0], y_low_proj0)
        plot_price_conn(x_current[0], y_current, x_proj[0], y_high_proj0)
    else:
        y_last_hist = price_hist_extended[len(hist_years)-1]
        y_low_proj0 = price_low_proj[0]
        y_high_proj0 = price_high_proj[0]
        plot_price_conn(x_hist[-1], y_last_hist, x_proj[0], y_low_proj0)
        plot_price_conn(x_hist[-1], y_last_hist, x_proj[0], y_high_proj0)

    def annotate_prices(ax, x_vals, y_vals, color):
        for x, y in zip(x_vals, y_vals):
            if y is not None:
                ax.annotate(f"${y:.2f}", (x, y), textcoords="offset points", xytext=(0, 8),
                            ha='center', fontsize=9, color=color)

    annotate_prices(ax2, x_hist, price_hist_extended[:len(hist_years)], 'blue')
    if insert_current:
        annotate_prices(ax2, x_current, [price_hist_extended[len(hist_years)]], 'purple')
    annotate_prices(ax2, x_proj, price_low[-len(proj_years):], 'red')
    annotate_prices(ax2, x_proj, price_high[-len(proj_years):], 'green')

    def annotate_proj_change(ax, x_start, y_start, x_end, y_end, color, label):
        if y_start is None or y_end is None:
            return
        pct_change = (y_end - y_start) / y_start * 100
        x_mid = (x_start + x_end) / 2
        y_mid = (y_start + y_end) / 2
        offset_y = 30 if color == 'green' else -40
        ax.annotate(f"{label}\n{pct_change:+.1f}%",
            xy=(x_mid, y_mid),
            xytext=(0, offset_y),
            textcoords='offset points',
            ha='center',
            fontsize=9,
            color=color,
            arrowprops=dict(arrowstyle='->', color=color, lw=1))

    if insert_current:
        x_current_idx = len(hist_years)
        x_first_proj_idx = len(hist_years) + 1
        y_current_price = price_hist_extended[x_current_idx]
        y_low_first_proj = price_low_proj[0]
        y_high_first_proj = price_high_proj[0]
        annotate_proj_change(ax2, x_current_idx, y_current_price,
                             x_first_proj_idx, y_low_first_proj, 'red', "Low Price")
        annotate_proj_change(ax2, x_current_idx, y_current_price,
                             x_first_proj_idx, y_high_first_proj, 'green', "High Price")
    else:
        x_last_hist_idx = len(hist_years) - 1
        x_first_proj_idx = len(hist_years)
        y_last_hist_price = price_hist_extended[x_last_hist_idx]
        y_low_first_proj = price_low_proj[0]
        y_high_first_proj = price_high_proj[0]
        annotate_proj_change(ax2, x_last_hist_idx, y_last_hist_price,
                             x_first_proj_idx, y_low_first_proj, 'red', "Low Price")
        annotate_proj_change(ax2, x_last_hist_idx, y_last_hist_price,
                             x_first_proj_idx, y_high_first_proj, 'green', "High Price")

    def scale_ylim(ax):
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, ymax * 1.15)

    scale_ylim(ax1)
    scale_ylim(ax2)

    # 🔼 Add annotations for Revenue and Net Income
    def annotate_financials(ax, x_vals, y_vals, color, prefix=""):
        for x, y in zip(x_vals, y_vals):
            if y is not None:
                ax.annotate(f"{prefix}{y:.2f}", (x, y),
                            textcoords="offset points", xytext=(0, 8),
                            ha='center', fontsize=9, color=color)

    annotate_financials(ax1, x_hist, rev_combined[:len(hist_years)], 'tab:blue', prefix="$")
    annotate_financials(ax1, x_hist, ni_combined[:len(hist_years)], 'tab:orange', prefix="$")
    if insert_current:
        annotate_financials(ax1, x_current, [rev_combined[len(hist_years)]], 'tab:blue', prefix="$")
        annotate_financials(ax1, x_current, [ni_combined[len(hist_years)]], 'tab:orange', prefix="$")
    annotate_financials(ax1, x_proj, rev_combined[-len(proj_years):], 'tab:blue', prefix="$")
    annotate_financials(ax1, x_proj, ni_combined[-len(proj_years):], 'tab:orange', prefix="$")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
