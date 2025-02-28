import hashlib
import socket
import json
import time
import threading
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from pyfiglet import Figlet

# Constants
POOL_HOST = "etc-eu1.nanopool.org"  # Replace with your preferred Nanopool server
POOL_PORT = 10100  # Stratum port (non-SSL)
WALLET_ADDRESS = "0xdc3963e4b45010df24675d979357bff67f9e8bb3"  # Replace with your ETC wallet address
WORKER_NAME = "cerberus_miner"
PASSWORD = "x"  # Default password for Nanopool

# Mining statistics
@dataclass
class MiningStats:
    hashes_computed: int = 0
    shares_submitted: int = 0
    hashrate: float = 0.0
    start_time: float = time.time()
    lock: threading.Lock = threading.Lock()  # Thread-safe lock

# Banner
def display_banner():
    figlet = Figlet(font="slant")
    banner = figlet.renderText("Cerberus ETC Miner")
    console.print(Panel(Text(banner, style="bold blue")))
    console.print(f"[bold green]Programmer: Sudeepa Wanigarathna[/bold green]\n")

# Stratum protocol communication
def stratum_communication(stats: MiningStats):
    try:
        # Connect to the pool
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((POOL_HOST, POOL_PORT))

        # Subscribe to the pool
        subscribe_msg = {
            "id": 1,
            "method": "mining.subscribe",
            "params": []
        }
        sock.sendall((json.dumps(subscribe_msg) + "\n").encode())

        # Authorize worker
        auth_msg = {
            "id": 2,
            "method": "mining.authorize",
            "params": [f"{WALLET_ADDRESS}.{WORKER_NAME}", PASSWORD]
        }
        sock.sendall((json.dumps(auth_msg) + "\n").encode())

        # Read responses
        while True:
            response = sock.recv(1024).decode().strip()
            if not response:
                break

            try:
                json_response = json.loads(response)
                if json_response.get("method") == "mining.notify":
                    # Handle new work from the pool
                    job_id = json_response["params"][0]
                    seed_hash = json_response["params"][1]
                    target = json_response["params"][2]

                    # Mine with Ethash algorithm
                    nonce = mine(seed_hash, target, stats)

                    # Submit share
                    submit_msg = {
                        "id": 3,
                        "method": "mining.submit",
                        "params": [f"{WALLET_ADDRESS}.{WORKER_NAME}", job_id, f"{nonce:08x}", "header", "mix_hash"]
                    }
                    sock.sendall((json.dumps(submit_msg) + "\n").encode())

                    # Update shares submitted
                    with stats.lock:
                        stats.shares_submitted += 1
            except json.JSONDecodeError:
                console.print(f"[bold red]Invalid JSON response: {response}[/bold red]")
            except KeyError as e:
                console.print(f"[bold red]Missing key in JSON response: {e}[/bold red]")

    except Exception as e:
        console.print(f"[bold red]Stratum error: {e}[/bold red]")
    finally:
        sock.close()

# Ethash mining function (simplified)
def mine(seed_hash: str, target: str, stats: MiningStats) -> int:
    nonce = 0
    target_int = int(target, 16)

    while True:
        # Generate the hash using Keccak-256 (Ethash uses Keccak-256, not SHA-256)
        data = f"{seed_hash}{nonce:08x}".encode()
        keccak_hash = hashlib.sha3_256(data).hexdigest()
        hash_int = int(keccak_hash, 16)

        # Update hashes computed
        with stats.lock:
            stats.hashes_computed += 1

        # Check if the hash meets the target
        if hash_int < target_int:
            return nonce

        nonce += 1

# Display mining statistics
def display_stats(stats: MiningStats):
    with Live(console=console, refresh_per_second=4) as live:
        while True:
            elapsed_time = time.time() - stats.start_time
            with stats.lock:
                hashrate = stats.hashes_computed / elapsed_time if elapsed_time > 0 else 0

            # Create a table for statistics
            table = Table(title="Mining Statistics", show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan", justify="right")
            table.add_column("Value", style="green")

            table.add_row("Hashrate", f"{hashrate:.2f} H/s")
            table.add_row("Hashes Computed", f"{stats.hashes_computed}")
            table.add_row("Shares Submitted", f"{stats.shares_submitted}")
            table.add_row("Elapsed Time", f"{elapsed_time:.2f} seconds")

            live.update(table)
            time.sleep(1)

# Main function
def main():
    stats = MiningStats()

    # Display banner
    display_banner()

    # Start Stratum communication thread
    stratum_thread = threading.Thread(target=stratum_communication, args=(stats,))
    stratum_thread.daemon = True
    stratum_thread.start()

    # Start statistics display
    try:
        display_stats(stats)
    except KeyboardInterrupt:
        console.print("[bold yellow]Shutting down miner...[/bold yellow]")

# Rich console for advanced UI
console = Console()

if __name__ == "__main__":
    main()
