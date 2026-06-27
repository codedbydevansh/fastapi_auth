from fastapi import FastAPI, HTTPException, Depends
from schema import RegisterUser, LoginUser , TodoBase , TodoCreate , TodoResponse , Token # Fixed import name
from database import Base, engine, get_db    # Added get_db and engine
from models import User , Todo
from jwt_handler import get_current_user, create_access_token # Renamed file for clarity
from sqlalchemy.orm import Session
from auth import hash_password, verify_password
from typing  import List

app = FastAPI()

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")


# Helper to get user object from the token email
def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    # 1. Normalize
    email_clean = user.email.lower().strip()
    
    # 2. Check if exists
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(400, "Email already registered")

    # 3. Hash and Save
    hashed = hash_password(user.password)
    new_user = User(
        username=user.username.strip(),
        email=email_clean,
        password=hashed
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Ensure it's fully written
    return {"message": "User Created Successfully"}

@app.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):
    # 1. Normalize
    email_clean = user.email.lower().strip()
    
    # 2. Find User
    db_user = db.query(User).filter(User.email == email_clean).first()

    # --- DEBUG LOGS ---
    print("--- LOGIN ATTEMPT ---")
    print(f"Input Email: {email_clean}")
    
    if not db_user:
        print("RESULT: User NOT found in database")
        raise HTTPException(401, "Invalid Credentials")
    
    print(f"User Found: {db_user.email}")
    print(f"Stored Hash: {db_user.password}")
    
    is_correct = verify_password(user.password, db_user.password)
    print(f"Password Match: {is_correct}")
    # ------------------

    if not is_correct:
        raise HTTPException(401, "Invalid Credentials")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}


 #--- TODO ROUTES ---

@app.get("/todos", response_model=List[TodoResponse])
def get_todos(current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(current_user_email, db)
    return db.query(Todo).filter(Todo.owner_id == user.id).all()

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(current_user_email, db)
    new_todo = Todo(**todo.dict(), owner_id=user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.put("/todos/{todo_id}")
def toggle_todo(todo_id: int, current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(current_user_email, db)
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(404, "Todo not found")
    todo.is_completed = not todo.is_completed
    db.commit()
    return {"message": "Updated"}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(current_user_email, db)
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(404, "Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Deleted"}