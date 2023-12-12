from fastapi import Depends, FastAPI
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models import User, Post, Feed
from schema import PostGet, UserGet, FeedGet, Response
from datetime import timedelta
import datetime
from load_model import load_models
from load_features import load_features
from get_recommendation import get_exp_group, model_control, model_test, get_recomendation
from loguru import logger

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


control_model = load_models('catboost_model')
test_model = load_models('new_catboost_model')

user_features = load_features(user_features)
user_features_2 = load_features(user_features_2)

'''В endpoint-е для построения рекомендаций используйте функцию для определения группы пользователя, в соответствии с этим вызывайте нужную функцию для построение рекомендаций, логируйте, какая модель применялась (на практике часто опираются на эти логи при обсчёта A/B экспериментов). Не забудь в ответе endpoint-а указать группу, в которую попал пользователь ("control" или "test").'''

@app.get("/post/recommendations/", response_model=Response)
def recommended_posts(
        id: int,
        time: datetime,
        limit: int = 10,
        db: Session = Depends(get_db)) -> List[PostGet]:
    exp_group = get_exp_group(id)
    
    logger.info(f"user_id: {id}")
    logger.info(f"exp_group: {exp_group}")
    
    if exp_group == 'control':
        recommendations = model_control(id, time, limit)
    elif exp_group == 'test':
        recommendations = model_test(id, time, limit)
    else:
        raise ValueError('unknown group')
    logger.info(recommendations)
    return db.query(Post.id, Post.text, Post.topic).filter(Post.id.in_(recommendations)).all()


