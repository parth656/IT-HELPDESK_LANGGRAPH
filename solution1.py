import os
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import START, END, StateGraph

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# TODO: add all five categories from the assignmen
HELP_DESK_DATA = {
    "network": {
        "keywords": ["wifi not working", "no internet", "network down"],
        "priority": "high",
        "reply_guidance": "Acknowledge the outage and state that the network team will investigate.",
        "team": "network team",
    },
    "software": {
        "keywords": ["application crash", "software error", "app not opening"],
        "priority": "medium",
        "reply_guidance": "Acknowledge the software issue and ask the user to share the error message.",
        "team": "application support team",
    },
    "hardware": {
        "keywords": [
            "laptop not starting",
            "keyboard not working",
            "screen flickering",
        ],
        "priority": "medium",
        "reply_guidance": "Acknowledge the hardware problem and explain that a device check will be arranged.",
        "team": "hardware support team",
    },
    "security": {
        "keywords": ["suspicious email", "account hacked", "malware detected"],
        "priority": "critical",
        "reply_guidance": "Tell the user not to interact further and mention immediate security escalation.",
        "team": "security team",
    },
    "general": {
        "keywords": [],
        "priority": "low",
        "reply_guidance": "Acknowledge the request and provide a clear next step.",
        "team": "IT helpdesk",
    },
}


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", temperature=0, api_key=api_key
    )


class HelpdeskState(TypedDict):
    # TODO: add all required state keys and types
    ticket: str
    category: str
    priority: str
    assigned_team: str
    reply: str
    validation_status: str
    review_notes: str
    revision_count: int


def classify_state(state: HelpdeskState):
    ticket = state["ticket"].lower()
    for category, data in HELP_DESK_DATA.items():
        for keyword in data["keywords"]:
            if ticket in keyword:
                return {
                    "category": category,
                    "priority": data["priority"],
                    "assigned_team": data["team"],
                }
    return {"category": "IT", "priority": "low", "assigned_team": "IT Helpdesk"}


def validate_reply(state: HelpdeskState):
    if len(state["reply"]) > 90:
        return {
            "status": "improved",
            "review_notes": "Keep the response within 90 words",
        }
    if state["priority"] == "crictical" or "security team" not in state["reply"]:
        return {
            "status": "improved",
            "review_notes": "Mention immediately to the security team",
        }
    words = ["will", "please", "next", "team", "check", "investigate"]
    if not any(word in state["reply"] for word in words):
        return {
            "status": "improved",
            "review_notes": "Add one clear next action for the employee.",
        }
    return {"status": "accepted", "review_notes": ""}


def improve_reply(state: HelpdeskState):
    llm = get_llm()
    prompt = f"""
    
    You have given {state['reply']} You have to improve acc  to {state["review_notes"]}"""
    response = llm.invoke(prompt)
    return {
        "reply": response.content[0][-1],
        "revision_count": state["revision_count"] + 1,
    }


def route_after_validation(state: HelpdeskState):
    if state["validation_status"] == "improve" and state["revision_count"] < 1:
        return "improved"
    else:
        return "finished"


def build_graph():
    builder = StateGraph(HelpdeskState)
    builder.add_node("classify_state", classify_state)
    builder.add_node("validate_reply", validate_reply)
    builder.add_node("improve_reply", improve_reply)
    builder.add_edge(START, "classify_state")
    builder.add_edge("classify_state", "validate_reply")
    builder.add_conditional_edges(
        "validate_reply",
        route_after_validation,
        {
            "improved": "improve_reply",
            "finished": END,
        },
    )
    builder.add_edge("improve_reply", END)
    return builder.compile()


def main():
    app = build_graph()
    ticket = input("Enter your problem: ")
    initial_state = {
        "ticket": ticket,
        "category": "",
        "priority": "",
        "assigned_team": "",
        "reply": "",
        "validation_status": "",
        "review_notes": "",
        "revision_count": "",
    }
    response = app.invoke(initial_state)
    print(response)


if __name__ == "__main__":
    main()
