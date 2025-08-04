from agents import Agent,Runner,OpenAIChatCompletionsModel,function_tool,enable_verbose_stdout_logging
from openai import AsyncOpenAI
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from dataclasses import dataclass
import os
enable_verbose_stdout_logging()
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY");

client = AsyncOpenAI(
    api_key=google_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


async def main():

    @dataclass
    class User:
        name: str
        is_premium: bool


    @function_tool
    def refund_tool(user:User):
        if user.is_premium == True :
            return {
            "status": "success",
            "refund_id": "RF123456",
            "amount": "$20",
            "message": "Your refund has been issued."
        }
        else:
           return {
            "status": "failed",
            "refund_id": None,
            "amount": "$0",
            "message": "Refund could not be processed. Please check your order ID or try again later."
        }
        

    billing_agent = Agent(
    name="Billing Agent",
    instructions="you are Billing agent",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    )

    technical_agent = Agent[User](
    name="Technical Agent",
    instructions="you are Technical agent",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),


    )

    general_agent = Agent[User](
    name="General Agent",
    instructions="""You are a general assistant that helps users with billing, technical, and general queries...
    if user qurey about refund call function toll refund_tool...
    if user query about technical handoffs to technical_agent...
    if user query about billing handoffs to billing_agent...
    """,
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    handoffs=[technical_agent,billing_agent],
    tools=[refund_tool]
) 



    user_free = User(name="sahil",is_premium=False);
    user_pro = User(name="sheza",is_premium=True)
    prompt = input("Enter your support question below:\n> ")
    result = Runner.run_streamed(general_agent,prompt,context=user_pro);
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            print(event.data.delta,end="",flush=True)
            

if __name__ == "__main__":
    
    asyncio.run(main())