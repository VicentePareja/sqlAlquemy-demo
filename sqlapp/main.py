from typing import Optional
from fastapi import FastAPI, Request, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from . import models

# Normally you use migrations.
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

templates = Jinja2Templates(directory="sqlapp/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_populate_db():
    db = SessionLocal()
    num_films = db.query(models.Film).count()
    if num_films == 0:
        db.add_all([
            models.Film(name="The Shawshank Redemption", director="Scorsese"),
            models.Film(name="The Godfather", director="Francis Ford Coppola"),
            models.Film(name="The Dark Knight", director="Christopher Nolan"),
            models.Film(name="Pulp Fiction", director="Quentin Tarantino"),
            models.Film(name="Forrest Gump", director="Robert Zemeckis"),
        ])
        db.commit()
    else:
        print(f"Database already populated with {num_films} films.")
    db.close()
    

@app.get("/index/", response_class=HTMLResponse)
async def movielist(request: Request,
                    hx_request: Optional[str] = Header(None),
                    db: Session = Depends(get_db),
                    page: int = 1,
                    ):
    films_per_page = 2
    offset = (page - 1) * films_per_page
    films = db.query(models.Film).offset(offset).limit(films_per_page)
    print(films)
    context = {"request": request, 'films': films, 'page': page}
    if hx_request:
        return templates.TemplateResponse("partials/table.html", context)
    return templates.TemplateResponse("index.html", context)