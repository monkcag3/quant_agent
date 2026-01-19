
import pandas as pd


if __name__ == '__main__':
    df = pd.read_csv("600000.csv")
    df['date'] = pd.to_datetime(df['time'], format="%Y%m%d%H%M%S%f")
    df = df.drop(['time'], axis=1)
    df.rename(columns={'date': 'datetime'}, inplace=True)
    print(df)
    df.to_csv("600000.u.csv")