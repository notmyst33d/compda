import json
from enum import Enum
from dataclasses import dataclass
from typing import Self, List

class AttachmentType(Enum):
    FILE = 0
    IMAGE = 1

@dataclass
class Attachment:
    id: int
    type: AttachmentType
    url: str
    file_id: int

    @staticmethod
    def decode_list(data: list) -> Self:
        return Attachment(id=data[0], type=AttachmentType(data[1]), url=data[2], file_id=data[3])

@dataclass
class Post:
    id: int
    author_name: str
    author_profile_picture: str
    timestamp: int
    text: str
    attachments: List[Attachment]

    @staticmethod
    def decode_list(data: list) -> Self:
        return Post(
            id=data[0],
            author_name=data[2],
            author_profile_picture=data[7],
            timestamp=data[5],
            text=data[6],
            attachments=[Attachment.decode_list(e) for e in data[8]],
        )

@dataclass
class Topic:
    posts: List[Post]

    @staticmethod
    def decode(data: bytes) -> Self:
        data = json.loads(data.decode("CP1251"))
        return Topic(posts=[Post.decode_list(e) for e in data[14]])

@dataclass
class PostLittle:
    page_st: int

    @staticmethod
    def decode(data: bytes) -> Self:
        data = json.loads(data.decode("CP1251"))
        return PostLittle(page_st=data[3])
