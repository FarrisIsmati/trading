from typing import Any
from src.db.db import Db
from src.live.binance_socket import BinanceSocket
from src.types.trade_types import TradePairSymbolsLiteral

class Ticker:
    def __init__(self, trade_socket):
        self.trade_socket = trade_socket
        self.db = Db('sqlite:///BTCUSDTstream.db')

    async def update_ticker_db(self) -> None:
        count = 0
        async with self.trade_socket as tscm:
            while True:
                msg = await tscm.recv()
                frame = await self.db.update_ticker_db('BTCUSDT', msg)
                print(frame)
                print(count)
                count += 1
