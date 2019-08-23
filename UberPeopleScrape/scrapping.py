import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import datetime
from regression import regression
import numpy as np
import matplotlib.pyplot as plt


def printGraph(x, y, itemName, type):
    # plotting the points
    plt.plot(x, y)
    plt.xlabel('Time')
    plt.ylabel('Price')

    title = itemName + "-" + type
    plt.title(title)
    # function to show the plot
    plt.show()


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
itemIndex = {}


def main():
    page = session.get("https://rsbuddy.com/exchange/summary.json", verify=True)
    allItems = json.loads(page.text)
    print(allItems.__len__())
    for itemNum in allItems:
        if allItems[itemNum]["members"] == False:
            itemIndex[allItems[itemNum]["name"]] = allItems[itemNum]

    print(itemIndex.__len__())
    one_gp_items()
    buy_less_than_sell()


def meanCheck(itemId, itemName):
    pageUrl = "http://services.runescape.com/m=itemdb_oldschool/api/graph/" + itemId + ".json"
    page = session.get(pageUrl, verify=True)
    response = json.loads(page.text)
    dailyArray = response["daily"]
    averageArray = response["average"]
    daily_six_month_value = list(dailyArray.values())
    average_six_month_values = list(averageArray.values())
    daily_three_month_values = daily_six_month_value[89:]
    average_three_month_values = average_six_month_values[89:]
    daily_month_values = daily_six_month_value[149:]
    average_month_values = average_six_month_values[149:]
    daily_weekly_values = daily_six_month_value[172:]
    average_weekly_values = average_six_month_values[172:]
    return [daily_month_values, daily_three_month_values, daily_weekly_values]


def one_gp_items():
    print("1 GP items that make profit out of", itemIndex.__len__())
    unit_list = []
    for item in itemIndex:
        if itemIndex[item]["buy_average"] == 1 and validBuy(item):
            toInsert = {}
            toInsert["Name"] = item
            toInsert["id"] = str(itemIndex[item]["id"])
            toInsert["Buy"] = itemIndex[item]["buy_average"]
            toInsert["Sell"] = itemIndex[item]["sell_average"]
            toInsert["Margin"] = (itemIndex[item]["sell_average"] - itemIndex[item]["buy_average"])
            toInsert["Shop Price"] = itemIndex[item]["sp"]
            unit_list.append(toInsert)

    printList(unit_list)
def buy_less_than_sell():
    print("These Items have a lower buy avg than sell avg out of", itemIndex.__len__())
    valid_item_list = []
    for item in itemIndex:
        if lowPrice(item) and validBuy(item) and highVolume(item) and profit(item):
            toInsert = {}
            toInsert["Name"] = item
            toInsert["id"] = str(itemIndex[item]["id"])
            toInsert["Buy"] = itemIndex[item]["buy_average"]
            toInsert["Sell"] = itemIndex[item]["sell_average"]
            toInsert["Margin"] = (itemIndex[item]["sell_average"] - itemIndex[item]["buy_average"])
            toInsert["Shop Price"] = itemIndex[item]["sp"]
            valid_item_list.append(toInsert)
    print(valid_item_list.__len__())
    printList(valid_item_list)


def profit(item):
    return itemIndex[item]["buy_average"] <= itemIndex[item]["sell_average"]


def validBuy(item):
    return itemIndex[item]["buy_average"] != 0


def printList(itemList):
    for item in itemList:
            values = meanCheck(item["id"], item["Name"])
            monthlyMean = np.average(values[0])
            yearlyMean = np.average((values[1]))
            weeklyMean = np.average((values[2]))
            print("---- GOOD ITEM ----")
            print(item["Name"])
            print("Monthly Mean =", monthlyMean)
            print("Weekly Mean =", weeklyMean)
            index = values.__len__() - 1
            print("Latest Value =", values[index])
            print("Current Buying Price", item['Buy'])
            print("Current Selling Price", item['Sell'])
            print("Current Margin", item['Margin'])
            print("Quantity:", itemIndex[item["Name"]]["sell_quantity"])
            print("---- --------- ----")


def highMargin(item):
    margin = itemIndex[item]["buy_average"] - itemIndex[item]["sell_average"]
    return margin > (itemIndex[item]["sell_average"] * 0.1)


def inStock(item):
    return itemIndex[item]["sell_quantity"] > itemIndex[item]["buy_quantity"]


def lowPrice(item):
    return itemIndex[item]["buy_average"] < 100


def highVolume(item):
    return itemIndex[item]['overall_quantity'] >= 10000


def printItem(item):
    print(item["Name"], item["Buy"], item["Sell"], item["Margin"], itemIndex[item["Name"]]['overall_quantity'])


main()
