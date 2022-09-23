import asyncio
import os
from typing import Any
from dotenv import load_dotenv
from src.db.db import Db
from binance.streams import BinanceSocketManager
from binance.client import AsyncClient
from src.types.trade_types import TradePairSymbolsLiteral, TradePairSymbols

load_dotenv()


class BinanceSocket:
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
