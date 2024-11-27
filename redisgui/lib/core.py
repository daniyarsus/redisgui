from importlib.resources import files

import redis
from fastapi import APIRouter, FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


class RedisGUI:
    def __init__(self, url: str) -> None:
        self.client = redis.from_url(url)

    def insert_record(self, key: str, value: str) -> None:
        self.client.set(key, value)

    def remove_record(self, key: str) -> None:
        self.client.delete(key)

    def get_record(self, key: str) -> str | None:
        value = self.client.get(key)
        return value.decode() if value else None

    def get_all_records(self) -> dict[str, str]:
        keys = list(self.client.scan_iter(match="*"))
        return {key.decode(): self.get_record(key.decode()) for key in keys}


templates_dir = files("redisgui.lib").joinpath("templates")
templates = Jinja2Templates(directory=str(templates_dir))


class RedisGUIController:
    def __init__(self, gui: RedisGUI) -> None:
        self.router = APIRouter()
        self._gui = gui
        self._routes()

    def _routes(self) -> None:
        @self.router.get("/redis")
        async def redis_all_records(request: Request):
            """Displays all records in Redis."""
            records = self._gui.get_all_records()
            return templates.TemplateResponse(
                "redis_select_all_records.html",
                {
                    "request": request,
                    "records": records
                }
            )

        @self.router.get("/redis/insert")
        async def redis_form(request: Request):
            """Renders the page to add a record."""
            return templates.TemplateResponse(
                "redis_insert_record.html",
                {
                    "request": request
                }
            )

        @self.router.post("/redis/insert")
        async def redis_insert(key: str = Form(...), value: str = Form(...)):
            """Inserts a record into Redis."""
            self._gui.insert_record(key, value)
            return RedirectResponse(
                url="/redis",
                status_code=303
            )


def setup_redis_gui(app: FastAPI, gui: RedisGUI) -> None:
    app.include_router(RedisGUIController(gui).router, include_in_schema=False)
