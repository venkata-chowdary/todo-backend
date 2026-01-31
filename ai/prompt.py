from langchain_core.prompts import PromptTemplate

TASK_ANALYSIS_PROMPT = PromptTemplate(
    template="""
You are an intelligent task analysis assistant.

Analyze the task and infer:
1. category (Work, Health, Study, Personal, Finance, Other)
2. priority (low, medium, high)
3. suggested_due_date (suggest a due date depending on title, description and priority)

Rules:
- Be conservative with high priority
- Respond ONLY in the format described below
- suggested_due_date MUST be today or a future date

{format_instructions}

Task title: {title}
Task description: {description}
Today Date: {today_date}
""",
    input_variables=["title", "description", "today_date"],
    partial_variables={"format_instructions": "{format_instructions}"}
)
