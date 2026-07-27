from app.db.database import init_database
from app.agent.agent import agent

init_database()

while True:
    text = input("\n你:")
    if text == "exit":
        break
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ]
        })
    print(
        "\nAI:",
        result["messages"][-1].content
    )
