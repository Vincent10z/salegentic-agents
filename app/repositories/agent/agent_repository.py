from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

