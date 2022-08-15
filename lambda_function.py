import boto3
from datetime import date
import datetime
import collections
import dataclasses
import json


def handle_record_match(event):
    request = json.loads(event["body"])
    flag_1 = request["flag1"]
    flag_2 = request["flag2"]
    win = request["winner"]

    source_ip = event["requestContext"]["http"]["sourceIp"]

    session = boto3.Session()
    client = session.client("dynamodb")
    tdate = str(date.today())
    time = str(datetime.datetime.now())
    client.update_item(
        TableName="flagrant_storage",
        Key={"hash_key":{"S":f"rankings/{source_ip}"},"range_key":{"S":time}},
        UpdateExpression="SET winner= :p, state1= :z, state2= :c",
        ExpressionAttributeValues={":z":{"S":flag_1},":c":{"S":flag_2},":p":{"S":win}},
        ReturnValues="UPDATED_NEW"
    ) 
    return request

def handle_request_list(event):

    session1 = boto3.Session()
    client1 = session1.client("dynamodb")
    response1 = client1.query(
        TableName='flagrant_storage',
        KeyConditionExpression="#name = :name",
        ExpressionAttributeNames={"#name":"hash_key"},
        ExpressionAttributeValues={":name":{"S":"ratings"}}
    )

    results = [{'state': item["range_key"]["S"],'elo_rating': float(item["state_rating"]["S"])} for item in response1['Items']]
    ranked = sorted(results, key=lambda x: x["elo_rating"], reverse = True)
    return {"results":ranked}

def main(event, context):
    print(json.dumps(event))
    path = event["requestContext"]["http"]["path"]
    if path.lower() == "/record-match":
        return handle_record_match(event)
    else:
        return handle_request_list(event)

    # how to get an item from the database
    #-------------------------------------
    # response = client.get_item(
    #     TableName="flagrant_storage",
    #     Key={
    #         'hash_key': {'S': '123'},
    #         'range_key': {'S': 'abc'}
    #     }
    # )
    # return response['Item']



