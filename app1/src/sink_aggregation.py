import json
from pymongo import database
from pymongo.mongo_client import MongoClient

###
# This Sink service transform incoming WiFi data from one station (PC,Smartphone, IoT Device, Sound device ...) 
# into aggregate data and detect anomalies to improve WiFi services
# Example message:
# {
#  "info": {
#        "identifier": "GTW02",
#       "uploadTime" : 1665057512,
#        "manufacturerName" : "Sagemcom"
#    },
#    "wifiData": [
#        {
#            "eventTime" : 1665057512,
#            "deviceType": "PC",
#            "bytesSent": 782140,
#            "bytesReceived" : 15860542,
#            "connection": "2_4GHZ",
#            "rssi": -56
#        }
#     ]
# }
# 
###
# The expected data is an aggregation of:
# - WiFi metrics aggregation (min/max/avg)
# - Number of connection changes during the data collection
# - Monitoring RSSI value during the collection
#   - RSSI (Received Signal Strength Indication) --> Indication of WiFi Link quality --> A low value indicate a poor WiFi link quality

# Threshold used for RSSI
RSSITHRESHOLD = -70

#MongoDB ENV
MONGO_DB_HOST= "db1"
MONGO_DB_PORT = 27017
MONGO_DB_USERNAME = "mongodb"
MONGO_DB_PASSWORD = "mongodb"

MONGO_DB_DATABASE_NAME = "dataLake"
MONGO_DB_COLLECTION_NAME = "wifi"

# Main function
def sink_aggregation(json_data):
    aggregate_data = {
        "identifier": None,
        "manufacturerName": None,
        "startTime": None,
        "endTime": None,
        "wifiAggregate": {
            "deviceType" : None,
            "minRSSI": None,
            "avgRSSI": None,
            "maxRSSI": None,
            "countBandChange" : None
        },
        "anomalies_report" : []
    }
    aggregate_data["identifier"] = json_data["info"]["identifier"]
    aggregate_data["manufacturerName"] = json_data["info"]["manufacturerName"]
    aggregate_data["startTime"] = find_min(json_data["wifiData"],"eventTime")
    aggregate_data["endTime"] = find_max(json_data["wifiData"],"eventTime")
    aggregate_data["wifiAggregate"]["deviceType"] = json_data["wifiData"][0]["deviceType"]
    aggregate_data["wifiAggregate"]["countBandChange"] = count_value_change(json_data["wifiData"],"connection")
    aggregate_data["wifiAggregate"]["minRSSI"] = find_min(json_data["wifiData"],"rssi")
    aggregate_data["wifiAggregate"]["maxRSSI"] = find_max(json_data["wifiData"],"rssi")
    aggregate_data["wifiAggregate"]["avgRSSI"] = calculate_avg(json_data["wifiData"],"rssi")
    aggregate_data["anomalies_report"] = detect_anomaly_min(json_data["wifiData"],"rssi",RSSITHRESHOLD)

    identifier_data = json_data["info"]["identifier"]

    # Mongo Insert data into mongoDB
    try:
        mongo_server = MongoClient(f"mongodb://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOST}:{MONGO_DB_PORT}/")
        insert_data_mongo(mongo_server,aggregate_data)        

        # Find the data into mongoDB
        result_aggregate_data = find_data_mongo(mongo_server,identifier_data)
    except:
        result_aggregate_data = {}
    return result_aggregate_data


def find_min(array,key):
    if len(array) >0:
        min = array[0][key]
        for i in range(len(array)):
            if array[i][key] != None:
                if array[i][key] < min:
                    min = array[i][key]
        return min 
    return None

def find_max(array,key):
    if len(array) >0:
        max = array[0][key]
        for i in range(len(array)):
            if array[i][key] != None:
                if array[i][key] > max:
                    max = array[i][key]
        return max 
    return None

def count_value_change(array,key):
    counter = 0
    if len(array) > 0:
        ref_value = array[0][key]
        for i in range(len(array)):
            if ref_value != array[i][key]:
                counter += 1
                ref_value = array[i][key]
        return counter
    return None

def calculate_avg(array,key):
    if len(array) > 0:
        sum = 0
        for i in range(len(array)):
            sum += array[i][key]
        return sum//len(array)
    return None
      
def detect_anomaly_min(array,key,threshold):
    array_anomaly = []
    if len(array) > 0:
        for i in range(len(array)):
            if array[i][key] < threshold:
                anomaly_report = {
                    "eventTime": None,
                    "deviceType": None,
                    "rssi": None
                }
                anomaly_report["eventTime"] = array[i]["eventTime"]
                anomaly_report["deviceType"] = array[i]["deviceType"]
                anomaly_report["connection"] = array[i]["connection"]
                anomaly_report["rssi"] = array[i]["rssi"]
                array_anomaly.append(anomaly_report)
    return array_anomaly


# Connect on mongodb and post one aggregated WiFi Data
def insert_data_mongo(mongo_server: MongoClient,json_insert):
    try:
        collection = mongo_server[MONGO_DB_DATABASE_NAME][MONGO_DB_COLLECTION_NAME]
        collection.insert_one(json_insert)
        return True
    except OverflowError:
        print("Cannot put data into MongoDB")
        return False

def find_data_mongo(mongo_server: MongoClient, identifier:str):
    result = {}
    try:
        result = mongo_server[MONGO_DB_DATABASE_NAME][MONGO_DB_COLLECTION_NAME]\
            .find_one({"identifier": identifier},{"_id": 0})
    except:
        print("Cannot find data into MongoDB")
    return result