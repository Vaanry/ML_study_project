from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from database import SessionLocal


class Feed(Base):
    __tablename__ = "feed_action"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("public.user.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("public.post.id"), primary_key=True)
    action = Column(String)
    time = Column(TIMESTAMP)
    # user = relationship("User")
    # post = relationship("Post")


class Post(Base):
    __tablename__ = "post"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)


if __name__ == "__main__":
    session = SessionLocal()
    print([post.id for post in (
        session.query(Post)
        .filter(Post.topic == "business")
        .order_by(Post.id.desc())
        .limit(10)
        .all()
    )])


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    gender = Column(String)
    age = Column(Integer)
    country = Column(String)
    city = Column(String)
    exp_group = Column(Integer)
    os = Column(String)
    source = Column(String)


from sqlalchemy import func

if __name__ == "__main__":
    session = SessionLocal()
    result = [(user.country, user.os, user.count_id) for user in
              (session.query(User.country, User.os, func.count(User.id).label("count_id"))
               .filter(User.exp_group == 3)
               .group_by(User.country,
                         User.os)
               .having(func.count(User.id) > 100)
               .order_by(func.count(User.id).desc())
               )]
    print(result)