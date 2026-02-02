from app.ai.chains import initialize_chain
from datetime import date

async def analyze_task(title: str, description: str):
    chain=initialize_chain()
    result=await chain.ainvoke({"title": title, "description": description, "today_date": str(date.today())})
    return result