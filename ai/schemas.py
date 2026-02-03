from pydantic import BaseModel, Field
from datetime import date

class TaskAIAnalysis(BaseModel):
    category: str = Field(..., description="Category of the task (Work, Health, Study, Personal, Finance, Other)")
    priority: str=Field(..., description="priority of the task (low, medium, high)")
    suggested_due_date:  date = Field (...,description="ISO Date")

class NLTodo(BaseModel):
    title: str = Field(..., description="Title of the todo")
    description: str=Field(..., description="description of the todo")