from fastapi import FastAPI,Depends,Request,Form,status,Response,HTTPException
from . import schemas,models
from .database import engine,SessionLocal
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
app = FastAPI()

models.Base.metadata.create_all(engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/list',response_class=HTMLResponse)
def get_blogs(request: Request,db:Session = Depends(get_db)):
    n = db.query(models.Blogs).all()
    return templates.TemplateResponse(
        "blogs.html",
        {"request": request, "blogs": n}
    )

@app.get('/create',response_class=HTMLResponse)
def show_form(request:Request):
    return templates.TemplateResponse( "create_blog.html", {"request": request})

@app.post('/create',response_class=HTMLResponse,status_code=status.HTTP_201_CREATED)
def create_blog(request:Request,title:str = Form(...),body:str = Form(...),db:Session = Depends(get_db)):
    new_blog = models.Blogs(title=title, body=body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return templates.TemplateResponse(
        "create_blog.html",
        {
            "request":request,
            "message":"Blog Saved SuccessFully"
        }
    )
@app.post('/delete/{id}',response_class=HTMLResponse)
def delete_blog(request:Request,id:int,db:Session = Depends(get_db)):
    blog = db.query(models.Blogs).filter(models.Blogs.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"The blog {id} not found") #raising a httpexception
    else:
        db.delete(blog)
        db.commit()
        return RedirectResponse(url='/list',status_code=303) #redirect to the same page
    
@app.put('/update/{id}',status_code=status.HTTP_202_ACCEPTED)
def update_blog(request:schemas.Blog,id:int,db:Session = Depends(get_db)): 
    blog = db.query(models.Blogs).filter(models.Blogs.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Blog with{id} not found")
    blog.update(request.dict())
    db.commit()
    return f"The blog with {id} id updated"

