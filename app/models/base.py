from typing import List
from pydantic import BaseModel
from datetime import datetime


class Base(BaseModel):

    class Config:
        orm_mode = True

class UUIDList(Base):
    id_list: List[str]