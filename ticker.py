import asyncio
import os
from typing import Any
from dotenv import load_dotenv  # type: ignore
from src.live.ticker import Ticker
from src.types.trade_types import TradePairSymbols
from src.live.binance_socket import BinanceSocket
from src.db.db import Db
from src.strategies.strategy_1 import Strategy1

load_dotenv()

async def main():
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True

    bnc = BinanceSocket(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    ts = await bnc.connect(TradePairSymbols.BTCUSDT.value)

    ticker = Ticker(ts)
    await ticker.update_ticker_db()
    
    await bnc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
