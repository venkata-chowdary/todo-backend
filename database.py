from uuid import UUID
from schemas import Todo

todos_db = [
    Todo(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        title="APIs",
        description="Learn CRUD operations step by step",
        completed=False
    ),
    Todo(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        title="FastAPI",
        description="Study routing and validation basics",
        completed=False
    ),
    Todo(
        id=UUID("33333333-3333-3333-3333-333333333333"),
        title="Setup",
        description="Initialize project structure for todo app",
        completed=False
    ),
    Todo(
        id=UUID("44444444-4444-4444-4444-444444444444"),
        title="CRUD",
        description="Implement create, read, update, delete",
        completed=False
    ),
    Todo(
        id=UUID("55555555-5555-5555-5555-555555555555"),
        title="Docs",
        description="Write Swagger/OAPI documentation",
        completed=False
    ),
    Todo(
        id=UUID("66666666-6666-6666-6666-666666666666"),
        title="Tests",
        description="Test endpoints using Swagger UI",
        completed=True
    ),
    Todo(
        id=UUID("77777777-7777-7777-7777-777777777777"),
        title="UUIDs",
        description="Understand advantages of UUID over int IDs",
        completed=False
    ),
    Todo(
        id=UUID("88888888-8888-8888-8888-888888888888"),
        title="Models",
        description="Refine Pydantic schemas for clarity",
        completed=False
    ),
    Todo(
        id=UUID("99999999-9999-9999-9999-999999999999"),
        title="Config",
        description="Prepare environment settings config",
        completed=False
    ),
    Todo(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        title="Cache",
        description="Plan caching logic with Redis later",
        completed=False
    )
]
