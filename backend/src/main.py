import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.auth.routers import router_auth
from src.users.routers import router_users
from src.chats.routers import router_chats
# from src.messages.routers import router_messages

# from src.admin.auth import authentication_backend
# from src.admin.views import (
# )

app = FastAPI(
    title="diploma-chatbot",
    # root_path="/api/v1",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_CORS_METHODS,
    allow_headers=settings.ALLOWED_CORS_HEADERS,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "API is active"}

# API Routers
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_chats)
# app.include_router(router_messages)

# Admin Panel
# admin = Admin(
#     app,
#     engine,
#     authentication_backend=authentication_backend
# )
# admin.add_view(UserAdmin)
# admin.add_view(ReportAdmin)
# admin.add_view(DepartmentAdmin)
# admin.add_view(RankAdmin)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # if main.py outside /src -> start from /backend directory -> run "python3 main.py", due to 'if __name__ == '__main__':'
    # if main.py inside /src -> start from /backend directory -> run "uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
    # use "--reload" or "reload=True" only when debugging application, but not in production
