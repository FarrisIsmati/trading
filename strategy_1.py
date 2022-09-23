import asyncio
import os
from dotenv import load_dotenv  # type: ignore
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
    await bnc.connect(TradePairSymbols.BTCUSDT.value)

    strategy1 = Strategy1(
        bnc=bnc, 
        feed_db_name='sqlite:///db/BTCUSDTstream.db',
        feed_table_name='BTCUSDT',
        trades_db_name='sqlite:///db/trades.db',
        trades_table_name='trades1',
        symbol=TradePairSymbols.BTCUSDT.value
    )

    await strategy1.trade(
        lookback=50,
        entry=0.0001,
        qty=0.0009,
        sell_high_pct=0.00015,
        sell_low_pct=0.00015
    )
    await bnc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
