import asyncio
import os
from typing import Any
from dotenv import load_dotenv
import pandas as pd
import sqlalchemy
from binance.streams import BinanceSocketManager
from binance.client import AsyncClient
from trade_types import TradePairSymbolsLiteral, TradePairSymbols

load_dotenv()


class Binance:
    def __init__(self, API_KEY: str, SECRET_KEY: str, testnet: bool) -> None:
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.testnet = testnet
        self.trade_socket: Any = None
        self.client: Any = None

    async def connect(self, symbol: TradePairSymbolsLiteral) -> Any:
        self.client = await AsyncClient.create(self.API_KEY, self.SECRET_KEY,
                                               tld='us', testnet=self.testnet)
        bm = BinanceSocketManager(self.client)
        trade_socket: Any = bm.trade_socket(symbol)
        return trade_socket

    async def close(self) -> None:
        await self.client.close_connection()


class Db:
    def __init__(self, file_name: str) -> None:
        self.engine = sqlalchemy.create_engine(file_name, echo=False)

    def create_df(self, msg: Any):
        df = pd.DataFrame([msg])
        df = df.loc[:, ['s', 'E', 'p']]
        df.columns = ['symbol', 'Time', 'Price']
        df.Price = df.Price.astype(float)
        df.Time = pd.to_datetime(df.Time, unit='ms')
        return df

    async def update_db(self, trade_socket: Any,  symbol:
                        TradePairSymbolsLiteral) -> None:
        count = 0
        async with trade_socket as tscm:
            while True:
                msg = await tscm.recv()
                frame = self.create_df(msg)
                frame.to_sql(symbol, con=self.engine, if_exists='append', index=False)
                print(frame)
                print(count)
                count += 1


async def main():
    BINANCE_API_KEY = os.environ['BINANCE_API_KEY_DEV']
    BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY_DEV']
    is_testnet = True

    bnc = Binance(BINANCE_API_KEY, BINANCE_SECRET_KEY, is_testnet)
    db = Db('sqlite:///BTCUSDTstream.db')

    ts = await bnc.connect(TradePairSymbols.BTCUSDT.value)

    await db.update_db(ts, TradePairSymbols.BTCUSDT.value)

    await bnc.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
#
