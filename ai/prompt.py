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


NATURAL_LANG_PROMPT = PromptTemplate(
    template="""
You are a task parsing assistant.

Your job is to convert a user's natural language input into a structured task.

Extract:
1. title — a short, clear, actionable task title
2. description — an optional expanded description for clarity

Rules:
- The title must be concise and imperative (start with a verb when possible)
- Do NOT invent details that are not present
- If the input is already clear, keep the description short
- Do NOT add dates, priorities, or categories
- Do NOT include explanations or extra text

{format_instructions}

User input:
{user_input}
""",
    input_variables=["user_input"],
    partial_variables={"format_instructions": "{format_instructions}"}
)
