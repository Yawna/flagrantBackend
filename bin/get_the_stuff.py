import boto3
import dataclasses
import math
import collections
from datetime import date
import datetime

@dataclasses.dataclass
class Ranking:

    winner: str
    state1: str
    state2: str

# Function to calculate the Probability
def probability(rating1, rating2):
 
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))
 
 
# Function to calculate Elo rating
# K is a constant.
# d determines whether
# Player A wins or Player B.
def elo_rating(Ra, Rb, K, d):
  
 
    # To calculate the Winning
    # Probability of Player B
    Pb = probability(Ra, Rb)
 
    # To calculate the Winning
    # Probability of Player A
    Pa = probability(Rb, Ra)
 
    # Case 1: When Player A wins
    # Updating the Elo Ratings
    if (d) :
        Ra = Ra + K * (1 - Pa)
        Rb = Rb + K * (0 - Pb)
     
 
    # Case 2: When Player B wins
    # Updating the Elo Ratings
    else :
        Ra = Ra + K * (0 - Pa)
        Rb = Rb + K * (1 - Pb)
     
    return(round(Ra, 6),round(Rb, 6))



client = boto3.client('dynamodb')

def dump_table(table_name):
    results = []
    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = client.scan(
                TableName=table_name,
                FilterExpression="contains(#name, :name)",
                ExpressionAttributeNames={"#name":"hash_key"},
                ExpressionAttributeValues={":name":{"S":"ranking"}},
                ExclusiveStartKey=last_evaluated_key
            )
                
        else: 
           response = client.scan(
                TableName=table_name,
                FilterExpression="contains(#name, :name)",
                ExpressionAttributeNames={"#name":"hash_key"},
                ExpressionAttributeValues={":name":{"S":"ranking"}}
           )
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        results.extend([Ranking(item["winner"]["S"], item["state1"]["S"], item["state2"]["S"]) for item in response['Items']])
        
        if not last_evaluated_key:
            break
    return results

# Usage
data = dump_table('flagrant_storage')
state_scores = collections.defaultdict(lambda: 1500)
for row in data:

    rating1,rating2 = elo_rating(state_scores[row.state1], state_scores[row.state2], 30, row.state1 == row.winner)
    state_scores[row.state1] = rating1
    state_scores[row.state2] = rating2

ranked = list(state_scores.items())
ranked = sorted(ranked, key=lambda x: x[1])

session = boto3.Session()
client2 = session.client("dynamodb")
time = str(datetime.datetime.now())

for item in ranked:
    state = item[0]
    elo = str(item[1])
    client2.update_item(
       TableName="flagrant_storage",
       Key={"hash_key":{"S":"ratings"},"range_key":{"S":state}},
       UpdateExpression="SET last_update= :p, state_rating= :z",
       ExpressionAttributeValues={":z":{"S":elo},":p":{"S":time}},
       ReturnValues="UPDATED_NEW"
    ) 