from typing import Any
import pandas as pd
import sqlalchemy
from pandas import DataFrame
from datetime import datetime
from src.types.trade_types import Positions, TradePairSymbols, TradePairSymbolsLiteral
from binance.streams import BinanceSocketManager
from binance.client import AsyncClient
from src.types.trade_types import TradePairSymbolsLiteral, TradePairSymbols
from src.types.db_types import TradeOrder

class Db:
    def __init__(self, file_name: str) -> None:
        self.engine = sqlalchemy.create_engine(file_name, echo=False)

    def __create_position_df(self, order: TradeOrder):
        df = pd.DataFrame(data=order, index=[0])
        df.SessionId = df.SessionId.astype(str)
        df.Symbol = df.Symbol.astype(str)
        df.Position = df.Position.astype(str)
        df.Quantity = df.Quantity.astype(float)
        df.TradingPrice = df.TradingPrice.astype(float)
        df.Spent = df.Spent.astype(float)
        df.Comission = df.Comission.astype(float)
        df.Earned = df.Earned.astype(float)
        df.Change = df.Change.astype(float)
        df.Time = pd.to_datetime(df.Time, unit='ms')
        return df

    def update_position_db(self, name: str, order: TradeOrder) -> None:
        frame = self.__create_position_df(order=order)
        frame.to_sql(name, con=self.engine, if_exists='append', index=False)  # type: ignore

    def __create_ticker_df(self, msg: Any):
        df = pd.DataFrame([msg])
        df = df.loc[:, ['s', 'E', 'p']]
        df.columns = ['symbol', 'Time', 'Price']
        df.Price = df.Price.astype(float)
        df.Time = pd.to_datetime(df.Time, unit='ms')
        return df

    async def update_ticker_db(self, table: str, msg: Any) -> DataFrame:
        frame = self.__create_ticker_df(msg)
        frame.to_sql(table, con=self.engine, if_exists='append', index=False)
        return frame

