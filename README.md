# Water Intake Coach — Agent Project 

Tools: `log_water(ml)` logs how much water the user drank and updates today's running total. `get_progress()` checks that total against the daily goal and returns how much is left and whether the goal is met. Two additional tools support the group add-on: `get_weekly_average()` and `get_streak()`, which compute a 7-day average and the current goal-met streak from logged history.

Memory: The agent keeps two things across the whole conversation: the day's running water total (plus a short history of past days, used for the weekly average and streak), and the full chat history. This means the agent never has to be reminded what's already been logged — if a user logs a drink and asks about their progress three turns later, it still has the real numbers, not a guess.

One honest failure and how I handled it: We originally built this on GitHub Models, but GitHub fully retired that service partway through the project. We switched to Microsoft Foundry next, but ran into deprecated models and Azure region/subscription errors we couldn't resolve on a free tier. We moved to Groq, which is free with no card and fully OpenAI-SDK-compatible, so only the client setup (three lines) had to change — the tools, memory, and agent loop were untouched. This taught us to keep the model-calling code separate from the agent logic so a provider swap stays small.

