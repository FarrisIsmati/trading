# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
import asyncio
import os
from typing import Any
from dotenv import load_dotenv  # type: ignore
from trade_types import TradePairSymbolsLiteral, TradePairSymbols
from livefeed import Db, Binance
import pandas as pd

load_dotenv()


class Trade:
    def __init__(self, bnc: Binance, db: Db) -> None:
        self.bnc = bnc
        self.engine = db.engine

    async def buy(self, symbol: TradePairSymbolsLiteral, qty: float):
        # Add logging logic
        return await self.bnc.client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=qty
        )

    async def sell(self, symbol: TradePairSymbolsLiteral, qty: float):
        # Add logging logic
        return await self.bnc.client.create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=qty
        )

    async def binance_fee(self, price: float, fee: float = .1):

    async def strategy_1(
            self,
            symbol: TradePairSymbolsLiteral,
            entry: float,
            lookback: int,
            qty: float,
            sell_high_pct: float,
            sell_low_pct: float,
            log_period: int = 200
    ):
        """
        Buy X quantity of crypto when price moves up X percentage within a 
        lookback period. Sell the opened position when price moves up or 
        down X or Y percentage of the opened position.

        :param TradePairSymbolsLiteral symbol: The trading pair you want to execute on
        :param float entry: The percentage swing up in a lookback period that you are willing to buy on
        :param int lookback: The period of time in which to check for percentage upward swings
        :param float qty: The amount to purchase/sell
        :param float sell_high_pct: The percentage upwards you are willing to sell your opened position
        :param float sell_low_pct: The percentage downwards you are willing to sell your opened position
        :param bool log_period: Arbitrary amount of time between each log
        :return: void
        """
        open_position = False
        order: Any = None
        count = 0
        while True:
            df = pd.read_sql(symbol, self.engine)
            # Look back a the last x number of data entries

            lookback_pd = df.iloc[-lookback:]
            # Get the percentage change (from each prev entry)
            # of all lookback entries
            # Multiply them all cumulativley from start to end
            # Total percentage change from the given lookback period (not in
            # units of time)
            cumret = (lookback_pd.Price.pct_change() + 1).cumprod() - 1
            if not open_position:
                # Go in if value starts to move up
                if count % log_period:
                    print(
                        round((cumret[cumret.last_valid_index()] / entry) * 100, 2),
                        f'% - {entry} % increase')

                if cumret[cumret.last_valid_index()] > entry:
                    # Buy some with USDT
                    order = await self.buy(TradePairSymbols.BTCUSDT.value, qty)
                    print(order)
                    open_position = True
            if open_position:
                # Only look at data in db where entries
                # are after the purchase we made
                sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit='ms')]
                position_price = float(order['fills'][0]['price'])
                # Wait till we have entries
                if len(sincebuy) > 1:
                    # Get latest percent change since the last purchase
                    sincebuyret = ((sincebuy.Price.pct_change() + 1).cumprod()) - 1
                    last_entry = sincebuyret[sincebuyret.last_valid_index()]

                    if count % log_period:
                        print(round((df.iloc[lookback_pd.last_valid_index()].Price / position_price) * 100, 2),
                              '% - ', position_price, '->', df.iloc[lookback_pd.last_valid_index()].Price,
                              f'Looking to sell with {sell_high_pct}% or -{sell_low_pct}%, -> {last_entry:.10f}')

                    # If latest entry is greater than x percent or negative sell
                    if last_entry > sell_high_pct or last_entry < (-1 * sell_low_pct):
                        order = await self.sell(TradePairSymbols.BTCUSDT.value, qty)
                        print(order)
                        open_position = False
            count += 1


async def main():
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True

    bnc = Binance(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    await bnc.connect(TradePairSymbols.BTCUSDT.value)

    db = Db('sqlite:///BTCUSDTstream.db')
    trade = Trade(bnc, db)

    await trade.strategy_1(
        symbol=TradePairSymbols.BTCUSDT.value,
        entry=0.0001,
        lookback=50,
        qty=0.001,
        sell_high_pct=0.00015,
        sell_low_pct=0.00015
    )
    await bnc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# 1.
# Inputs to put in, if I invested X money at X price how much percentage increase I need to make +$1 per trade

# By default also include binance fee .1 of each trade (buy & sell)
# Include option to include .075 with BNB trades
# Set options to make percentage increase and decrease per trade easy
# 2.
# Send all trade data to DB
# Create reporting metrics out of this
# Run multiple options compare them via reporting metrics at similar intervals
# 3.
# Study multiple algos for trading
# Create tax reporting
#
# pt ...
# Future categorize market conditions per bot
# Create rumor/news bot to buy/sell
# Start with $3,000
# Work up to $10,000
# Eventually bot handles $25,000 goal
