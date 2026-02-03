from langchain_core.runnables import RunnableSequence
from app.ai.prompt import TASK_ANALYSIS_PROMPT, NATURAL_LANG_PROMPT
from app.ai.llm import get_llm
from langchain_core.output_parsers import PydanticOutputParser
from app.ai.schemas import TaskAIAnalysis, NLTodo


parser_ai_analysis=PydanticOutputParser(pydantic_object=TaskAIAnalysis)
parser_nl=PydanticOutputParser(pydantic_object=NLTodo)

def initialize_chain():
    
    llm=get_llm()
    prompt = TASK_ANALYSIS_PROMPT.partial(
        format_instructions=parser_ai_analysis.get_format_instructions()
    )

    chain = prompt | llm | parser_ai_analysis
    return chain

def nl_chain():
    llm=get_llm()
    prompt=NATURAL_LANG_PROMPT.partial(
        format_instructions=parser_nl.get_format_instructions()
    )
    chain=prompt | llm | parser_nl
    return chain