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
def elo_rating(rating_1: float, rating_2: float, stake: float, first_won: bool):
    
    """
    Calculate the new elo rating for two competitors based on the incoming match result.
    
    :param rating_1:
        The elo rating of the first player.
    :param rating_2:
        The elo rating of the second player.
    :param stake:
        The maximum number of points up for grabs in the match. This will never be fully be transferred.
        A highly unlikely win based on rankings will lead to a large portion of the points being transferred
        while a highly likely win will lead to few points being transferred.
    :param first_won:
        Whether the first player won.
    """

    Pb = probability(rating_1, rating_2)
 
    # To calculate the Winning
    # Probability of Player A
    Pa = probability(rating_2, rating_1)
 
    # Case 1: When Player A wins
    # Updating the Elo Ratings
    if (first_won) :
        rating_1 = rating_1 + stake * (1 - Pa)
        rating_2 = rating_2 + stake * (0 - Pb)
     
 
    # Case 2: When Player B wins
    # Updating the Elo Ratings
    else :
        rating_1 = rating_1 + stake * (0 - Pa)
        rating_2 = rating_2 + stake * (1 - Pb)
     
    return(round(rating_1, 6),round(rating_2, 6))



client = boto3.client('dynamodb')

def dump_table(table_name):
    paginator = client.get_paginator('scan')
    response_iterator = paginator.paginate(
        TableName=table_name,
        FilterExpression="contains(#name, :name)",
        ExpressionAttributeNames={"#name": "hash_key"},
        ExpressionAttributeValues={":name": {"S": "ranking"}},
    )
        
    return [
        Ranking(item["winner"]["S"], item["state1"]["S"], item["state2"]["S"]) 
        for page in response_iterator
            for item in page['Items']]


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
    ) 