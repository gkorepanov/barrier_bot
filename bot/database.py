from typing import Optional, Any, Dict, List, Tuple
from bson.objectid import ObjectId

import logging
import pymongo
from datetime import datetime

from bot import config
from bot.handlers import manage_data as md


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-12s :%(name)-30s: %(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)


ChatId = UserId = MessageId = int
NewsletterId = str


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(config.mongodb_uri)
        self.db = self.client["bot"]
        self.user_collection = self.db["user"]
        self.barrier_collection = self.db["barrier"]

    def add_or_update_user(
        self,
        user_id: UserId,
        *,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: Optional[str] = None,
    ):
        user_dict = {
            "_id": user_id,
        }
        if role is not None:
            user_dict["role"] = role
        if username is not None:
            user_dict["username"] = username
        if first_name is not None:
            user_dict["first_name"] = first_name
        if last_name is not None:
            user_dict["last_name"] = last_name

        self.user_collection.update_one(
            {"_id": user_id},
            {"$set": user_dict},
            upsert=True,
        )

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False) -> bool:
        if self.user_collection.count_documents({"_id": user_id}) > 0:
            return True
        else:
            if raise_exception:
                raise ValueError(f"User {user_id} does not exist")
            else:
                return False

    def set_user_attribute(self, user_id: UserId, key: str, value: Any):
        self.check_if_user_exists(user_id, raise_exception=True)
        self.user_collection.update_one({"_id": user_id}, {"$set": {key: value}})

    def get_user_attribute(
        self,
        user_id: int,
        key: str,
        *,
        raise_exception: bool = False,
        default: Optional[Any] = None,
    ) -> Any:
        self.check_if_user_exists(user_id, raise_exception=True)
        user_dict = self.user_collection.find_one({"_id": user_id})
        if key not in user_dict:
            if raise_exception:
                raise KeyError(f"Key {key} does not exist for user {user_id}")
            else:
                return default
        return user_dict[key]

    def get_user_role(
        self,
        user_id: UserId,
    ) -> Optional[md.Role]:
        user = self.user_collection.find_one({"_id": user_id})
        if user is None:
            return None
        if user.get("role") is None:
            return md.Role.BANNED
        return md.Role(user["role"])
    
    def is_user_allowed_to_open_barrier(
        self,
        user_id: UserId,
    ) -> bool:
        user = self.user_collection.find_one({"_id": user_id})
        if user is None or user.get("role") in (None, md.Role.BANNED.value):
            return False
        if user["role"] in (md.Role.ADMIN.value, md.Role.USER.value):
            return True
        return False
    
    def add_barrier(
        self,
        *,
        phone_number: str,
        name: str,
    ) -> ObjectId:
        barrier_dict = {
            "phone_number": phone_number,
            "name": name,
        }
        return self.barrier_collection.insert_one(barrier_dict).inserted_id

    def add_barrier_to_user(
        self,
        *,
        barrier_id: ObjectId,
        user_id: UserId,
    ):
        barriers = self.get_user_attribute(user_id, "barriers", default=[])
        barriers.append(barrier_id)
        barriers = list(dict.fromkeys(barriers))
        db.set_user_attribute(user_id, "barriers", barriers)

    def remove_barrier_from_user(
        self,
        *,
        barrier_id: ObjectId,
        user_id: UserId,
    ):
        barriers = self.get_user_attribute(user_id, "barriers", default=[])
        if barrier_id in barriers:
            barriers = [x for x in barriers if x != barrier_id]
            db.set_user_attribute(user_id, "barriers", barriers)

    def switch_barrier_access_for_user(
        self,
        *,
        barrier_id: ObjectId,
        user_id: UserId,
    ):
        barriers = self.get_user_attribute(user_id, "barriers", default=[])
        if barrier_id in barriers:
            self.remove_barrier_from_user(barrier_id=barrier_id, user_id=user_id)
        else:
            self.add_barrier_to_user(barrier_id=barrier_id, user_id=user_id)

    def get_barriers(
        self,
    ) -> List[Dict[str, Any]]:
        barriers = self.barrier_collection.find()
        return list(barriers)
    
    def get_barrier(
        self,
        barrier_id: ObjectId,
    ) -> Optional[Dict[str, Any]]:
        barrier = self.barrier_collection.find_one({"_id": barrier_id})
        return barrier

db = Database()
