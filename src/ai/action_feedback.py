"""
Action Feedback System - AI-powered feedback for player decisions
"""
import boto3
import json
from dotenv import load_dotenv
import os
import re

load_dotenv()

client = boto3.client(
    "bedrock-runtime",
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

def call_claude(prompt, max_tokens=400):
    """Helper function to call Claude via Bedrock"""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": 0.4,
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

    result = json.loads(response['body'].read().decode('utf-8'))
    content_text = result['content'][0]['text']
    
    try:
        return json.loads(content_text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', content_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}


def get_action_feedback(player, action_type, action_details):
    """
    Get immediate AI feedback on a specific action
    
    Args:
        player: Player object
        action_type: Type of action (loan, sale, repayment)
        action_details: Dictionary with action-specific details
    
    Returns:
        dict: {feedback: str, severity: str, emoji: str, tip: str}
    """
    total_debt = sum(player.debts.values())
    debt_to_money_ratio = total_debt / player.money if player.money > 0 else float('inf')
    
    prompt = f"""You are a financial advisor providing immediate feedback on a player's action in a financial literacy game.

PLAYER STATUS:
- Money: {player.money} gold
- Stock: {player.stock}
- Total Debt: {total_debt} gold
- Debt-to-Money Ratio: {debt_to_money_ratio:.2f}
- Individual Debts: {json.dumps(player.debts)}

ACTION TAKEN:
Type: {action_type}
Details: {json.dumps(action_details)}

CONTEXT:
- Game Goal: Reach 500 gold with 0 debt
- Lender Interest Rates:
  * Banker Bard: 2-8% (dynamic, based on risk)
  * Poultry Guy: 10% (credit card style)
  * Farmer Finn: 8% (emergency loans)
  * Witch of Woe: 25% (predatory)

Provide immediate, encouraging feedback on this action. Respond in JSON format:
{{
    "feedback": "2-3 sentence analysis of this specific action",
    "severity": "positive/neutral/warning/danger",
    "emoji": "single emoji representing the action quality",
    "tip": "one practical tip for next steps"
}}

Be supportive but honest. Help them learn financial literacy."""

    try:
        return call_claude(prompt, max_tokens=300)
    except Exception as e:
        return {
            "feedback": "Action recorded successfully.",
            "severity": "neutral",
            "emoji": "📝",
            "tip": "Keep playing to learn more!"
        }


def get_financial_suggestions(player):
    """
    Get strategic suggestions based on current financial status
    
    Args:
        player: Player object
    
    Returns:
        dict: {suggestions: list, priority: str, next_steps: list, health: str}
    """
    total_debt = sum(player.debts.values())
    net_worth = player.money - total_debt
    
    # Calculate debt composition
    debt_breakdown = {}
    for lender, amount in player.debts.items():
        if amount > 0:
            debt_breakdown[lender] = {
                "amount": amount,
                "percentage": round((amount / total_debt * 100), 1) if total_debt > 0 else 0
            }
    
    prompt = f"""You are a financial advisor analyzing a player's overall strategy in a financial literacy game.

CURRENT FINANCIAL STATUS:
- Money: {player.money} gold
- Stock: {player.stock}
- Total Debt: {total_debt} gold
- Net Worth: {net_worth} gold

DEBT BREAKDOWN:
{json.dumps(debt_breakdown, indent=2)}

GAME GOAL: Reach 500 gold with 0 debt

LENDER CONTEXT:
- Banker Bard: 2-8% interest (SAFE - best option)
- Poultry Guy: 10% interest (RISKY - credit card trap)
- Farmer Finn: 8% interest (EMERGENCY - creates spirals)
- Witch of Woe: 25% interest (PREDATORY - debt trap)

Analyze their financial strategy and provide actionable suggestions. Respond in JSON format:
{{
    "suggestions": ["specific suggestion 1", "specific suggestion 2", "specific suggestion 3"],
    "priority": "immediate/important/advisory",
    "next_steps": ["concrete action 1", "concrete action 2"],
    "health": "excellent/good/concerning/critical",
    "assessment": "brief 1-2 sentence assessment of their approach"
}}

Focus on practical advice they can implement immediately. Be encouraging."""

    try:
        return call_claude(prompt, max_tokens=500)
    except Exception as e:
        return {
            "suggestions": [
                "Generate sales at the coffee shop to build income",
                "Avoid high-interest lenders (Witch and Poultry Guy)",
                "Pay off highest interest debts first"
            ],
            "priority": "advisory",
            "next_steps": ["Visit Coffee Shop", "Check Account"],
            "health": "unknown",
            "assessment": "Keep working to improve your financial situation."
        }


def get_loan_analysis(player, loan_amount, interest_rate, lender_name):
    """
    Analyze a loan offer before the player accepts it
    
    Args:
        player: Player object
        loan_amount: Amount of gold being borrowed
        interest_rate: Interest rate as decimal (e.g., 0.02 for 2%)
        lender_name: Name of the lender
    
    Returns:
        dict: Analysis of the loan decision
    """
    total_debt = sum(player.debts.values())
    amount_owed = round(loan_amount * (1 + interest_rate), 2)
    
    prompt = f"""You are a financial advisor analyzing a loan offer in a financial literacy game.

LOAN OFFER:
- Lender: {lender_name}
- Amount: {loan_amount} gold
- Interest Rate: {interest_rate * 100}%
- Total to Repay: {amount_owed} gold

PLAYER STATUS:
- Current Money: {player.money} gold
- Current Stock: {player.stock}
- Current Total Debt: {total_debt} gold
- Debts: {json.dumps(player.debts)}

GAME CONTEXT:
- Average sale generates 10-50 gold but costs 20 stock
- Goal: Reach 500 gold with 0 debt

Calculate and provide loan analysis. Respond in JSON format:
{{
    "sales_needed": number (approximate sales to repay),
    "risk_level": "low/medium/high/critical",
    "repayment_strategy": "specific strategy recommendation",
    "warning": "any warnings (empty string if none)",
    "recommendation": "should they take this loan? why?"
}}

Be realistic and educational."""

    try:
        return call_claude(prompt, max_tokens=350)
    except Exception as e:
        avg_sale = 30
        sales = max(1, int(amount_owed / avg_sale))
        return {
            "sales_needed": sales,
            "risk_level": "medium",
            "repayment_strategy": "Generate consistent sales to pay back quickly",
            "warning": "Make sure you can repay this loan",
            "recommendation": "Consider if you really need this loan right now."
        }