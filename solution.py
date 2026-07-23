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


def get_llm():
    """Return the llm of gemini model"""
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite", temperature=0, api_key=api_key
    )


def classify_ticket(state: HelpdeskState):
    ticket = state["ticket"].lower()
    for category, data in HELP_DESK_DATA.items():
        for keyword in data["keywords"]:
            if ticket in keyword:
                return {
                    "category": category,
                    "priority": data["priority"],
                    "assigned_item": data["team"],
                }
    return {"category": "general", "priority": "low", "assigned_item": "IT Helpdesk"}


def create_reply(state: HelpdeskState):
    # TODO: create an LLM prompt and return reply
    llm = get_llm()
    prompt = f"""
    You are an IT helpdesk assisstant
    Ticket : {state['ticket']}
    Category :{state['category']}
    Priority : {state['priority']}
    Assigned Item : {state['assigned_team']}
    Guidance: {HELP_DESK_DATA[state['category']]["reply_guidance"]}
    Write a poilte reply under 90 words 
    Include a clear next step and if priority is critical mention the words security team
    """
    response = llm.invoke(prompt)
    return {"reply": response.content[0]["text"]}


def validate_reply(state: HelpdeskState):
    # TODO: check word count, critical escalation, and next action
    if len(state["reply"].split()) > 90:
        {"validation_status": "Improved", "reply": "Keep the response withoin 90 words"}
    if state["priority"] == "crictical" or "security team" not in state["reply"]:
        {
            "validation_status": "Improved",
            "review_notes": "Mention Immediately to security team",
        }
    words = ["will", "please", "next", "team", "check", "investigate"]
    if not any(word in state["reply"].lower().split() for word in words):
        {
            "validation_status": "Improved",
            "review_notes": "Add one clear next action for the employee.",
        }
    return {"validation_status": "Accepted", "review_notes": ""}


def improve_reply(state: HelpdeskState):
    # TODO: rewrite using review_notes and increment revision_count
    pass


def route_after_validation(state: HelpdeskState):
    if state["validation_status"] == "improved":
        return "need_improve"
    else:
        return "end"


def build_graph():
    graph = StateGraph(HelpdeskState)
    graph.add_node("classify_ticket", classify_ticket)
    graph.add_node("create_reply", create_reply)
    graph.add_node("validate_reply", validate_reply)

    graph.add_edge(START, "classify_ticket")
    graph.add_edge("classify_ticket", "create_reply")
    graph.add_edge("create_reply", "validate_reply")
    graph.add_conditional_edges(
        "validate_reply",
        route_after_validation,
        {
            "need_improve": "improve_reply",
            "end": END
        },
    )
    graph.add_edge("validate_reply", END)

    # TODO: add four nodes
    # TODO: add START and fixed edges
    # TODO: add conditional edges after validate
    # TODO: connect improve back to validate

    return graph.compile()


def main():
    app = build_graph()
    user_input = input("Enyter concern")
    initial_state = {
        "ticket": user_input,
        "category": "",
        "priority": "",
        "assigned_team": "",
        "reply": "",
        "validation_status": "",
        "review_notes": "",
        "revision_count": 0,
    }
    final_state = app.invoke(initial_state)
    print(final_state)

    # TODO: create the complete initial state
    # TODO: invoke the graph
    # TODO: print all required final values


if __name__ == "__main__":
    main()
