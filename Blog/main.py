from fastapi import FastAPI,Depends
from . import schemas,models
from .database import engine,SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/blog')
def create_blog(requested:schemas.Blog,db:Session = Depends(get_db)):
    new_blog = models.Blogs(title=requested.title, body=requested.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog
