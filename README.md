# Python ETC Miner

A Python-based Ethereum Classic (ETC) mining tool. This tool connects to a mining pool using the Stratum protocol and simulates mining using multi-threading.

![6181300397235357464](https://github.com/user-attachments/assets/659b9681-8e56-41e1-ad8c-70f3bb764fc3)

---

## Features
- **Multi-threaded mining**: Utilizes multiple CPU cores.
- **Stratum protocol support**: Connects to mining pools.
- **Real-time statistics**: Displays hashrate, shares submitted, and elapsed time using `rich`.
- **Configurable settings**: Easily configure wallet address, worker name, and pool settings.

---

## Requirements
- Python 3.7+
- `rich` (for the terminal UI)
- `pyfiglet` (for the banner)

---

## Installation

1. Clone the repository:
   -cd etc miner python
   -sudo python3 -m venv venv
   -sudo source venv/bin/activate  # On Windows: venv\Scripts\activate
   -sudo pip3 install -r requirements.txt
   -python3 cerberus_etc_miner.py
