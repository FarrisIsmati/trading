from datetime import datetime
from typing import TypedDict
from src.types.trade_types import PositionsLiteral, TradePairSymbolsLiteral


class TradeOrder(TypedDict):
    SessionId: str
    Symbol: TradePairSymbolsLiteral
    Position: PositionsLiteral
    Quantity: float
    TradingPrice: float
    Spent: float
    Earned: float
    Change: float
    Time: datetime
