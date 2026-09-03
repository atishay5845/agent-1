
#Setup — Groq client

# !pip install openai

import os
import json
from datetime import date, timedelta
from openai import OpenAI

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "PASTE_YOUR_GROQ_API_KEY_HERE")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

MODEL = "openai/gpt-oss-120b"


# Memory

class Memory:
    def __init__(self, daily_goal_ml=2000):
        self.daily_goal_ml = daily_goal_ml
        self.today = date.today()
        self.today_total_ml = 0
        self.history = {
            self.today - timedelta(days=1): 2100,
            self.today - timedelta(days=2): 1800,
            self.today - timedelta(days=3): 2200,
            self.today - timedelta(days=4): 1500,
            self.today - timedelta(days=5): 2000,
        }
        self.chat_history = []  # persists across turns -> gives the agent memory

memory = Memory(daily_goal_ml=2000)

# Tools
def log_water(ml: float) -> dict:
    """Add ml of water to today's total."""
    memory.today_total_ml += ml
    memory.history[memory.today] = memory.today_total_ml
    return {"added_ml": ml, "today_total_ml": memory.today_total_ml}

def get_progress() -> dict:
    """Return today's progress toward the goal."""
    total = memory.today_total_ml
    goal = memory.daily_goal_ml
    remaining = max(goal - total, 0)
    pct = round(100 * total / goal, 1) if goal else 0
    return {
        "today_total_ml": total,
        "goal_ml": goal,
        "remaining_ml": remaining,
        "percent_complete": pct,
        "goal_met": total >= goal,
    }

def get_weekly_average() -> dict:
    """Average ml logged per day over the last 7 days (including today)."""
    last_7 = [memory.history.get(memory.today - timedelta(days=i), 0) for i in range(7)]
    avg = round(sum(last_7) / 7, 1)
    return {"weekly_average_ml": avg, "days_counted": 7}

def get_streak() -> dict:
    """Number of consecutive days (ending today) the goal was met."""
    streak = 0
    d = memory.today
    while memory.history.get(d, 0) >= memory.daily_goal_ml:
        streak += 1
        d -= timedelta(days=1)
    return {"current_streak_days": streak}

TOOL_FUNCTIONS = {
    "log_water": log_water,
    "get_progress": get_progress,
    "get_weekly_average": get_weekly_average,
    "get_streak": get_streak,
}


# Tool schemas + system prompt

TOOLS = [
    {"type": "function", "function": {
        "name": "log_water",
        "description": "Log that the user drank some water. Convert any unit (glass ~250ml, bottle ~500ml, cup ~240ml) into milliliters before calling.",
        "parameters": {"type": "object", "properties": {"ml": {"type": "number", "description": "Amount of water in milliliters"}}, "required": ["ml"]},
    }},
    {"type": "function", "function": {
        "name": "get_progress",
        "description": "Get today's water intake progress toward the daily goal.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "get_weekly_average",
        "description": "Get the user's average daily water intake over the last 7 days.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "get_streak",
        "description": "Get the user's current streak of consecutive days meeting the water goal.",
        "parameters": {"type": "object", "properties": {}},
    }},
]

SYSTEM_PROMPT = (
    "You are a friendly water intake coach. The user's daily goal is stored in the system "
    "(use get_progress to check it, never assume a number). When the user mentions drinking "
    "water, log it first, THEN check progress, THEN reply with an encouraging, specific nudge "
    "(e.g. how much is left, or congratulate them if the goal is met). If asked about weekly "
    "habits or streaks, use those tools too. Always base your numbers on tool results, never "
    "guess. Keep replies short and warm."
)

# The agent loop (plan → act → observe → repeat)

def agent_turn(user_message: str, max_steps: int = 5) -> str:
    memory.chat_history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + memory.chat_history

    for step in range(max_steps):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})
            for call in msg.tool_calls:
                fn_name = call.function.name
                fn_args = json.loads(call.function.arguments or "{}")
                print(f"  [agent step {step+1}] calling {fn_name}({fn_args})")
                result = TOOL_FUNCTIONS[fn_name](**fn_args)
                print(f"  [agent step {step+1}] result: {result}")
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
            continue
        else:
            final_text = msg.content
            memory.chat_history.append({"role": "assistant", "content": final_text})
            return final_text

    return "(stopped: too many steps)"

# Demo — run this and keep the printed output in your notebook
print("USER: I just drank a bottle of water")
print("AGENT:", agent_turn("I just drank a bottle of water"))
print()

print("USER: had another glass too")
print("AGENT:", agent_turn("had another glass too"))
print()

print("USER: how am I doing today, and what's my weekly average?")
print("AGENT:", agent_turn("how am I doing today, and what's my weekly average?"))
print()

print("USER: am I on a streak?")
print("AGENT:", agent_turn("am I on a streak?"))

