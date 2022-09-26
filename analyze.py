import asyncio
from src.stats.analyze import analyze
import asyncio
import os
from dotenv import load_dotenv  # type: ignore
from src.types.trade_types import TradePairSymbols
from src.live.binance import Binance

load_dotenv()

async def main():
    # analyze()
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True
    bnc = Binance(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    await bnc.connect()
    account = await bnc.client.get_account()
    print(account)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())