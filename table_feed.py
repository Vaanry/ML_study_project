from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Feed(Base):
    __tablename__ = "feed_action"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("public.User.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("public.Post.id"), primary_key=True)
    action = Column(String)
    time = Column(TIMESTAMP)
    user = relationship("User")
    post = relationship("Post")