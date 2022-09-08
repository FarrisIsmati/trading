import asyncio
import os
from typing import Any
from dotenv import load_dotenv
from trade_types import TradePairSymbolsLiteral, TradePairSymbols
from livefeed import Db, Binance
import pandas as pd

load_dotenv()


class Trade:
    def __init__(self, bnc: Binance, db: Db) -> None:
        self.bnc = bnc
        self.engine = db.engine

    async def buy(self, symbol: TradePairSymbolsLiteral, qty: int):
        order = await self.bnc.client.create_order(
            symbol, side='SELL', type='MARKET', quantity=qty)
        print(order)

    async def strategy(self, symbol: TradePairSymbolsLiteral, entry: int,
                       lookback: int, qty: int, open_position: bool = False):
        print('begin strat')
        while True:
            # Full dataframe
            df = pd.read_sql(symbol, self.engine)
            # Look back a the last x number of data entries
            lookbackperiod = df.iloc[-lookback:]
            # Get the percentage change (from each prev entry)
            # of all lookback entries
            # Multiply them all cumulativley from start to end
            # Total percentage change from the given lookback period (not in
            # units of time)
            cumret = (lookbackperiod.Price.pct_change() + 1).cumprod() - 1
            if not open_position:
                # Go in if value starts to move up
                if cumret[cumret.last_valid_index()] > entry:
                    # Buy some with USDT
                    order = await self.bnc.client.create_order(symbol, side='BUY',
                                                               type='MARKET',
                                                               quantity=qty)
                    print(order)
                    open_position = True
                    break
        if open_position:
            while True:
                df = pd.read_sql(symbol, self.engine)
                # Only look at data in db where entries
                # are after the purchase we made
                sincebuy = df.loc[df.Time > pd.to_datetime(
                    order['transactTime'], unit='ms')]

                # Wait till we have entries
                if len(sincebuy) > 1:
                    # Get latest percent change since the last purchase
                    sincebuyret = (sincebuy.Price.pct_change() + 1).cumprod() - 1
                    last_entry = sincebuyret[sincebuyret.last_valid_index()]

                    # If latest entry is greater than x percent or negative sell
                    if last_entry > 0.0015 or last_entry < -0.0015:
                        order = await self.bnc.client.create_order(
                            symbol, side='SELL', type='MARKET', quantity=qty)
                        print(order)
                        break


async def main():
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True

    bnc = Binance(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    db = Db('sqlite:///BTCUSDTstream.db')
    trade = Trade(bnc, db)

    await trade.buy(TradePairSymbols.BTCUSDT.value, 0.0001)
    # trade.strategy(TradePairSymbols.BTCUSDT.value, 0.001, 20, 0.001)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
