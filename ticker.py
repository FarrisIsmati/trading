import asyncio
import os
from dotenv import load_dotenv  # type: ignore
from src.live.ticker import Ticker
from src.types.trade_types import TradePairSymbols
from src.live.binance import Binance
from src.db.db import Db
from src.strategies.strategy_1 import Strategy1

load_dotenv()

async def main():
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True

    bnc = Binance(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    await bnc.connect()
    ts = await bnc.create_socket(TradePairSymbols.BTCUSDT.value)

    ticker = Ticker(ts, 'sqlite:///db/BTCUSDTstream.db', table_name='BTCUSDT')
    await ticker.update_ticker_db()
    
    await bnc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
