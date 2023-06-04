import csv
import matplotlib.pyplot as plt

BTC_FILENAME = "Binance_BTCUSDT_minute.csv"
ETH_FILENAME = "Binance_ETHUSDT_minute.csv"
UNIX_START = "1609459200000"  # 2021-01-01 00:00:00
UNIX_FINISH = "1612137600000"  # 2021-02-01 00:00:00
OFFSET = 60


# Возвращает массив данных за выбранное время
def getDataForPeriod(start, finish, filename):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["unix"] >= start and row["unix"] < finish:
                data.append(row)
    return data


# проходится по данным и применяет к ним addDifferenceBeetwinField
def setDifferenceBeetwinWithDataset(offset, data):
    data_difference = []
    for i in data:
        data_difference = addDifferenceBeetwinField(data_difference, offset, i)
    return data_difference


# Если работать в риал тайме, можно будет просто дергать эту функцию
# Тут бы очень классно зашли указатели, либо можно сделать класс
def addDifferenceBeetwinField(data_difference, offset, node):
    if len(data_difference) >= offset:
        data_difference[-offset]["unix_finish"] = node["unix"]
        data_difference[-offset]["value_finish"] = float(node["open"])
        data_difference[-offset]["difference"] = data_difference[-offset]["value_start"] / \
            float(node["open"])
    data_difference.append({
        "unix_start": node["unix"],
        "date_start": node["date"],
        "value_start": float(node["open"]),
        "unix_finish": "",
        "value_finish": "",
        "difference": ""})
    return data_difference


# Собирает данные для построения графика
def getPlotData(eth_difference, btc_difference, offset_major, offset_minor):
    plot_data = {
        "date": [],
        "eth_data": [],
        "btc_data": [],
        "major_time": [],
        "minor_time": [],
    }

    for i in range(len(eth_difference)):
        if type(eth_difference[i]["difference"]) == str:
            break

        if i % offset_major == 0:
            plot_data["eth_data"].append([])
            plot_data["btc_data"].append([])
            plot_data["minor_time"].append([])
            plot_data["major_time"].append([])
            plot_data["date"].append(eth_difference[i]["date_start"][:11])
        plot_data["eth_data"][-1].append(eth_difference[i]["difference"])
        plot_data["btc_data"][-1].append(btc_difference[i]["difference"])
        plot_data["minor_time"][-1].append(btc_difference[i]["date_start"][11:-3])
        if i % offset_minor == 0:
            plot_data["major_time"][-1].append(eth_difference[i]
                                          ["date_start"][11:-3])
    return plot_data


def displayPlot(plot_data, period):
    fig, ax = plt.subplots()
    ax.plot(plot_data["minor_time"][period], plot_data["eth_data"][period], plot_data["btc_data"][period])
    ax.set_xticks(plot_data["major_time"][period])
    plt.show()
    return fig, ax


# Возвращает статистику по 
def getDifferenceAdditionSignsData(eth_difference, btc_difference):
    difference_data = {
        "both_equal": 0,
        "non_equal_eth": [],
        "non_equal_btc": [],
    }

    for i in range(len(eth_difference)):
        if type(eth_difference[i]["difference"]) == str:
            break
        if eth_difference[i]["difference"] >= 1 and btc_difference[i]["difference"] >= 1:
            difference_data["both_equal"] += 1
        else:
            difference_data["non_equal_eth"].append(btc_difference[i])
            difference_data["non_equal_btc"].append(btc_difference[i])
    return difference_data


def main():
    eth = getDataForPeriod(UNIX_START, UNIX_FINISH, ETH_FILENAME)
    btc = getDataForPeriod(UNIX_START, UNIX_FINISH, BTC_FILENAME)
    eth_difference = setDifferenceBeetwinWithDataset(OFFSET, eth)
    btc_difference = setDifferenceBeetwinWithDataset(OFFSET, btc)


    # Так я получил, что моменты, когда
    # btc растет/падает, одновременно с eth случаются на 34% чаще, чем когда они движутся в одном направлении
    difference_data = getDifferenceAdditionSignsData(eth_difference, btc_difference)
    print(difference_data["both_equal"], len(difference_data["non_equal_eth"]))


    # Собираем данные для графика
    plot_data = getPlotData(eth_difference, btc_difference, 1440, 30)
    # Отображаем их на графике
    displayPlot(plot_data, 0)


# Компилируется не моментально
if __name__ == "__main__":
	main()