import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from typing import List, Dict, Any, Optional

# --- Konfigurasi & Konstanta ---
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": "false",
    "price_change_percentage": "24h,7d"
}

# --- Fungsi Helper ---
def format_large_number(num: float) -> str:
    """Meringkas angka besar menjadi format B (Miliar) atau T (Triliun)."""
    if num >= 1_000_000_000_000:
        return f"${num / 1_000_000_000_000:.2f}T"
    if num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    if num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    return f"${num:,.0f}"

# --- Fungsi Logika ---
def fetch_data(session: requests.Session, console: Console) -> Optional[List[Dict[str, Any]]]:
    """Mengambil data koin dari API CoinGecko."""
    console.print("📊 [bold yellow]Mengambil data dari CoinGecko...[/bold yellow]")
    try:
        response = session.get(API_URL, params=PARAMS)
        response.raise_for_status()
        data = response.json()
        if not data:
            console.print("[bold red]API tidak mengembalikan data.[/bold red]")
            return None
        return data
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Gagal terhubung ke API: {e}[/bold red]")
        return None

def create_coin_panel_mobile(coin: Dict[str, Any]) -> Panel:
    """
    Membuat panel Rich yang dioptimalkan untuk layar sempit (mobile).
    Menggunakan Table untuk layout dua kolom yang rapi.
    """
    # Ekstraksi data
    rank = coin.get('market_cap_rank', 'N/A')
    symbol = coin.get('symbol', 'N/A').upper()
    name = coin.get('name', 'Unknown')
    price = coin.get('current_price', 0)
    pct_24h = coin.get('price_change_percentage_24h_in_currency', 0.0)
    pct_7d = coin.get('price_change_percentage_7d_in_currency', 0.0)
    market_cap = coin.get('market_cap', 0)
    volume = coin.get('total_volume', 0)
    
    # Logika pewarnaan
    pct_24h_str = f"[green]{pct_24h:+.2f}%[/green]" if pct_24h >= 0 else f"[red]{pct_24h:+.2f}%[/red]"
    pct_7d_str = f"[green]{pct_7d:+.2f}%[/green]" if pct_7d >= 0 else f"[red]{pct_7d:+.2f}%[/red]"

    # Membuat Tabel di dalam Panel untuk perataan sempurna
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(justify="left", ratio=1)
    table.add_column(justify="right", ratio=2)

    # Menambahkan baris data ke tabel
    table.add_row("Price", f"[bold cyan]${price:,.4f}[/bold cyan]")
    table.add_row("24H %", pct_24h_str)
    table.add_row("7D %", pct_7d_str)
    # Menambahkan pemisah
    table.add_row("─" * 12, "─" * 24) 
    table.add_row("Market Cap", f"[bold]{format_large_number(market_cap)}[/bold]")
    table.add_row("Volume 24H", format_large_number(volume))

    title = f"#{rank} {symbol} ({name})"
    
    return Panel(
        table,
        title=f"[bold yellow]{title}[/bold yellow]",
        border_style="dim",
        width=44 # Membatasi lebar panel secara eksplisit
    )

def main():
    """Fungsi utama untuk menjalankan skrip."""
    console = Console()
    with requests.Session() as session:
        coins_data = fetch_data(session, console)
        
        if coins_data:
            console.print("\n[bold green]✅ 100 Koin Teratas (Mode Mobile)[/bold green]\n")
            for coin in coins_data:
                # Gunakan fungsi panel yang baru
                panel = create_coin_panel_mobile(coin)
                console.print(panel)

# --- Titik Masuk Eksekusi ---
if __name__ == "__main__":
    main()
