import boto3
from datetime import date
import datetime
import json

def main(event, context):
    print(json.dumps(event))
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



