"""
Action Tracker - Records all player actions with timestamps and context
"""
import json
import time
from datetime import datetime

class ActionTracker:
    def __init__(self):
        self.actions = []
        self.session_start = time.time()
    
    def log_action(self, action_type, details):
        """
        Log a player action with full context
        
        Args:
            action_type: Type of action (loan, sale, repayment, etc.)
            details: Dictionary with action-specific details
        """
        action_entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": action_type,
            "details": details
        }
        self.actions.append(action_entry)
        return action_entry
    
    def get_recent_actions(self, count=5):
        """Get the most recent N actions"""
        return self.actions[-count:] if len(self.actions) >= count else self.actions
    
    def get_action_summary(self):
        """Get summary statistics of all actions"""
        summary = {
            "total_actions": len(self.actions),
            "loans_taken": 0,
            "sales_made": 0,
            "repayments_made": 0,
            "total_borrowed": 0,
            "total_earned": 0,
            "total_repaid": 0
        }
        
        for action in self.actions:
            action_type = action["action_type"]
            details = action["details"]
            
            if action_type == "loan":
                summary["loans_taken"] += 1
                summary["total_borrowed"] += details.get("amount", 0)
            elif action_type == "sale":
                summary["sales_made"] += 1
                summary["total_earned"] += details.get("amount", 0)
            elif action_type == "repayment":
                summary["repayments_made"] += 1
                summary["total_repaid"] += details.get("amount", 0)
        
        return summary
    
    def get_lender_history(self, lender_name):
        """Get all interactions with a specific lender"""
        return [
            action for action in self.actions
            if action["details"].get("lender") == lender_name
        ]
    
    def export_to_json(self, filename="player_actions.json"):
        """Export all actions to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                "session_start": self.session_start,
                "actions": self.actions,
                "summary": self.get_action_summary()
            }, f, indent=2)
    
    def get_formatted_history(self, count=10):
        """Get formatted string of recent actions for AI prompts"""
        recent = self.get_recent_actions(count)
        formatted = []
        
        for action in recent:
            action_type = action["action_type"]
            details = action["details"]
            time_str = action["datetime"]
            
            if action_type == "loan":
                formatted.append(
                    f"{time_str}: Borrowed {details['amount']} gold from {details['lender']} "
                    f"at {details['interest_rate']*100}% interest (will owe {details['amount_owed']} gold)"
                )
            elif action_type == "sale":
                formatted.append(
                    f"{time_str}: Made sale for {details['amount']} gold (stock used: {details['stock_used']})"
                )
            elif action_type == "repayment":
                formatted.append(
                    f"{time_str}: Repaid {details['amount']} gold to {details['lender']}"
                )
        
        return "\n".join(formatted) if formatted else "No actions yet"

# Global tracker instance
action_tracker = ActionTracker()