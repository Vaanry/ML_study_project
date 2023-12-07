from sqlalchemy import Column, Integer, String

from database import Base


class Post(Base):
    __tablename__ = "post"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True)
    text = Column(String)
    topic = Column(String)


from database import SessionLocal

if __name__ == "__main__":
    session = SessionLocal()

    print([post.id for post in (
        session.query(Post)
        .filter(Post.topic == "business")
        .order_by(Post.id.desc())
        .limit(10)
        .all()
    )])