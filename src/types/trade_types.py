from enum import Enum
from typing import Literal


class TradePairSymbols(Enum):
    BTCUSDT = 'BTCUSDT'

class Positions(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class Sell(Enum):
    WIN = 'WIN'
    LOSS = 'LOSS'

TradePairSymbolsLiteral = Literal['BTCUSDT']
PositionsLiteral = Literal['BUY', 'SELL']
SellLiteral = Literal['WIN', 'LOSS']