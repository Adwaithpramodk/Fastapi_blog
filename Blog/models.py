from sqlalchemy import Column,Integer,String,Text
from .database import Base

class Blogs(Base):

    __tablename__ = 'blogs'

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String(200))
    body = Column(Text)

