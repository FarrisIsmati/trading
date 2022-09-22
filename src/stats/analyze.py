from src.db.db import Db
import pandas as pd
from time import sleep
from types.trade_types import Positions

def analyze():
    while True:
        db = Db('sqlite:///trades.db')
        df = pd.read_sql('trades1', db.engine)  # type: ignore

        total:float = 0 # type: ignore
        df = df.loc[1:df.last_valid_index()]
        for index, row in df.iterrows():
            if row.Position == Positions.BUY.value:
                total -= row.Spent
            if row.Position == Positions.SELL.value:
                total += row.Earned
        
        print(f'Earnings = $ {round(total, 6)}')
        sleep(3)

