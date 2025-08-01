# -*- coding: utf-8 -*-
import requests
import os
import time
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

# Simbol & emoji
XMR_SYMBOL = "ɱ"         # Monero dengan M berekor
PANEL_EMOJI = "📊"       # Untuk panel harga
SWAP_EMOJI = "🔁"        # Untuk panel konversi
ARROW = "→"
APPROX = "≈"

# Cache exchange rates
cached_rates = {
    'xmr_idr': None,
    'xmr_usd': None,
    'usd_idr': None,
    'last_fetch_time': 0
}
CACHE_DURATION = 60

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_exchange_rates():
    global cached_rates
    current_time = time.time()

    # Pakai cache kalau masih segar
    if current_time - cached_rates['last_fetch_time'] < CACHE_DURATION:
        if all([cached_rates['xmr_idr'], cached_rates['xmr_usd'], cached_rates['usd_idr']]):
            console.print("[dim]📦 Menggunakan data dari cache (masih segar).[/dim]")
            time.sleep(0.5)
            return cached_rates['xmr_idr'], cached_rates['xmr_usd'], cached_rates['usd_idr']

    console.print("[dim]🔄 Mengambil harga terkini dari CoinGecko...[/dim]", end="\r")

    try:
        xmr_data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd,idr"
        ).json().get('monero', {})

        tether_data = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=idr"
        ).json().get('tether', {})

        xmr_usd = xmr_data.get('usd')
        xmr_idr = xmr_data.get('idr')
        usd_idr = tether_data.get('idr')

        if (usd_idr is None or usd_idr == 0) and xmr_usd and xmr_idr:
            usd_idr = xmr_idr / xmr_usd
            console.print("[yellow]🔃 Menggunakan kurs XMR sebagai proxy untuk USD→IDR[/yellow]")
            time.sleep(1)

        if xmr_idr and xmr_usd and usd_idr:
            cached_rates.update({
                'xmr_idr': xmr_idr,
                'xmr_usd': xmr_usd,
                'usd_idr': usd_idr,
                'last_fetch_time': current_time
            })
            console.print("[green]✅ Data harga berhasil diperbarui![/green]")
        else:
            console.print("[orange1]⚠️ Beberapa data harga tidak lengkap.[/orange1]")
            time.sleep(1)

    except Exception as e:
        console.print(f"[bold red]❌ Gagal ambil data: {e}[/bold red]")
        time.sleep(2)
        return None, None, None

    return xmr_idr, xmr_usd, usd_idr

def display_rates(xmr_idr, xmr_usd, usd_idr):
    rate_panel = Text()
    rate_panel.append(f"{XMR_SYMBOL} {ARROW} Rp : ")
    rate_panel.append(f"Rp {xmr_idr:,.0f}" if xmr_idr else "N/A", style="bold green")
    rate_panel.append(f"\n{XMR_SYMBOL} {ARROW} $  : ")
    rate_panel.append(f"$ {xmr_usd:,.2f}" if xmr_usd else "N/A", style="bold green")
    rate_panel.append(f"\n$  {ARROW} Rp : ")
    rate_panel.append(f"Rp {usd_idr:,.0f}" if usd_idr else "N/A", style="bold green")

    console.print(Panel(rate_panel, title=f"{PANEL_EMOJI} [bold blue]Harga Terkini[/bold blue]", border_style="dim"))

def display_menu():
    menu = Text()
    menu.append(f"1. {XMR_SYMBOL} {ARROW} Rp", style="cyan")
    menu.append(f"\n2. Rp {ARROW} {XMR_SYMBOL}", style="cyan")
    menu.append(f"\n3. {XMR_SYMBOL} {ARROW} $", style="cyan")
    menu.append(f"\n4. $  {ARROW} {XMR_SYMBOL}", style="cyan")
    menu.append(f"\n5. $  {ARROW} Rp", style="cyan")
    menu.append(f"\n6. Rp {ARROW} $", style="cyan")
    menu.append("\nq. Keluar", style="red")

    console.print(Panel(menu, title=f"{SWAP_EMOJI} [bold yellow]Pilih Konversi[/bold yellow]", border_style="dim"))

def get_amount_input(symbol):
    while True:
        try:
            amount_str = Prompt.ask(f"[bold white]Jumlah {symbol}[/bold white]", default="1")
            amount = float(amount_str)
            if amount <= 0:
                console.print("[bold red]⛔ Jumlah harus lebih besar dari nol, bro.[/bold red]")
                continue
            return amount
        except ValueError:
            console.print("[bold red]⚠️ Input tidak valid. Masukkan angka ya.[/bold red]")

def perform_conversion(choice, rates):
    xmr_idr, xmr_usd, usd_idr = rates

    if None in rates:
        console.print("[bold red]❌ Data harga belum lengkap. Konversi gagal.[/bold red]")
        console.input("[yellow]Tekan Enter untuk lanjut...[/yellow]")
        return

    amount = 0
    result_text = ""

    if choice == '1':
        amount = get_amount_input(XMR_SYMBOL)
        result_text = f"{XMR_SYMBOL} {amount:,.5f} {APPROX} Rp {amount * xmr_idr:,.0f}"
    elif choice == '2':
        amount = get_amount_input("Rp")
        result_text = f"Rp {amount:,.0f} {APPROX} {XMR_SYMBOL} {amount / xmr_idr:,.5f}"
    elif choice == '3':
        amount = get_amount_input(XMR_SYMBOL)
        result_text = f"{XMR_SYMBOL} {amount:,.5f} {APPROX} $ {amount * xmr_usd:,.2f}"
    elif choice == '4':
        amount = get_amount_input("$")
        result_text = f"$ {amount:,.2f} {APPROX} {XMR_SYMBOL} {amount / xmr_usd:,.5f}"
    elif choice == '5':
        amount = get_amount_input("$")
        result_text = f"$ {amount:,.2f} {APPROX} Rp {amount * usd_idr:,.0f}"
    elif choice == '6':
        amount = get_amount_input("Rp")
        result_text = f"Rp {amount:,.0f} {APPROX} $ {amount / usd_idr:,.2f}"
    else:
        console.print("[bold red]❌ Pilihan tidak valid.[/bold red]")
        console.input("[yellow]Tekan Enter untuk lanjut...[/yellow]")
        return

    console.print(f"\n[bold green]{result_text}[/bold green]")
    console.input("[yellow]Tekan Enter untuk lanjut...[/yellow]")

def main():
    while True:
        clear_screen()
        rates = get_exchange_rates()
        display_rates(*rates)
        display_menu()

        choice = Prompt.ask("[bold white]Pilihan[/bold white]").lower().strip()

        if choice == 'q':
            console.print("[bold yellow]👋 Terima kasih sudah pakai MoneroKonversi™![/bold yellow]")
            break
        elif choice in ['1', '2', '3', '4', '5', '6']:
            perform_conversion(choice, rates)
        else:
            console.print("[bold red]❌ Pilihan tidak valid, bro.[/bold red]")
            console.input("[yellow]Tekan Enter untuk lanjut...[/yellow]")

if __name__ == "__main__":
    main()
