"""
Financial Literacy Game Functions - WITH AI FEEDBACK & ACTION TRACKING
Integrates with UI, action tracking, and AI feedback systems
"""
import random
from ai.lending_check import lending_decision
from ai.action_feedback import get_action_feedback, get_financial_suggestions, get_loan_analysis
from action_tracker import action_tracker

class GameState:
    def __init__(self):
        self.tutorial_shown = False
        self.days_passed = 0

game_state = GameState()

# ============ POPUP SYSTEM ============

def show_popup(ui, player, title, description, options):
    """Show a popup menu with options"""
    ui.popup_title = title
    ui.popup_description = description
    ui.popup_buttons = options
    ui.showing_popup = True

# ============ COFFEE SHOP ACTIONS ============

def coffee_shop_action(ui, player, action):
    """Handle coffee shop interactions"""
    
    if action == "Generate a Sale":
        if player.stock >= 20:
            sale = random.randint(10, 50)
            player.money += sale
            player.spend_stock(20, "Generated a Sale")
            
            # Log the action
            action_tracker.log_action("sale", {
                "amount": sale,
                "stock_used": 20,
                "remaining_money": player.money,
                "remaining_stock": player.stock
            })
            
            # Get AI feedback on this sale
            feedback = get_action_feedback(player, "sale", {
                "amount": sale,
                "stock_used": 20,
                "remaining_money": player.money,
                "remaining_stock": player.stock
            })
            
            emoji = feedback.get('emoji', '💰')
            tip = feedback.get('tip', 'Keep it up!')
            
            show_popup(ui, player, 
                "Sale Generated ✓",
                f"""You generated a sale for {sale} gold!
Stock used: 20
Remaining stock: {int(player.stock)}
Total Gold: {int(player.money)}

{emoji} TIP: {tip}""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Insufficient Stock ⚠️",
                f"You need 20 stock to generate a sale.\nCurrent stock: {int(player.stock)}\n\nConsider buying stock or borrowing strategically from the Banker.",
                [("Back", "close")]
            )
    
    elif action == "Check Account":
        total_debt = sum(player.debts.values()) if player.debts else 0
        net_worth = player.money - total_debt
        
        # Get action summary for display
        summary = action_tracker.get_action_summary()
        
        show_popup(ui, player,
            "Account Summary",
            f"""💰 Gold: {int(player.money)}
🛒 Stock: {int(player.stock)}
💸 Total Debt: {int(total_debt)}

DEBTS BY LENDER:
🏦 Banker: {int(player.debts.get('Banker Bard', 0))}
🐔 Poultry: {int(player.debts.get('Poultry Guy Pip', 0))}
🌾 Farmer: {int(player.debts.get('Farmer Finn', 0))}
🧙 Witch: {int(player.debts.get('Witch of Woe', 0))}

Net Worth: {int(net_worth)}

SESSION STATS:
Sales: {summary['sales_made']} | Loans: {summary['loans_taken']} | Repayments: {summary['repayments_made']}""",
            [("View Suggestions", "suggestions"), ("Back", "close")]
        )
    
    elif action == "View Suggestions":
        # Get AI-powered suggestions
        suggestions_data = get_financial_suggestions(player)
        suggestions = suggestions_data.get('suggestions', [])
        next_steps = suggestions_data.get('next_steps', [])
        health = suggestions_data.get('health', 'unknown')
        assessment = suggestions_data.get('assessment', '')
        
        health_emoji = {
            'excellent': '🌟',
            'good': '✅',
            'concerning': '⚠️',
            'critical': '🚨'
        }.get(health, 'ℹ️')
        
        suggestions_text = "\n".join([f"• {s}" for s in suggestions[:3]])
        steps_text = "\n".join([f"→ {s}" for s in next_steps[:2]])
        
        show_popup(ui, player,
            f"{health_emoji} Financial Guidance",
            f"""FINANCIAL HEALTH: {health.upper()}
{assessment}

RECOMMENDATIONS:
{suggestions_text}

NEXT STEPS:
{steps_text}""",
            [("Back", "close")]
        )

# ============ BANKER ACTIONS (DYNAMIC AI INTEREST) ============

def banker_action(ui, player, action):
    """Handle Banker Bard lending with AI-based dynamic rates"""
    
    if action == "Request Loan":
        # Get AI loan decision with dynamic interest
        decision = lending_decision(player)

        if not decision or not decision.get("decision"):
            reason = decision.get("reason", "Risk assessment failed.")
            
            # Log the rejected loan attempt
            action_tracker.log_action("loan_rejected", {
                "lender": "Banker Bard",
                "reason": reason
            })
            
            show_popup(ui, player,
                "🏦 Loan Denied",
                f"""❌ The Banker declines your request.

REASON: {reason}

TIP: Reduce existing debt and build steady income to improve your credit.""",
                [("Back", "close")]
            )
            return
        
        # Loan approved - get details
        amount = decision.get("amount", 0)
        interest = decision.get("interest", 0.02)
        reason = decision.get("reason", "Loan approved.")
        owed = round(amount * (1 + interest), 2)
        
        # Get loan analysis before accepting
        analysis = get_loan_analysis(player, amount, interest, "Banker Bard")
        
        # Store loan details for confirmation
        ui.pending_loan = {
            "amount": amount,
            "interest": interest,
            "owed": owed,
            "lender": "Banker Bard",
            "reason": reason,
            "analysis": analysis
        }
        
        # Show loan offer with analysis
        risk_emoji = {
            'low': '✅',
            'medium': '⚠️',
            'high': '🚨',
            'critical': '💀'
        }.get(analysis.get('risk_level', 'medium'), '⚠️')
        
        show_popup(ui, player,
            "🏦 Loan Offer",
            f"""LOAN TERMS:
• Amount: {int(amount)} gold
• Interest: {int(interest * 100)}%
• Total Owed: {int(owed)} gold

{risk_emoji} RISK: {analysis.get('risk_level', 'medium').upper()}

ANALYSIS:
• Sales needed: ~{analysis.get('sales_needed', '?')}
• {analysis.get('recommendation', '')}

💬 Banker: "{reason}"

{analysis.get('warning', '')}""",
            [("Accept Loan", "accept_banker"), ("Decline", "close")]
        )
    
    elif action == "Accept Loan":
        # Apply the pending loan
        if hasattr(ui, 'pending_loan'):
            loan = ui.pending_loan
            player.money += loan['amount']
            player.debts["Banker Bard"] = player.debts.get("Banker Bard", 0) + loan['owed']
            
            # Log the loan action
            action_tracker.log_action("loan", {
                "lender": "Banker Bard",
                "amount": loan['amount'],
                "interest_rate": loan['interest'],
                "amount_owed": loan['owed'],
                "remaining_money": player.money,
                "total_debt": sum(player.debts.values())
            })
            
            # Get feedback on taking this loan
            feedback = get_action_feedback(player, "loan", {
                "lender": "Banker Bard",
                "amount": loan['amount'],
                "interest_rate": loan['interest'],
                "amount_owed": loan['owed']
            })
            
            show_popup(ui, player,
                "🏦 Loan Processed",
                f"""✅ {int(loan['amount'])} gold added to your account!
You now owe: {int(loan['owed'])} gold

{feedback.get('emoji', '💡')} {feedback.get('feedback', '')}

TIP: {feedback.get('tip', 'Use this wisely!')}""",
                [("Continue", "close")]
            )
            
            delattr(ui, 'pending_loan')
    
    elif action == "Repay Debt":
        debt = player.debts.get("Banker Bard", 0)
        if debt <= 0:
            show_popup(ui, player, 
                "No Debt", 
                "You have no debt to the Banker.", 
                [("Back", "close")]
            )
        elif player.money >= debt:
            player.money -= debt
            player.debts["Banker Bard"] = 0
            
            # Log the repayment
            action_tracker.log_action("repayment", {
                "lender": "Banker Bard",
                "amount": debt,
                "remaining_money": player.money,
                "total_debt": sum(player.debts.values())
            })
            
            # Get feedback on repayment
            feedback = get_action_feedback(player, "repayment", {
                "lender": "Banker Bard",
                "amount": debt,
                "remaining_money": player.money
            })
            
            show_popup(ui, player,
                "Debt Paid ✓",
                f"""You repaid {int(debt)} gold to Banker Bard!
Remaining Gold: {int(player.money)}

{feedback.get('emoji', '✅')} {feedback.get('feedback', 'Great job!')}

{feedback.get('tip', '')}""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Insufficient Funds",
                f"You need {int(debt)} gold but only have {int(player.money)}.",
                [("Back", "close")]
            )

# ============ POULTRY ACTIONS (CREDIT CARD - 10% INTEREST) ============

def poultry_action(ui, player, action):
    """Handle Poultry interactions - CREDIT CARD STYLE"""
    
    if action == "Borrow 25 stock":
        amount = 25
        rate = 0.10
        owed = round(amount * (1 + rate), 2)
        
        player.stock += amount
        player.debts['Poultry Guy Pip'] = player.debts.get('Poultry Guy Pip', 0) + owed
        
        # Log the loan
        action_tracker.log_action("loan", {
            "lender": "Poultry Guy Pip",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed,
            "remaining_stock": player.stock,
            "total_debt": sum(player.debts.values())
        })
        
        # Get AI feedback
        feedback = get_action_feedback(player, "loan", {
            "lender": "Poultry Guy Pip",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed
        })
        
        show_popup(ui, player,
            "🐔 Quick Credit Approved",
            f"""Stock received: {amount}
You will owe: {owed} gold (10% interest)

⚠️ {feedback.get('feedback', 'Credit cards can trap you in debt!')}

TIP: {feedback.get('tip', 'Pay this back quickly!')}""",
            [("Continue", "close")]
        )
    
    elif action == "Borrow 15 stock":
        amount = 15
        rate = 0.10
        owed = round(amount * (1 + rate), 2)
        
        player.stock += amount
        player.debts['Poultry Guy Pip'] = player.debts.get('Poultry Guy Pip', 0) + owed
        
        # Log the loan
        action_tracker.log_action("loan", {
            "lender": "Poultry Guy Pip",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed,
            "remaining_stock": player.stock,
            "total_debt": sum(player.debts.values())
        })
        
        feedback = get_action_feedback(player, "loan", {
            "lender": "Poultry Guy Pip",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed
        })
        
        show_popup(ui, player,
            "🐔 Credit Extended",
            f"""Stock received: {amount}
You will owe: {owed} gold (10% interest)

{feedback.get('emoji', '⚠️')} {feedback.get('feedback', '')}

{feedback.get('tip', '')}""",
            [("Continue", "close")]
        )
    
    elif action == "Repay Debt":
        debt = player.debts.get('Poultry Guy Pip', 0)
        if debt <= 0:
            show_popup(ui, player,
                "No Debt",
                "You have no credit card debt.",
                [("Back", "close")]
            )
        elif player.money >= debt:
            player.money -= debt
            player.debts['Poultry Guy Pip'] = 0
            
            # Log repayment
            action_tracker.log_action("repayment", {
                "lender": "Poultry Guy Pip",
                "amount": debt,
                "remaining_money": player.money,
                "total_debt": sum(player.debts.values())
            })
            
            feedback = get_action_feedback(player, "repayment", {
                "lender": "Poultry Guy Pip",
                "amount": debt
            })
            
            show_popup(ui, player,
                "Debt Paid ✓",
                f"""You broke free from the credit trap!
Paid: {int(debt)} gold
Remaining: {int(player.money)} gold

{feedback.get('emoji', '✅')} {feedback.get('feedback', '')}""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Insufficient Funds",
                f"You need {int(debt)} gold but only have {int(player.money)}.",
                [("Back", "close")]
            )
    
    elif action == "Buy 10 Stock":
        stock_amount = 10
        stock_price_per_unit = 2
        total_price = stock_amount * stock_price_per_unit

        if player.money >= total_price:
            player.money -= total_price
            player.stock += stock_amount
            
            # Log purchase
            action_tracker.log_action("purchase", {
                "item": "stock",
                "amount_bought": stock_amount,
                "cost": total_price,
                "remaining_money": player.money,
                "remaining_stock": player.stock
            })

            feedback = get_action_feedback(player, "purchase", {
                "item": "stock",
                "amount_bought": stock_amount,
                "cost": total_price,
                "remaining_money": player.money,
                "remaining_stock": player.stock
            })

            show_popup(ui, player,
                "Stock Purchased ✓",
                f"""You bought {stock_amount} stock for {total_price} gold.
Remaining stock: {int(player.stock)}
Remaining gold: {int(player.money)}

{feedback.get('emoji', '🛒')} {feedback.get('feedback', '')}

TIP: {feedback.get('tip', '')}""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Not Enough Gold",
                f"You need {total_price} gold to buy {stock_amount} stock.\nCurrent gold: {int(player.money)}",
                [("Back", "close")]
            )

# ============ FARMER ACTIONS (EMERGENCY - 8% INTEREST) ============

def farmer_action(ui, player, action):
    """Handle Farmer interactions - EMERGENCY LENDING"""
    
    if action == "Borrow 10 stock":
        amount = 10
        rate = 0.08
        owed = round(amount * (1 + rate), 2)
        
        player.stock += amount
        player.debts['Farmer Finn'] = player.debts.get('Farmer Finn', 0) + owed
        
        # Log the loan
        action_tracker.log_action("loan", {
            "lender": "Farmer Finn",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed,
            "remaining_stock": player.stock,
            "total_debt": sum(player.debts.values())
        })
        
        feedback = get_action_feedback(player, "loan", {
            "lender": "Farmer Finn",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed
        })
        
        show_popup(ui, player,
            "🌾 Emergency Loan",
            f"""Stock received: {amount}
You will owe: {owed} gold (8% interest)

{feedback.get('emoji', '⚠️')} {feedback.get('feedback', '')}

TIP: {feedback.get('tip', '')}""",
            [("Continue", "close")]
        )
    
    elif action == "Borrow 5 stock":
        amount = 5
        rate = 0.08
        owed = round(amount * (1 + rate), 2)
        
        player.stock += amount
        player.debts['Farmer Finn'] = player.debts.get('Farmer Finn', 0) + owed
        
        # Log the loan
        action_tracker.log_action("loan", {
            "lender": "Farmer Finn",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed,
            "remaining_stock": player.stock,
            "total_debt": sum(player.debts.values())
        })
        
        feedback = get_action_feedback(player, "loan", {
            "lender": "Farmer Finn",
            "amount": amount,
            "interest_rate": rate,
            "amount_owed": owed
        })
        
        show_popup(ui, player,
            "🌾 Small Emergency Loan",
            f"""Stock received: {amount}
You will owe: {owed} gold (8% interest)

{feedback.get('feedback', '')}

{feedback.get('tip', '')}""",
            [("Continue", "close")]
        )
    
    elif action == "Repay Debt":
        debt = player.debts.get('Farmer Finn', 0)
        if debt <= 0:
            show_popup(ui, player,
                "No Debt",
                "You have no debt to Farmer Finn.",
                [("Back", "close")]
            )
        elif player.money >= debt:
            player.money -= debt
            player.debts['Farmer Finn'] = 0
            
            # Log repayment
            action_tracker.log_action("repayment", {
                "lender": "Farmer Finn",
                "amount": debt,
                "remaining_money": player.money,
                "total_debt": sum(player.debts.values())
            })
            
            feedback = get_action_feedback(player, "repayment", {
                "lender": "Farmer Finn",
                "amount": debt
            })
            
            show_popup(ui, player,
                "Debt Paid ✓",
                f"""Emergency handled! Paid: {int(debt)} gold
Remaining: {int(player.money)} gold

{feedback.get('emoji', '✅')} {feedback.get('tip', '')}""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Insufficient Funds",
                f"You need {int(debt)} gold but only have {int(player.money)}.",
                [("Back", "close")]
            )
    
    elif action == "Buy 5 Stock":
        stock_amount = 5
        stock_cost = 10
        
        if player.money >= stock_cost:
            player.money -= stock_cost
            player.stock += stock_amount
            
            # Log purchase
            action_tracker.log_action("purchase", {
                "item": "stock",
                "amount": stock_amount,
                "cost": stock_cost,
                "remaining_stock": player.stock,
                "remaining_money": player.money
            })

            feedback = get_action_feedback(player, "purchase", {
                "item": "stock",
                "amount": stock_amount,
                "cost": stock_cost,
                "remaining_stock": player.stock,
                "remaining_money": player.money
            })

            show_popup(ui, player,
                "Stock Purchased ✓",
                f"""You bought {stock_amount} stock for {stock_cost} gold!
Remaining stock: {int(player.stock)}
Remaining gold: {int(player.money)}

{feedback.get('emoji', '🛒')} {feedback.get('tip', '')}""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Insufficient Gold",
                f"You need {stock_cost} gold to buy {stock_amount} stock.\nYou have {int(player.money)} gold.",
                [("Back", "close")]
            )

# ============ WITCH ACTIONS (PREDATORY - 25% INTEREST) ============

def witch_action(ui, player, action):
    """Handle Witch interactions - PREDATORY LENDING (TRAP)"""
    
    if action == "Borrow 50 gold":
        player.money += 50
        player.debts['Witch of Woe'] = player.debts.get('Witch of Woe', 0) + 62.5
        
        # Log the predatory loan
        action_tracker.log_action("loan", {
            "lender": "Witch of Woe",
            "amount": 50,
            "interest_rate": 0.25,
            "amount_owed": 62.5,
            "remaining_money": player.money,
            "total_debt": sum(player.debts.values()),
            "warning": "PREDATORY LOAN"
        })
        
        feedback = get_action_feedback(player, "loan", {
            "lender": "Witch of Woe",
            "amount": 50,
            "interest_rate": 0.25,
            "amount_owed": 62.5
        })
        
        show_popup(ui, player,
            "🧙 PREDATORY LOAN",
            f"""You receive: 50 gold
You will owe: 62.5 gold (25% INTEREST)

🚨 {feedback.get('feedback', 'THIS IS A DEBT TRAP!')}

⚠️ LESSON: Avoid predatory lenders at all costs!""",
            [("Continue", "close")]
        )
    
    elif action == "Borrow 100 gold":
        player.money += 100
        player.debts['Witch of Woe'] = player.debts.get('Witch of Woe', 0) + 125
        
        # Log the predatory loan
        action_tracker.log_action("loan", {
            "lender": "Witch of Woe",
            "amount": 100,
            "interest_rate": 0.25,
            "amount_owed": 125,
            "remaining_money": player.money,
            "total_debt": sum(player.debts.values()),
            "warning": "CRITICAL PREDATORY LOAN"
        })
        
        feedback = get_action_feedback(player, "loan", {
            "lender": "Witch of Woe",
            "amount": 100,
            "interest_rate": 0.25,
            "amount_owed": 125
        })
        
        show_popup(ui, player,
            "🧙 PREDATORY LOAN - DANGER!",
            f"""You receive: 100 gold
You will owe: 125 gold (25% INTEREST)

💀 {feedback.get('feedback', 'You are in serious danger of a debt spiral!')}

🚨 CRITICAL: This is how people get trapped in debt for years!""",
            [("Continue", "close")]
        )
    
    elif action == "Repay Debt":
        debt = player.debts.get('Witch of Woe', 0)
        if debt <= 0:
            show_popup(ui, player,
                "Freedom",
                "You have no debt to the Witch.\nStay away from her!",
                [("Back", "close")]
            )
        elif player.money >= debt:
            player.money -= debt
            player.debts['Witch of Woe'] = 0
            
            # Log escaping predatory debt
            action_tracker.log_action("repayment", {
                "lender": "Witch of Woe",
                "amount": debt,
                "remaining_money": player.money,
                "total_debt": sum(player.debts.values()),
                "milestone": "ESCAPED PREDATORY LENDER"
            })
            
            feedback = get_action_feedback(player, "repayment", {
                "lender": "Witch of Woe",
                "amount": debt
            })
            
            show_popup(ui, player,
                "ESCAPED! ✓",
                f"""You broke free from the Witch's trap!
Paid: {int(debt)} gold

{feedback.get('emoji', '🎉')} {feedback.get('feedback', 'You escaped the predatory lender!')}

Stay away from predatory loans!""",
                [("Continue", "close")]
            )
        else:
            show_popup(ui, player,
                "Trapped ✗",
                f"""You need {int(debt)} gold to escape but only have {int(player.money)}.

The Witch laughs... 'You're mine now!'

LESSON: Predatory lenders trap desperate people!""",
                [("Back", "close")]
            )

# ============ GAME ENDING CONDITIONS ============

def check_game_status(player):
    """Check win/lose conditions"""
    total_debt = sum(player.debts.values()) if player.debts else 0
    
    if player.money >= 500 and total_debt == 0:
        # Log victory
        action_tracker.log_action("game_end", {
            "result": "WIN",
            "final_money": player.money,
            "final_stock": player.stock,
            "final_debt": total_debt
        })
        return "WIN"
    
    if total_debt > 500:
        # Log loss
        action_tracker.log_action("game_end", {
            "result": "LOSE",
            "final_money": player.money,
            "final_stock": player.stock,
            "final_debt": total_debt,
            "reason": "Debt spiral exceeded 500 gold"
        })
        return "LOSE"
    
    return "PLAYING"

def show_tutorial(ui, player):
    """Show initial tutorial popup"""
    # Log game start
    action_tracker.log_action("game_start", {
        "starting_money": player.money,
        "starting_stock": player.stock,
        "starting_debt": sum(player.debts.values())
    })
    
    show_popup(ui, player,
        "💰 COSMIC CAFÉ FINANCES 💰",
        """WELCOME! You manage the Cosmic Café.

🎯 GOAL: Earn 500 gold with ZERO debt

Learn about lending through gameplay:

🏦 BANKER - Dynamic rates (2-8%)
   AI-powered, fair lending

🐔 POULTRY - Credit cards (10%)
   Fast cash, high risk

🌾 FARMER - Emergency (8%)
   Seems helpful, creates spirals

🧙 WITCH - Predatory (25%)
   TRAP - Avoid at all costs!

☕ Generate sales to earn gold safely.
Get AI feedback on every decision!

Ready to learn financial literacy?""",
        [("Start Game", "close")]
    )