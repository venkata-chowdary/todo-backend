from langchain_core.runnables import RunnableSequence
from app.ai.prompt import TASK_ANALYSIS_PROMPT
from app.ai.llm import get_llm
from langchain_core.output_parsers import PydanticOutputParser
from app.ai.schemas import TaskAIAnalysis


parser=PydanticOutputParser(pydantic_object=TaskAIAnalysis)

llm=get_llm()
def initialize_chain():
    prompt = TASK_ANALYSIS_PROMPT.partial(
        format_instructions=parser.get_format_instructions()
    )

    chain = prompt | llm | parser
    return chain
