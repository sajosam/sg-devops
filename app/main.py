from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
import time
from sqlalchemy.exc import OperationalError


# Retry logic before initializing DB
def wait_for_db():
    max_retries = 10
    retry_delay = 2
    retries = 0

    while retries < max_retries:
        try:
            # Attempt to connect
            models.Base.metadata.create_all(bind=database.engine)
            print("✅ Database connected successfully!")
            return
        except OperationalError:
            print("⏳ Waiting for database to be ready...")
            retries += 1
            time.sleep(retry_delay)

    raise Exception("❌ Could not connect to the database after several retries.")


wait_for_db()
app = FastAPI()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def list_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()