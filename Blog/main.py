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
@app.get('/',response_class=HTMLResponse)
def index(request:Request):
    return templates.TemplateResponse("index.html",{"request":request}) 

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
    return RedirectResponse(url="/list", status_code=303)
@app.post('/delete/{id}',response_class=HTMLResponse)
def delete_blog(request:Request,id:int,db:Session = Depends(get_db)):
    blog = db.query(models.Blogs).filter(models.Blogs.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"The blog {id} not found") #raising a httpexception
    else:
        db.delete(blog)
        db.commit()
        return RedirectResponse(url='/list',status_code=303) #redirect to the same page
    
@app.get('/edit/{id}',response_class=HTMLResponse)
def show_edit(request:Request,id:int,db:Session = Depends(get_db)):
    blog = db.query(models.Blogs).filter(models.Blogs.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No specific blog Found")
    else:
        return templates.TemplateResponse("update.html",{"request":request,"blogs":blog})

@app.post('/update/{id}',status_code=status.HTTP_202_ACCEPTED,response_class=HTMLResponse)
def update_blog(request:Request,id:int,title:str = Form(...),body:str = Form(...),db:Session = Depends(get_db)): 
    update_blog = db.query(models.Blogs).filter(models.Blogs.id == id).first()
    update_blog.title = title
    update_blog.body = body
    db.commit()
    blog = db.query(models.Blogs.id.desc()).all()
    return RedirectResponse(url="/list", status_code=303)

