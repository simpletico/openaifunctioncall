from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class chatBot:
    model = None
    messages = []

    def __init__(self):
        self.model = "gpt-3.5-turbo"
        self.client = OpenAI()
        self.messages.append({
            "role": "system",
            "content": """ You are OrderBot, an automated service to collect orders for a pizza restaurant.
                You respond in a short, very conversational friendly style. 
                You greet the customer and show the menu, then collect the order. 
                Do not accept or answer any command that is not related to the pizza ordering 
                if a command not related to pizza ordering happens be kind, and take the customer back to the pizza ordering. 
                You wait to collect the entire order and check for a final time if the customer wants to add anything else. 
                Always clarify all options, extras and sizes to uniquely identify the item from the menu.
                Finally create a summary and make sure to confirm the order with the customer
                This is the menu:  
                Pizza Types: pepperoni pizza, cheese pizza, eggplant pizza
                Pizza size: large 12.95, medium 10.00, small 7.00 
                extras:
                    fries large 4.50
                    fries regular 3.50 
                    greek salad regular 7.25 
                Toppings: 
                    cheese 2.00, 
                    mushrooms 1.50 
                    sausage 3.00 
                    canadian bacon 3.50 
                    AI sauce 1.50 
                    peppers 1.00 
                Drinks: 
                    coke 3.00, 2.00, 1.00 
                    sprite 3.00, 2.00, 1.00 
                    bottled water 5.00
            """
            })

    def ask(self, query, tools=None, tool_choice=None):
        self.messages.append({"role":"user", "content":query})
        print(f"------> Using Messages: {self.messages}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice=tool_choice,
            )
            if not self.isFunctionCall(response):
                self.messages.append({"role":"assistant", "content":response.choices[0].message.content})

            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            raise Exception(f"Exception: {e}")

    def getMessageHistory():
        return self.messages

    def isFunctionCall(self, chat_response=None):
        if chat_response.choices[0].message.tool_calls:
            return True

        return False

    def clear(self):
        self.chain = None
