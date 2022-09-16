import asyncio
import os
from typing import Any
from dotenv import load_dotenv  # type: ignore
from trade_types import TradePairSymbolsLiteral, TradePairSymbols
from livefeed import Db, Binance
import pandas as pd
from pandas import DataFrame
from BinanceTypes import BinanceOrder

load_dotenv()

class Strategy1:
    def __init__(
        self, 
        bnc: Binance, 
        db: Db, 
        symbol: TradePairSymbolsLiteral, 
) -> None:
        self.bnc = bnc
        self.engine = db.engine
        self.symbol = symbol
       

    async def __buy(
        self, 
        symbol: TradePairSymbolsLiteral, 
        qty: float
    ):
        # Add logging logic
        return await self.bnc.client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=qty
        )

    async def __sell(
        self, 
        symbol: TradePairSymbolsLiteral, 
        qty: float
    ):
        # Add logging logic
        return await self.bnc.client.create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=qty
        )

    async def __open_position(
        self, 
        cumret: Any, 
        entry: float,
        qty: float,
        log_counter: int = -1, 
        log_period: int = 200
    ):
        # Go in if value starts to move up
        if log_counter > -1 and log_counter % log_period:
            print(
                round((cumret[cumret.last_valid_index()] / entry) * 100, 2),  # type: ignore
                f'% - {entry} % increase')

        if cumret[cumret.last_valid_index()] > entry:
            # Buy some with USDT
            order:BinanceOrder = await self.__buy(TradePairSymbols.BTCUSDT.value, qty)
            print(order)
            return order

        return None

    async def __close_position(
        self,
        order: BinanceOrder,
        df: DataFrame,
        qty: float,
        lookback_pd: Any,
        sell_high_pct: float,
        sell_low_pct: float,
        log_counter: int = -1, 
        log_period: int = 200
    ):
        # Only look at data in db where entries
        # are after the purchase we made
        sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit='ms')]
        position_price = float(order['fills'][0]['price'])
        # Wait till we have entries
        if len(sincebuy) > 1:
            # Get latest percent change since the last purchase
            sincebuyret = ((sincebuy.Price.pct_change() + 1).cumprod()) - 1
            last_entry = sincebuyret[sincebuyret.last_valid_index()]

            if log_counter > -1 and log_counter % log_period:
                print(round((df.iloc[lookback_pd.last_valid_index()].Price / position_price) * 100, 2),  # type: ignore
                        '% - ', position_price, '->', df.iloc[lookback_pd.last_valid_index()].Price,# type: ignore
                        f'Looking to sell with {sell_high_pct}% or -{sell_low_pct}%, -> {last_entry:.10f}')

            # If latest entry is greater than x percent or negative sell
            if last_entry > sell_high_pct or last_entry < (-1 * sell_low_pct):
                order = await self.__sell(TradePairSymbols.BTCUSDT.value, qty)
                print(order)
                return order

    async def trade(
            self,
            lookback: int,
            entry: float,
            qty: float,
            sell_high_pct: float,
            sell_low_pct: float,
            log_period: int = 200
    ):
        """
        Buy X quantity of crypto when price moves up X percentage within a 
        lookback period. Sell the opened position when price moves up or 
        down X or Y percentage of the opened position.

        :param float entry: The percentage swing up in a lookback period that you are willing to buy on
        :param int lookback: The period of time in which to check for percentage upward swings
        :param float qty: The amount to purchase/sell
        :param float sell_high_pct: The percentage upwards you are willing to sell your opened position
        :param float sell_low_pct: The percentage downwards you are willing to sell your opened position
        :param bool log_period: Arbitrary amount of time between each log
        :return: void
        """
        open_position = False
        buy_order: Any = None
        log_counter = 0
        while True:
            df = pd.read_sql(self.symbol, self.engine)  # type: ignore
            # Look back a the last x number of data entries

            lookback_pd = df.iloc[-lookback:]
            # Get the percentage change (from each prev entry)
            # of all lookback entries
            # Multiply them all cumulativley from start to end
            # Total percentage change from the given lookback period (not in
            # units of time)
            cumret: pd.Series = (lookback_pd.Price.pct_change() + 1).cumprod() - 1
            if not open_position:
                buy_order = await self.__open_position(
                    cumret=cumret, 
                    log_counter=log_counter,
                    entry=entry,
                    qty=qty
                )
                open_position = True if buy_order != None else False
            else:
                sell_order = await self.__close_position(
                    order=buy_order, 
                    df=df, 
                    log_counter=log_counter,
                    qty=qty,
                    lookback_pd=lookback_pd,
                    sell_high_pct=sell_high_pct,
                    sell_low_pct=sell_low_pct
                )
                open_position = False if sell_order != None else True
            log_counter += 1


async def main():
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True

    bnc = Binance(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    await bnc.connect(TradePairSymbols.BTCUSDT.value)

    db = Db('sqlite:///BTCUSDTstream.db')
    strategy1 = Strategy1(bnc=bnc, db=db, symbol=TradePairSymbols.BTCUSDT.value)

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
