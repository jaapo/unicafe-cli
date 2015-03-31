#!/usr/bin/env python

import urllib2
import json
import sys
import codecs
import datetime
import argparse

APIURL ="http://messi.hyyravintolat.fi/publicapi" 
allprice = ["Edullisesti", "Maukkaasti", "Makeasti", "Kevyesti"]
today = datetime.date.today()
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def apidate2date(apidate):
    d=datetime.datetime.strptime(apidate.split(' ')[1], "%d.%m").date()
    d=d.replace(year=today.year)
    return d

def thisweek(date):
    return today.isocalendar()[1] == date.isocalendar()[1]

def daterangestr(date1, date2):
    return date1 if date1 == date2 else date1 + " - " + date2

def gethours(fooddata):
    opentime = None
    closetime = None
    daystrs = []
    for time in fooddata["information"]["lounas"]["regular"]:
        opentime = time["open"]
        closetime = time["close"]
        days = []
        for day in time["when"]:
            if day and not day == "previous":
                days.append(day)
            elif days:
                daystrs.append([", ".join(days), opentime+"-"+closetime])
                days=[]

    for dayset,hours in daystrs:
        print dayset + ": " + hours

    extimes = []
    for extime in fooddata["information"]["lounas"]["exception"]:
        if extime["from"] and extime["to"]:
            days = daterangestr(extime["from"], extime["to"])
            status = "Suljettu" if extime["closed"] else extime["open"] + "-" + extime["close"]
            extimes.append(days + ": " + status)
    if extimes:
        print "\033[31mPoikkeukset\033[0m"
        print ", ".join(extimes)

def getfood(fooddata, prices):
    for fd in fooddata["data"]:
        if not fd["data"]:
            continue

        menudate = apidate2date(fd["date"])
        if menudate == today:
            print '\033[1m' + fd["date"] + '\033[0m'
        elif menudate < today or not thisweek(menudate):
            continue
        else:
            print fd["date"]

        for f in filter(lambda x: x["price"]["name"] in prices, fd["data"]):
            price = f["price"]["name"]
            print "  " + f["name"] + ("" if price=="Edullisesti" else " (" + price + ")")

def main(restaurants, prices, hours):
    allrestaurants = json.load(urllib2.urlopen(APIURL+"/restaurants"))["data"]
    restaurants = filter(lambda r: r["name"] in restaurants, allrestaurants)

    if not restaurants:
        print "restaurant not found"
        exit(2)

    for restaurant in restaurants:
        fooddata = json.load(urllib2.urlopen(APIURL + "/restaurant/" + str(restaurant["id"])))
        print restaurant["name"]
        print '='*len(restaurant["name"])
        if hours:
            gethours(fooddata)
        print
        getfood(fooddata, prices)
        print

parser = argparse.ArgumentParser(description="Get Unicafe lunch lists")
parser.add_argument("restaurant", nargs="?")
parser.add_argument("-r", metavar="restaurant", nargs="+", action="append")
parser.add_argument("-p", metavar="prices", nargs="*", action="append", choices=allprice)
parser.add_argument("-o", action="count")
p = None

args = parser.parse_args()
r = [args.restaurant] if args.restaurant else map(lambda r: r[0], args.r)
p = allprice if not args.p else map(lambda p: p[0], args.p)
main(r, p, args.o)
