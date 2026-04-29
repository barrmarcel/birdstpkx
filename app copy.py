from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# Your Webhook URL
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

def fetch_pkstockx_status(email, order_no):
    """
    Scrapes pkstockx.org to find the order status span.
    """
    # The target URL based on user input
    url = f"https://www.pkstockx.org/trackorder?email={email}&order={order_no}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for <span class="order-status label-success">
            status_element = soup.find("span", class_="order-status")
            if status_element:
                return status_element.text.strip()
            return "Status tag not found"
        return f"Site Error ({response.status_code})"
    except Exception as e:
        return "Connection Failed"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_method', methods=["GET", "POST"])
def get_numbers():
    print("🔥 ROUTE HIT /get_method")

    if request.method == "POST":
        print("✅ POST REQUEST RECEIVED")
        print("FORM DATA:", request.form)

        full_name = request.form.get("fullName")
        email = request.form.get("email")
        phone = request.form.get("phone")
        order_no = request.form.get("orderNo")

        print("📦 Parsed Data:", full_name, email, phone, order_no)

        order_status = fetch_pkstockx_status(email, order_no)
        print("📊 Scraped Status:", order_status)

        payload = {
            "username": "PKStockX Tracker",
            "content": "🚨 NEW ORDER RECEIVED (DEBUG MODE)",
            "embeds": [
                {
                    "title": "📦 Order Tracking Report",
                    "description": f"Live status check for **{full_name}**",
                    "color": 3066993,
                    "fields": [
                        {"name": "Customer Name", "value": f"{full_name}", "inline": True},
                        {"name": "Order Number", "value": f"`{order_no}`", "inline": True},
                        {"name": "Email Address", "value": f"{email}", "inline": True},
                        {"name": "Phone Number", "value": f"{phone}", "inline": True},
                        {"name": "Current Status", "value": f"**{order_status}**", "inline": False}
                    ],
                    "footer": {"text": "PKStockX Tracking System"}
                }
            ]
        }

        try:
            print("📡 Sending to Discord webhook...")
            response = requests.post(WEBHOOK_URL, json=payload)

            print("📬 Discord Status Code:", response.status_code)
            print("📬 Discord Response:", response.text)

            response.raise_for_status()

        except Exception as e:
            print("❌ Discord Error:", str(e))

    else:
        print("ℹ️ GET request received (no form submission)")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)