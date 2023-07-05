from sqlalchemy.orm import Session

from . import models, schemas

def get_history(db: Session, id: int):
    # select * from history where id = id
    return db.query(models.History).filter(models.History.id == id).first()

def get_all_history(db: Session):
    # select * from history
    return db.query(models.History).all()
def create_history(db: Session, history: schemas.History):
    db_history = models.History(query=history.query, result=history.result)
    # insert into history (query, result) values (history.query, history.result)
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history