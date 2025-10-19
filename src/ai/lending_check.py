import boto3
import json

# ========== AWS Bedrock Client ==========
from dotenv import load_dotenv
import os

load_dotenv()

client = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

def lending_decision(player):
    """
    Sends a request to Anthropic Claude via AWS Bedrock to get a lending decision.
    Returns a dictionary: {decision: bool, amount: float, interest: float, reason: str}
    """
    # Construct player info for prompt
    player_info = {
        "money": player.money,
        "debts": player.debts,
        "energy": getattr(player, 'stock', 100)
    }

    # Prompt for Claude
    prompt = f"""You are a financial advisor AI. Based on the following player profile, decide whether to lend them money.
    
Player profile:
Money: {player_info['money']}
Debts: {json.dumps(player_info['debts'])}
Energy: {player_info['energy']}

Respond strictly in JSON format with:
{{
    "decision": true or false,
    "amount": number (how much to lend, max 50% of available money if low risk),
    "interest": number (adjust if player already has loans),
    "reason": string explaining the decision
}}"""

    # Use Messages API format for Claude on Bedrock
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 250,
        "temperature": 0.3,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = client.invoke_model(
        modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0',
        contentType='application/json',
        accept='application/json',
        body=body
    )

    # Parse response
    result = json.loads(response['body'].read().decode('utf-8'))
    
    # Extract the text content from Claude's response
    content_text = result['content'][0]['text']
    
    # Parse the JSON from the response
    try:
        decision_json = json.loads(content_text)
    except json.JSONDecodeError:
        # Fallback: extract JSON manually if wrapped in markdown or other text
        import re
        match = re.search(r'\{.*\}', content_text, re.DOTALL)
        decision_json = json.loads(match.group(0)) if match else {
            "decision": False,
            "amount": 0,
            "interest": 0,
            "reason": "Error parsing response"
        }

    return decision_json

# ========== Example usage ==========
# from player import Player
# player = Player((100, 100))
# decision = lending_decision(player)
# print(decision)