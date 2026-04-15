#!/usr/bin/env python3
import requests
from datetime import datetime
from collections import defaultdict

EMAIL = "galyasurr14@gmail.com"
API_KEY = "$2a$10$7UoEVxWqBR.VRiRXz8Ch6uJSCXWtVHB6VA5UnMPvD/4C5F1VfMWtW"
AUTH = "Key " + EMAIL + ":" + API_KEY
BASE = "https://console.overwolf.com/api/stats"
BOT_TOKEN = "8743101257" + ":AAFUU6jvsOlD9UDUfMlmeCMFQGojSaYUzgA"
CHAT_ID = "963016639"

APP_IDS = [
    "ajmnodkkadanooppeoeiipkhfonepdmjjlgomdfa",
    "flicmkjhlmjkhfjngkcggjhmddjneknbadaelkbh",
    "kiglhbmjdbkpnjoeoghfdbjkdmehnjidkiblddgf",
]
APP_NAMES = {
    "ajmnodkkadanooppeoeiipkhfonepdmjjlgomdfa": "Deadlock Companion",
    "flicmkjhlmjkhfjngkcggjhmddjneknbadaelkbh": "RecycleMe",
    "kiglhbmjdbkpnjoeoghfdbjkdmehnjidkiblddgf": "Arknights Companion",
}


def fetch_daily_net(app_id):
    headers = {"Authorization": AUTH}
    url = (
        BASE + "/revenue/display-ads-revenue-net"
        + "?app_id=" + app_id
        + "&days_back=Last%20365%20Days"
    )
    return requests.get(url, headers=headers, timeout=60)


def telegram_send(text):
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data).raise_for_status()


if __name__ == "__main__":
    now = datetime.now()
    this_month = now.strftime("%Y-%m")
    prev_month_num = now.month - 1
    prev_month_year = now.year
    if prev_month_num == 0:
        prev_month_num = 12
        prev_month_year -= 1
    last_month = str(prev_month_year) + "-" + str(prev_month_num).zfill(2)

    now_str = now.strftime("%d/%m/%Y %H:%M")
    msg = "\U0001f4ca <b>Overwolf Revenue Report</b>\n" + now_str + "\n"

    combined_monthly = defaultdict(float)
    combined_today = 0.0

    for app_id in APP_IDS:
        name = APP_NAMES[app_id]
        msg += "\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        msg += "\U0001f3ae <b>" + name + "</b>\n"

        r = fetch_daily_net(app_id)
        if r.status_code != 200:
            msg += "\u274c Error " + str(r.status_code) + ": " + r.text[:200] + "\n"
            continue

        rows = r.json().get("rows", [])
        monthly = defaultdict(float)
        today_value = 0.0
        today_date = now.strftime("%Y-%m-%d")

        for row in rows:
            date = (row.get("revenue_date") or row.get("date") or "")[:10]
            net = float(row.get("daily_total_net_revenue") or 0)
            if date:
                month_key = date[:7]
                monthly[month_key] += net
                combined_monthly[month_key] += net
                if date == today_date:
                    today_value = net

        combined_today += today_value
        this_m = monthly.get(this_month, 0.0)
        last_m = monthly.get(last_month, 0.0)

        msg += "\U0001f4b0 Today: $" + str(round(today_value, 2)) + "\n"
        msg += "\U0001f4b0 This month: $" + str(round(this_m, 2)) + "\n"
        msg += "\U0001f4c5 Last month: $" + str(round(last_m, 2)) + "\n"
        msg += "\n\U0001f4c8 Last 12 months breakdown:\n"
        for m in sorted(monthly.keys())[-13:]:
            msg += "  \u2022 " + m + ": $" + str(round(monthly[m], 2)) + "\n"
        year_total = sum(v for k, v in monthly.items() if k.startswith(str(now.year)))
        msg += "Year total: $" + str(round(year_total, 2)) + "\n"

    msg += "\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
    msg += "\U0001f4b9 <b>All Apps Combined</b>\n"
    msg += "\U0001f4b0 Today: $" + str(round(combined_today, 2)) + "\n"
    msg += "\U0001f4b0 This month: $" + str(round(combined_monthly.get(this_month, 0), 2)) + "\n"
    msg += "\U0001f4c5 Last month: $" + str(round(combined_monthly.get(last_month, 0), 2)) + "\n"
    msg += "\n\U0001f4c8 Last 12 months breakdown:\n"
    for m in sorted(combined_monthly.keys())[-13:]:
        msg += "  \u2022 " + m + ": $" + str(round(combined_monthly[m], 2)) + "\n"
    combined_year = sum(v for k, v in combined_monthly.items() if k.startswith(str(now.year)))
    msg += "Year total: $" + str(round(combined_year, 2)) + "\n"

    telegram_send(msg)
    print("Done!")
