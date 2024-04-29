from typing import List, TypedDict, Literal

class ISource(TypedDict):
    source_type: Literal['facebook_page']
    name: str
    username: str