from sqlalchemy import Column, Integer, String
from database import Base


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


from database import SessionLocal
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