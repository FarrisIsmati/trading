from typing import Any
from src.db.db import Db

class Ticker:
    def __init__(self, trade_socket, db_name:str, table_name: str):
        self.trade_socket = trade_socket
        self.db = Db(db_name)
        self.table_name = table_name

    async def update_ticker_db(self) -> None:
        count = 0
        async with self.trade_socket as tscm:
            while True:
                msg = await tscm.recv()
                frame = await self.db.update_ticker_db(self.table_name, msg)
                print(frame)
                print(count)
                count += 1
