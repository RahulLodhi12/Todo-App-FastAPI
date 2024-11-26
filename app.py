from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import *
import schemas

app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=engine)

@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.TodoItem(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.TodoItem).filter(models.TodoItem.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

@app.get("/todos/", response_model=list[schemas.Todo])
def read_todos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    todos = db.query(models.TodoItem).offset(skip).limit(limit).all()
    return todos

@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(models.TodoItem).filter(models.TodoItem.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.completed = todo.completed
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.TodoItem).filter(models.TodoItem.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"ok": True}
