import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from api.authrouter import auth_router
from settengs.config import Config

app = FastAPI()
app.include_router(auth_router)
register_tortoise(
    app=app,
    db_url=Config.DB_URL,
    modules={'models': Config.DB_MODELS},
    add_exception_handlers=True,
    generate_schemas=False
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level='info')
