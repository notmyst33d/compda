import os
import json
import asyncio
import bbcode
import bbpda
from dataclasses import dataclass
from aiohttp import ClientSession
from aiohttp.web import _run_app, Application, Request, Response, RouteTableDef

with open("template.html", "r") as file:
    _template = file.read()

with open("post.frag.html", "r") as file:
    _post_fragment = file.read()

routes = RouteTableDef()

@dataclass
class GetTopicRequest:
    topic_id: int
    page_st: int = 0
    count: int = 20

    def encode(self):
        return json.dumps([
            0,
            "fr",
            self.topic_id,
            self.page_st,
            self.count,
            0,
        ]).encode("CP1251")

@dataclass
class Post:
    id: int
    author_name: str
    timestamp: int
    text: str
    author_profile_picture: str

    @staticmethod
    def decode_json(data):
        post_id = data[0]
        #data[1] unknown
        author_name = data[2]
        #data[3] unknown
        #data[4] unknown
        timestamp = data[5]
        text = data[6]
        author_profile_picture = data[7]
        attachments = data[8]
        return Post(
            id=post_id,
            author_name=author_name,
            timestamp=timestamp,
            text=text,
            author_profile_picture=author_profile_picture,
        )

@dataclass
class Topic:
    id: int
    name: str
    author_id: int
    author_name: int
    posts: list[Post]

    @staticmethod
    def decode(data):
        jdata = json.loads(data.decode("CP1251"))
        #jdata[0] unknown
        #jdata[1] unknown
        #jdata[2] topic_tree
        topic_id = jdata[3]
        topic_name = jdata[4]
        #jdata[5] unknown
        #jdata[6] unknown
        #jdata[7] unknown
        author_id = jdata[8]
        author_name = jdata[9]
        #jdata[10] unknown
        #jdata[11] unknown
        #jdata[12] unknown
        #jdata[13] unknown
        posts = [Post.decode_json(entry) for entry in jdata[14]]
        return Topic(
            id=topic_id,
            name=topic_name,
            author_id=author_id,
            author_name=author_name,
            posts=posts,
        )

@routes.get("/forum/index.php")
async def get_index_php(request: Request):
    # TODO: This doesnt work as intended
    if request.app["ws"].closed:
        print("Refresh")
        request.app["ws"] = await request.app["session"].ws_connect("wss://appbk.4pda.to/ws/")

    if (showtopic := request.query.get("showtopic")):
        return await get_showtopic(request)

async def get_showtopic(request: Request):
    topic_id = int(request.query["showtopic"])
    page_st = 0
    try:
        page_st = int(request.query["st"])
    except:
        pass

    await request.app["ws"].send_bytes(GetTopicRequest(topic_id, page_st).encode())
    msg = await request.app["ws"].receive()

    template = _template
    topic = Topic.decode(msg.data)
    posts_composite = ""

    def render_size(tag_name, value, options, parent, context):
        # TODO: More sizes
        sizes = {
            3: "24px",
            4: "32px",
        }
        size = sizes.get(options["size"], "16px")
        return f"<span style=\"font-size: {size};\">{value}</span>"

    for post in topic.posts:
        parser = bbcode.Parser()

        #
        # HACK:
        # Posts can contain spoilers with colored titles,
        # this removes the processing of [color] tags.
        # Instead, [color] tag (along with [spoiler]) is being processed in bbpda library.
        #
        del parser.recognized_tags["color"]

        parser.add_formatter("size", render_size)
        postprocessed = bbpda.render(parser.format(post.text))
        # TODO: This is extremely broken
        #postprocessed = postprocessed.replace("https://4pda.ru", "http://localhost:10000")
        #postprocessed = postprocessed.replace("http://4pda.ru", "http://localhost:10000")
        #postprocessed = postprocessed.replace("https://4pda.to", "http://localhost:10000")
        #postprocessed = postprocessed.replace("http://4pda.to", "http://localhost:10000")

        fragment = _post_fragment
        fragment = fragment.replace("[TEXT]", postprocessed)
        fragment = fragment.replace("[AUTHOR_PROFILE_PICTURE]", post.author_profile_picture)
        fragment = fragment.replace("[AUTHOR_NAME]", post.author_name)
        posts_composite += fragment

    template = template.replace("[POSTS]", posts_composite)

    return Response(text=template, content_type="text/html")

@routes.get("/fonts/{tail:.*}")
async def get_fonts(request):
    if not os.path.isfile(f"fonts/{request.match_info['tail']}"):
        return Response(status=404)
    with open(f"fonts/{request.match_info['tail']}", "rb") as file:
        return Response(body=file.read())

async def main():
    app = Application()
    app["session"] = ClientSession()
    app["ws"] = await app["session"].ws_connect("wss://appbk.4pda.to/ws/")

    app.add_routes(routes)
    await _run_app(app, port=10000)

asyncio.run(main())
