# Water Intake Coach

In this project, I built a stateful AI agent to help users track their daily water intake. The agent uses a multi-step ReAct loop and works with the Groq API via the OpenAI SDK.

**Tools:** I implemented four custom tools: `log_water(ml)` to convert units (like glasses or bottles) into milliliters and log intake to today's total, alongside `get_progress()` to check remaining volume against the daily goal. Two additional tools, `get_weekly_average()` and `get_streak()`, compute 7-day intake averages and track consecutive goal-met streaks.

**Memory:** Across the conversation, the agent maintains persistent memory of the day's running water total, a short history of past days, and the full chat history. This stateful tracking means the agent never needs to be reminded of previously logged drinks when answering progress questions several turns later.

**Honest Failure & Resolution:** I initially developed the project using GitHub Models, which was retired mid-development. I then attempted to use Microsoft Foundry, but ran into deprecated model endpoints and free-tier Azure region errors. To resolve this, I migrated to Groq's OpenAI-compatible API. Because I decoupled the model client from the agent loop, tools, and memory, switching providers required changing just three lines of setup code while keeping the rest of the system intact.

