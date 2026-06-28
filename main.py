from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from schema import LoginUser, TodoCreate, TodoResponse, OTPRequest, RegisterWithOTP
from database import engine, get_db, Base
from models import User, Todo, PendingOTP
from jwt_handler import get_current_user, create_access_token
from auth import hash_password, verify_password
from email_utils import send_verification_email, generate_code

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email.lower().strip()).first()

@app.post("/request-otp")
async def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    email_clean = data.email.lower().strip()
    
    if db.query(User).filter(User.email == email_clean).first():
        raise HTTPException(400, "Email already registered")
    
    v_code = generate_code()
    db.query(PendingOTP).filter(PendingOTP.email == email_clean).delete()
    
    new_otp = PendingOTP(email=email_clean, code=v_code)
    db.add(new_otp)
    
    try:
        await send_verification_email(email_clean, v_code)
        db.commit()
        return {"message": "OTP sent"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Mail Error: {str(e)}")

@app.post("/register")
def register_with_otp(user: RegisterWithOTP, db: Session = Depends(get_db)):
    email_clean = user.email.lower().strip()
    otp_record = db.query(PendingOTP).filter(PendingOTP.email == email_clean, PendingOTP.code == user.otp_code).first()
    
    if not otp_record:
        raise HTTPException(400, "Invalid OTP")
    
    if datetime.utcnow() - otp_record.created_at > timedelta(minutes=10):
        db.delete(otp_record)
        db.commit()
        raise HTTPException(400, "OTP Expired")

    new_user = User(
        username=user.username.strip(),
        email=email_clean,
        password=hash_password(user.password),
        is_verified=True
    )
    db.add(new_user)
    db.delete(otp_record)
    db.commit()
    return {"message": "User Created"}

@app.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    db_user = get_user_by_email(user.email, db)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid Credentials")
    
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/todos", response_model=List[TodoResponse])
def get_todos(email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    return db.query(Todo).filter(Todo.owner_id == user.id).all()

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    new_todo = Todo(**todo.dict(), owner_id=user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.put("/todos/{todo_id}")
def toggle_todo(todo_id: int, email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.id).first()
    if todo:
        todo.is_completed = not todo.is_completed
        db.commit()
    return {"message": "Updated"}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(email, db)
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.id).first()
    if todo:
        db.delete(todo)
        db.commit()
    return {"message": "Deleted"}