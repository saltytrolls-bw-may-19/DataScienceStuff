""" Moving data from  commentor_data.CSV to sqlite3.db"""
# import psycopg2
import pandas as pd
from sqlalchemy import create_engine
import sqlite3


def run_conversion(engine):
    # ___ load the CSV into a df ____
    csv_url = "commentor_data.csv"
    df = pd.read_csv(csv_url)

    #df.drop(columns=['salty_comments', 'sweet_comments'], inplace=True)
    print(df.head())

    # _____ Convert to SQL DB______
    df.to_sql('commentor_data',
              if_exists='replace',
              con=engine,
              chunksize=10)
    return


def main():
    eng_str = 'sqlite:///commentor_data.db'
    engine = create_engine(eng_str)

    # ____ Port csv to sqlite ___
    run_conversion(engine)

    #  _______ verify output  _________
    query = """
    SELECT *
    FROM commentor_data
    LIMIT 10 ;
    """
    print('--- commentor_data table ---')
    for row in engine.execute(query).fetchall():
        print(row)

    # ___ end main ___________
    return

#  Launched from the command line
if __name__ == '__main__':
    main()
