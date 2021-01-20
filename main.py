import os
import quandl
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

URL = "FSE/BDT_X"
quandl.ApiConfig.api_key = "zLDQk482zDNum9Gyoiyz"
CUR_DATE = datetime.today().strftime('%Y-%m-%d')


def get_data(date):
    file_names = os.listdir(os.path.abspath(os.curdir))
    data_csv = date + '.csv'
    if data_csv not in file_names:
        data = quandl.get(URL)
        data.reset_index(level=0, inplace=True)
        data.to_csv(date + '.csv')
    else:
        data = pd.read_csv(data_csv)
    return data


def monotonic_sequence(data, days, increase=True):
    data['value_diff'] = data['Close'].diff().fillna(0)
    if increase:
        seq = 5
        s = data['value_diff'].gt(0)
    else:
        seq = 4
        s = data['value_diff'].lt(0)
    data['monotonic_values'] = s.groupby(s.ne(s.shift()).cumsum()).cumcount().add(1).where(s, 0)
    df = data.tail(days)
    indexes = list(df.index[df['monotonic_values'] == seq])
    return indexes


def plot_graph(data, days):
    desired_data = data.tail(days).copy()
    desired_data['Date'] = pd.to_datetime(desired_data['Date']).apply(lambda x: x.toordinal())
    plt.xlabel('Date', fontweight='bold', color='green')
    plt.ylabel('Stock Value', fontweight='bold', color='green')
    plt.figure(figsize=(17, 10))
    plt.axhline(desired_data['Close'].mean(), color='green', ls='--', label="Average")
    plt.axhline(data.tail(30)['Close'].mean(), color='purple', ls='--', label="Monthly Average")
    plt.legend()
    plt.plot(desired_data['Date'], desired_data['Close'], marker='o', ms=3)
    inc_idx = monotonic_sequence(desired_data, days)
    dic_idx = monotonic_sequence(desired_data, days, False)
    for idx in inc_idx:
        plt.plot(desired_data['Date'].loc[idx - 4: idx], desired_data.loc[idx - 4: idx]['Close'], marker='^', ms=10)
    for idx in dic_idx:
        plt.plot(desired_data['Date'].loc[idx - 3: idx], desired_data.loc[idx - 3: idx]['Close'], marker='v', ms=10)

    x = desired_data['Date'].values.reshape(-1, 1)
    y = desired_data['Close'].values.reshape(-1, 1)
    linear_regression = LinearRegression()
    linear_regression.fit(x, y)
    y_pred = linear_regression.predict(x)
    plt.plot(x, y_pred, color='red', ms=3)

    plt.xticks(desired_data['Date'], rotation='vertical')
    plt.subplots_adjust(bottom=0.3)
    plt.title('Stock-value VS Date')
    plt.savefig(str(days) + 'Days Stock Exchange.pdf')
    plt.show()


if __name__ == '__main__':
    intervals = [7, 30, 90]
    df = get_data(CUR_DATE)
    for interval in intervals:
        plot_graph(df, interval)
