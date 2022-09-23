from src.db.db import Db
import pandas as pd
from time import sleep
from src.types.trade_types import Positions

def analyze():
    db = Db('sqlite:///db/trades.db')
    df = pd.read_sql('trades1', db.engine)  # type: ignore

    while True:
        db = Db('sqlite:///db/trades.db')
        df = pd.read_sql('trades1', db.engine)  # type: ignore

        total:float = 0 # type: ignore
        df = df.loc[0:df.last_valid_index()]
        for index, row in df.iterrows():
            if row.Position == Positions.BUY.value:
                total -= row.Spent
            if row.Position == Positions.SELL.value:
                total += row.Earned
        
        print(df)
        print(f'Earnings = $ {round(total, 6)}')
        print('')
        sleep(5)


    # last_row = df.loc[df.last_valid_index()]
    # print(df)
    # print('last trade', float(last_row.Spent) if int(last_row.Spent) != 0 else float(last_row.Earned))