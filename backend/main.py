from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import uvicorn

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./crypto_whack.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserScore(Base):
    __tablename__ = "scores"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    high_score = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScoreUpdate(BaseModel):
    user_id: int
    username: str
    score: int

@app.get("/")
def read_root():
    return {"status": "Crypto-Whack Backend Online"}

@app.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):
    scores = db.query(UserScore).order_by(UserScore.high_score.desc()).limit(10).all()
    return [{"username": s.username, "score": s.high_score} for s in scores]

@app.post("/update_score")
def update_score(update: ScoreUpdate, db: Session = Depends(get_db)):
    user = db.query(UserScore).filter(UserScore.user_id == update.user_id).first()
    
    if user:
        if update.score > user.high_score:
            user.high_score = update.score
            db.commit()
            db.refresh(user)
    else:
        user = UserScore(user_id=update.user_id, username=update.username, high_score=update.score)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    return {"status": "success", "high_score": user.high_score}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
