from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Your Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1497801972085166100/wVht_t-TlPc62u-GeorvD3DwlcaIjGzc3yD6ZGbAWN9DJc-w4nK7QRTVVpWH6RwoJTAq"

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
    if request.method == "POST":
        # 1. Pulling fields from the HTML form
        full_name = request.form.get("fullName")
        email = request.form.get("email")
        phone = request.form.get("phone")
        order_no = request.form.get("orderNo")

        # 2. Scrape the status from PKStockX
        order_status = fetch_pkstockx_status(email, order_no)

        # 3. Create the Discord Payload
        payload = {
            "username": "PKStockX Tracker",
            "embeds": [
                {
                    "title": "📦 Order Tracking Report",
                    "description": f"Live status check for **{full_name}**",
                    "color": 3066993, # Greenish color
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
            response = requests.post(WEBHOOK_URL, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Discord Error: {e}")
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)