import boto3
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

# ========== AWS Bedrock Client ==========
client = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

def overall_summary(player, actions):
    """
    Sends a request to Anthropic Claude via AWS Bedrock to get feedback on the player.
    Returns a dictionary: {summary: str, suggestions: str}.
    Always returns a valid dict, even if Claude response fails.
    """
    # Player info
    player_info = {
        "money": player.money,
        "debts": player.debts,
        "energy": getattr(player, 'stock', 100)
    }

    # Prompt for Claude (request strict JSON with quoted strings)
    prompt = f"""
You are a financial advisor AI. Based on the following player profile and actions, provide:
- A short overall summary of the player's financial situation
- Suggestions and lessons for loan and debt management

Player profile:
Money: {player_info['money']}
Debts: {json.dumps(player_info['debts'])}
Energy: {player_info['energy']}
Actions: {actions}

Respond strictly in JSON format like this example:
{{
    "summary": "short summary text here",
    "suggestions": "lessons and feedback text here"
}}
Ensure all values are strings and the JSON is valid.
"""

    # Messages API payload
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 250,
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}]
    })

    # Call Bedrock model
    try:
        response = client.invoke_model(
            modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0',
            contentType='application/json',
            accept='application/json',
            body=body
        )
        result = json.loads(response['body'].read().decode('utf-8'))
        content_text = result['content'][0]['text']
    except Exception as e:
        # Network, throttling, or response errors
        print("Bedrock request failed:", str(e))
        return {"summary": "Error", "suggestions": "Could not fetch feedback"}

    # Parse JSON safely
    try:
        decision_json = json.loads(content_text)
    except json.JSONDecodeError:
        # Extract JSON manually if wrapped in text
        match = re.search(r'\{.*\}', content_text, re.DOTALL)
        try:
            decision_json = json.loads(match.group(0)) if match else {}
        except json.JSONDecodeError:
            decision_json = {}

    # Ensure valid dict with string values
    return {
        "summary": str(decision_json.get("summary", "No summary")),
        "suggestions": str(decision_json.get("suggestions", "No suggestions"))
    }
