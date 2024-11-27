from fastapi import FastAPI
from redisgui import RedisGUI, setup_redis_gui

app = FastAPI()


gui = RedisGUI(url="redis://localhost:6379/0")
setup_redis_gui(app, gui)
