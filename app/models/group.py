from uuid import UUID
from typing import Optional, Union, List

from .base import Base, UUIDList
from .permission import PermissionInDB

class Group(Base):
    name: str
    description: str
    environment_id: UUID = None

class GroupInDB(Group):
    id: Union[UUID,str]
    
class GroupCreate(Group):
    pass

class GroupUpdate(GroupInDB):
    pass

class GroupId(Base):
    id: Union[UUID,str]

class GroupBulk(Base):
    group_data: GroupCreate
    list_permissions: Union[List[UUID],None]

class GroupPermissionSchema(Base):
    group: UUID
    permissions_id: List[UUID]

class GroupList(Base):
    group: GroupInDB
    permissions: List[PermissionInDB]

class GroupListInfo(Base):
    group: GroupInDB
    #permissions: List[PermissionInDB] = None

class GroupUpdate(Base):
    name: Optional[str]
    description: Optional[str]

class GroupUpdateList(Base):
    group: Optional[GroupUpdate]
