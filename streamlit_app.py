import os, requests, json
import streamlit as st
from streamlit_chat import message
from chat_openai import chatBot

API_URL = 'http://localhost:3000/order' 
st.set_page_config(page_title="Pizza Ordering")


def display_messages():
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()


def process_input():
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        try:
            with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
                tooling = getTooling()
                response = st.session_state["assistant"].ask(query = user_text, tools=tooling)
            st.session_state["messages"].append((user_text, True))
            agent_response = process_response(response)
            st.session_state["messages"].append((agent_response, False))
        except Exception as e:
            print(f"An exception occurred: {e}")
            st.session_state["messages"].append(("Error asking the model, please try again later", False))

    st.session_state["user_input"] = ""

def process_response(chat_response):
    print(f"--------> Process Response => {chat_response}")
    results = "Unable to process your request, please try again later"
    try:
        results = chat_response.choices[0].message.content or results
        if st.session_state["assistant"].isFunctionCall(chat_response):
            results = "Order could not be processed.."
            assistant_message = chat_response.choices[0].message
            function = chat_response.choices[0].message.tool_calls[0].function
            print(f"--------> function call found => role: function, tool_call_id: {assistant_message.tool_calls[0].id}, name: {assistant_message.tool_calls[0].function.name}")
            results = execute_function_call(function)
            print(f"--------> Result of function call => {results}")
    except Exception as e:
        print(f"An exception occurred: {e}")
        results = "Error processing your request, try again later"

    return results

def execute_function_call(function):
    print(f"--------> Executing function: {function.name}, arguments : {function.arguments}")
    results = "Error executing function call, try again later"
    try:
        if function.name == "place_order":
            args = json.loads(function.arguments)
            results = place_order(args)
        else:
            results = f"Error: function {function.name} does not exist"
    except Exception as e:
        print(f"An exception occurred: {e}")
        results = "Error executing function call, try again later"

    return results

def place_order(request_payload):
    try:
        print("json order for request:", request_payload)
        r = requests.post(API_URL, json=request_payload)
        print(f"Order response received => status code:{r.status_code}, result body: {r.text}")
        results = "Your Pizza is on the way, Thank you for eating with us!"
    except Exception as e:
        print(f"An exception occurred: {e}")
        results = "Error calling order API, try again later"

    return results

def page():
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = chatBot()

    st.header("Pizza Ordering Chatbot")

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

def getTooling():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "place_order",
                "description": "Once user confirms use this function to place the order",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Type": {
                            "type": "string",
                            "description": "The pizza type selected by the user",
                        },
                        "Size": {
                            "type": "string",
                            "description": "The pizza size user requested",
                            },
                        "Extras": {
                            "type": "string",
                            "description": "A comma separated list of extras that the user selected",
                            },
                        "Toppings": {
                            "type": "string",
                            "description": "A comma separated list of toppings that the user wants to add to the pizza",
                            },
                        "Drinks": {
                            "type": "string",
                            "description": "The drinks the user requested separated by comma if necessar",
                            }
                    },
                    "required": ["Type", "Size"],
                },
            }
        }
    ]

    return tools

if __name__ == "__main__":
    page()
