import json
from dataclasses import dataclass
from .data import *

@dataclass
class GetTopicRequest:
    topic_id: int
    page_st: int = 0

    def encode(self):
        return json.dumps([0, "fr", self.topic_id, self.page_st, 20, 0]).encode("CP1251")

@dataclass
class GetPostLittleRequest:
    post_id: int

    def encode(self):
        return json.dumps([0, "fj", 3, self.post_id, -1, 0]).encode("CP1251")

@dataclass
class GetAttachmentRequest:
    file_id: int

    def encode(self):
        return json.dumps([0, "fa", self.file_id]).encode("CP1251")

async def get_post_little(ws, post_id: int) -> PostLittle:
    await ws.send_bytes(GetPostLittleRequest(post_id).encode())
    msg = await ws.receive()
    return PostLittle.decode(msg.data)

async def get_topic(ws, topic_id: int, page_st: int) -> Topic:
    await ws.send_bytes(GetTopicRequest(topic_id, page_st).encode())
    msg = await ws.receive()
    return Topic.decode(msg.data)

async def get_attachments(ws, attachments: List[Attachment]) -> dict[int, str]:
    output = {}
    for attachment in attachments:
        if attachment.type == AttachmentType.IMAGE:
            await ws.send_bytes(GetAttachmentRequest(attachment.id).encode())
            msg = await ws.receive()
            data = json.loads(msg.data.decode("CP1251"))
            attachment.url = data[2]
        output[attachment.id] = attachment
    return output

