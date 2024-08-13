import requests
from decimal import Decimal, ROUND_HALF_UP

# Ganti dengan API key Anda
API_KEY = '2cd28305-f39d-4f18-8a9b-670b9a946f58'
BASE_URL = 'https://pro-api.coinmarketcap.com/v1/'

def get_cryptocurrency_listings(limit=100):
    url = f'{BASE_URL}cryptocurrency/listings/latest'
    params = {
        'start': '1',
        'limit': str(limit),  # Ambil 100 koin teratas
        'convert': 'USD'
    }
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return data

def format_number(value):
    try:
        number = Decimal(value)
        if number >= 1:
            # Untuk harga >= $1, tampilkan dengan 2 desimal
            formatted_number = number.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            # Untuk harga < $1, tampilkan dengan presisi yang diperlukan
            formatted_number = number.normalize()
            if formatted_number == Decimal('0'):
                return "$0.00"
            return f"${formatted_number:,.8f}".rstrip('0').rstrip('.')
        
        if formatted_number == formatted_number.to_integral_value():
            return f"${formatted_number.to_integral_value():,}"
        else:
            return f"${formatted_number:,.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_percentage(value):
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return "N/A"

def print_cryptocurrency_listings(listings):
    print("\n..................................................\nTop 100 Marketcap Cryptocurrency By CMC:\n")
    coins = listings.get('data', [])
    
    # Initialize variables to find gainer and loser
    max_gain = -float('inf')
    max_loss = float('inf')
    gainer = None
    loser = None

    for idx, crypto in enumerate(coins, start=1):
        symbol = crypto.get('symbol', 'N/A')
        price = crypto.get('quote', {}).get('USD', {}).get('price', 'N/A')
        percent_change_24h = crypto.get('quote', {}).get('USD', {}).get('percent_change_24h', 'N/A')
        formatted_price = format_number(price)
        formatted_percent_change = format_percentage(percent_change_24h)
        
        # Print each cryptocurrency
        print(f"{idx}. {symbol} ==> {formatted_price} ==> {formatted_percent_change}")
        
        # Update gainer and loser
        try:
            percent_change_value = float(percent_change_24h)
            if percent_change_value > max_gain:
                max_gain = percent_change_value
                gainer = (symbol, formatted_price, formatted_percent_change)
            if percent_change_value < max_loss:
                max_loss = percent_change_value
                loser = (symbol, formatted_price, formatted_percent_change)
        except ValueError:
            continue

    print()
    # Print the gainer and loser
    if gainer:
        print(f"Gainer (Highest Increase):\n {gainer[0]} ==> {gainer[1]} ==> {gainer[2]}")
    if loser:
        print(f"\nLoser (Highest Decrease):\n {loser[0]} ==> {loser[1]} ==> {loser[2]}")

def main():
    # Mengambil data koin teratas
    listings = get_cryptocurrency_listings()
    print_cryptocurrency_listings(listings)

if __name__ == "__main__":
    main()