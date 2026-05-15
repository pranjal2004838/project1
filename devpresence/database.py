from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    platform = Column(String)          
    content = Column(Text)             
    content_hash = Column(String)      
    target_url = Column(String)        
    posted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)            
    engagement = Column(JSON, default=dict)          

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True)
    platform = Column(String)
    url = Column(String, unique=True)  
    title = Column(String)
    body = Column(Text)
    author = Column(String)
    found_at = Column(DateTime, default=datetime.utcnow)
    responded = Column(Boolean, default=False)
    response_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    score = Column(Float, default=0.0)              

class DailyLimit(Base):
    __tablename__ = "daily_limits"
    id = Column(Integer, primary_key=True)
    platform = Column(String)
    action = Column(String)            
    count = Column(Integer, default=0)
    date = Column(Date, default=datetime.utcnow().date)

engine = create_engine('sqlite:///devpresence.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()