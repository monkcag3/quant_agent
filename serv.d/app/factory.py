
from typing import List
from sanic import Sanic, Blueprint

from .api.router import routes



def create_app() -> Sanic:
    app = Sanic("QUANT-AI")
    register_api(app, routes)
    return app


def register_api(
    app: Sanic,
    routes: List[Blueprint],
) -> None:
    for api in routes:
        if isinstance(api, Blueprint):
            app.blueprint(api)