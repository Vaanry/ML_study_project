from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models import User, Post, Feed
from schema import PostGet, UserGet, FeedGet
from datetime import timedelta
import datetime
from load_model import load_models
from load_features import load_features
import pandas as pd

app = FastAPI()


def get_db():
    with SessionLocal() as db:
        return db


@app.get("/user/{id}", response_model=UserGet)
def get_user(id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == id).all()


@app.get("/post/{id}", response_model=PostGet)
def get_post(id: int, db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.id == id).all()


@app.get("/user/{id}/feed{limit}", response_model=List[FeedGet])
def get_user_feed(id: int, limit=10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.user_id == id).order_by(Feed.time.desc()).limit(limit)


@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_user_feed(id: int, limit=10, db: Session = Depends(get_db)):
    return db.query(Feed).filter(Feed.post_id == id).order_by(Feed.time.desc()).limit(limit)


@app.get("/post/recommendations/", response_model=List[FeedGet])
def post_recommendations(id=None, limit=10, db: Session = Depends(get_db)):
    return db.query(Feed.post_id, Feed.text, Feed.topic, func.count(Feed.post_id).label("count_post")).filter(
        Feed.action == 'like').group_by(Feed.post_id, Feed.text, Feed.topic).order_by(
        func.count(Feed.post_id).desc()).limit(limit)


model = load_models()
user_features = load_features()

@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(
        id: int,
        time: datetime,
        limit: int = 10,
        db: Session = Depends(get_db)) -> List[PostGet]:
    end_time = time + timedelta(hours=1)
    user_info = ['user_id', 'gender', 'age', 'country', 'city', 'os', 'source', 'user_rate']
    X = user_features[(user_features['user_id']==id)]
    Y = user_features[~(user_features['user_id'] == id)]
    Y = Y[(pd.to_datetime(Y['timestamp']) >= time) & (pd.to_datetime(Y['timestamp']) < end_time)]
    Y = Y.drop(['index', 'Unnamed: 0'], axis=1)
    Y = Y.drop(user_info, axis=1)
    Y['user_id'] = id
    for col in user_info:
        Y[col] = X[X['user_id'] == id][col][0]

    Y_train = Y.drop(['index', 'Unnamed: 0', 'user_id', 'post_id', 'exp_group', 'text', 'timestamp'], axis=1)
    Y['prob'] = model.predict_proba(Y_train)[:, 1]
    Y['pred'] = model.predict(Y_train)
    posts = Y[Y['pred'] == 1].sort_values(by='prob', ascending=False)['post_id'][:limit].to_list()
    return db.query(Post.id, Post.text, Post.topic).filter(Post.id.in_(posts)).all()

