import os
import json
import asyncio
import bbcode
from datetime import datetime
from dataclasses import dataclass
from aiohttp import ClientSession
from aiohttp.web import _run_app, Application, Request, Response, RouteTableDef
from jinja2 import Environment, PackageLoader

from . import bbpda
from .requests import *
from .data import *
from .bbparser import get_bbcode_parser

routes = RouteTableDef()

@routes.get("/forum/index.php")
async def get_index_php(request: Request):
    if (showtopic := request.query.get("showtopic")):
        return await get_showtopic(request)
    else:
        return Response(text="Это альтернативный фронтенд 4PDA")

async def get_showtopic(request: Request):
    topic_id = int(request.query["showtopic"])
    page_st = int(request.query.get("st", "0"))

    ws = await request.app["session"].ws_connect("wss://appbk.4pda.to/ws/")

    if request.query.get("view") == "findpost":
        post_little = await get_post_little(ws, request.query["p"])
        page_st = post_little.page_st

    parser = get_bbcode_parser(request, topic_id)
    topic = await get_topic(ws, topic_id, page_st)
    posts = []
    for post in topic.posts:
        attachments = await get_attachments(ws, post.attachments)
        text = bbpda.render(parser.format(post.text), attachments)
        port_str = ""
        if request.url.port:
            port_str = f":{request.url.port}"
        text = text.replace(
            "https://4pda.to/forum/index.php?showtopic=",
            f"{request.url.scheme}://{request.url.host}{port_str}/forum/index.php?showtopic=",
        )
        text = text.replace(
            "http://4pda.to/forum/index.php?showtopic=",
            f"{request.url.scheme}://{request.url.host}{port_str}/forum/index.php?showtopic=",
        )
        posts.append({
            "id": post.id,
            "author_name": post.author_name,
            "author_profile_picture": post.author_profile_picture,
            "time": datetime.fromtimestamp(post.timestamp).strftime("%d.%m.%y %H:%M"),
            "text": text,
        })

    next_page = request.url.update_query({"st": page_st + 20})
    previous_page = request.url.update_query({"st": max(page_st - 20, 0)})
    html = request.app["jinja"].get_template("topic.html").render(
        posts=posts,
        next_page=next_page,
        previous_page=previous_page,
    )

    return Response(text=html, content_type="text/html")

async def main():
    app = Application()
    app["jinja"] = Environment(loader=PackageLoader(__name__))
    app["session"] = ClientSession()

    app.add_routes(routes)
    app.router.add_static("/fonts", "fonts")
    await _run_app(app, port=10000)

asyncio.run(main())
