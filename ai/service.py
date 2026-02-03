from app.ai.chains import initialize_chain, nl_chain
from datetime import date

async def analyze_task(title: str, description: str):
    chain=initialize_chain()
    result=await chain.ainvoke({"title": title, "description": description, "today_date": str(date.today())})
    return result

async def parse_nl_todo(user_input:str):
    chain=nl_chain()
    result=await chain.ainvoke({"user_input": user_input})
    return result