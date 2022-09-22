from datetime import datetime
from typing import Any
from src.types.trade_types import TradePairSymbolsLiteral, TradePairSymbols, PositionsLiteral, Positions
from src.types.db_types import TradeOrder
from src.live.binance_socket import BinanceSocket
import pandas as pd
from src.db.db import Db
from pandas import DataFrame
from src.types.binance_types import BinanceOrder

class Strategy1:
    def __init__(
        self, 
        bnc: BinanceSocket, 
        db: Db,
        symbol: TradePairSymbolsLiteral, 
        broker_fee: float = 0.1,
) -> None:
        self.bnc = bnc
        self.engine = db.engine
        self.symbol = symbol
        self.broker_fee = broker_fee
        self.spacer = '      '
        self.trades_db = Db('sqlite:///trades.db')

    def __print_position_open(
        self,
        cumret: Any,
        entry: float
    ):
        pct_to_buy: float = (cumret[cumret.last_valid_index()] / entry) * 100
        pct_to_buy_rounded = round(pct_to_buy, 2)
        print(f'{Positions.BUY.value}: {self.symbol} {self.spacer} ENTRY: +{entry}% {self.spacer} ENTRY+FEES: +{entry}% {self.spacer} ROC: {pct_to_buy_rounded}%')

    def __print_position_close(
        self,
        last_entry: float,
        sell_high_pct: float,
        sell_low_pct: float,
    ):
        pct_change = round(last_entry, 4)
        print(f'{Positions.SELL.value}: {self.symbol} {self.spacer} SELL UP: +{sell_high_pct}% {self.spacer} SELL DOWN: -{sell_low_pct}% {self.spacer} CHANGE: {pct_change}')

    def __print_order(self, order: BinanceOrder):
        print('')
        print(f"TRANSACTION: {order['side']} {self.spacer} PRICE: {order['fills'][0]['price']} {self.spacer} QTY: {order['fills'][0]['qty']} {self.spacer} ORDER ID: {order['orderId']}")
        print('')

    def __calc_slippage(self):
            return 0

    def __fees(
        self,
        entry: float
    ):
        return entry + self.broker_fee + self.__calc_slippage()


    async def __buy(
        self, 
        symbol: TradePairSymbolsLiteral, 
        qty: float
    ):
        # Add logging logic
        order = await self.bnc.client.create_order(
            symbol=symbol,
            side='BUY',
            type='MARKET',
            quantity=qty
        )

        trade: TradeOrder = {
            'SessionId': '1', 
            'Symbol': TradePairSymbols.BTCUSDT.value,
            'Position': Positions.BUY.value, 
            'TradingPrice': order['fills'][0]['price'], 
            'Quantity': order['fills'][0]['qty'],
            'Spent':float(order['fills'][0]['qty']) * float(order['fills'][0]['price']), 
            'Earned': 0,
            'Time': datetime.now()
        }
        self.trades_db.update_position_db(name='trades1', order=trade)

        return order 

    async def __sell(
        self, 
        symbol: TradePairSymbolsLiteral, 
        qty: float
    ):
        # Add logging logic
        order = await self.bnc.client.create_order(
            symbol=symbol,
            side='SELL',
            type='MARKET',
            quantity=qty
        )

        trade: TradeOrder = {
            'SessionId': '1', 
            'Symbol': TradePairSymbols.BTCUSDT.value, 
            'Position': Positions.SELL.value, 
            'TradingPrice': order['fills'][0]['price'],
            'Quantity': order['fills'][0]['qty'],
            'Spent': 0,
            'Earned': float(order['fills'][0]['qty']) * float(order['fills'][0]['price']),
            'Time': datetime.now()
        }
        self.trades_db.update_position_db(name='trades1', order=trade)

        return order

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
            self.__print_position_open(
                cumret = cumret,
                entry = entry
            )

        if cumret[cumret.last_valid_index()] > entry:
            # Buy some with USDT
            order:BinanceOrder = await self.__buy(TradePairSymbols.BTCUSDT.value, qty)
            self.__print_order(order)
            return order

        return None

    async def __close_position(
        self,
        order: BinanceOrder,
        df: DataFrame,
        qty: float,
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
            last_entry: float= sincebuyret[sincebuyret.last_valid_index()] #type: ignore

            if log_counter > -1 and log_counter % log_period:
                self.__print_position_close(
                    last_entry=last_entry,
                    sell_high_pct=sell_high_pct,
                    sell_low_pct=sell_low_pct
                )

            # If latest entry is greater than x percent or negative sell
            if last_entry > sell_high_pct or last_entry < (-1 * sell_low_pct):
                order = await self.__sell(TradePairSymbols.BTCUSDT.value, qty)
                self.__print_order(order)
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
                    sell_high_pct=sell_high_pct,
                    sell_low_pct=sell_low_pct
                )
                open_position = False if sell_order != None else True
            log_counter += 1

# 1.
# Tally up how much money I made or lost so far
# Track comission of binance and slippage
# Add to algorithim
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
