from automata.tm.dtm import DTM
from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session

from sql_app.database import engine, SessionLocal
from sql_app import crud, models, schemas

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/get_history/{id}")
async def get_history(id: int, db: Session = Depends(get_db)):
    history = crud.get_history(db=db, id=id)
    if history is None:
        return {
            "code": "404",
            "msg": "not found"
        }
    return history


@app.get("/get_all_history")
async def get_all_history(db: Session = Depends(get_db)):
    history = crud.get_all_history(db=db)
    return history


@app.post("/dtm")
async def dtm(info: Request, db: Session = Depends(get_db)):
    info = await info.json()
    states = set(info.get("states", []))

    if len(states) == 0:
        return {
            "code": "400",
            "msg": "states cannot be empty"
        }
    input_symbols = set(info.get("input_symbols", []))
    if len(input_symbols) == 0:
        return {
            "code": "400",
            "msg": "input_symbols cannot be empty"
        }
    tape_symbols = set(info.get("tape_symbols", []))
    if len(tape_symbols) == 0:
        return {
            "code": "400",
            "msg": "tape_symbols cannot be empty"
        }

    initial_state = info.get("initial_state", "")
    if initial_state == "":
        return {
            "code": "400",
            "msg": "initial_state cannot be empty"
        }
    blank_symbol = info.get("blank_symbol", "")
    if blank_symbol == "":
        return {
            "code": "400",
            "msg": "blank_symbol cannot be empty"
        }
    final_states = set(info.get("final_states", []))
    if len(final_states) == 0:
        return {
            "code": "400",
            "msg": "final_states cannot be empty"
        }
    transitions = dict(info.get("transitions", {}))
    if len(transitions) == 0:
        return {
            "code": "400",
            "msg": "transitions cannot be empty"
        }

    input = info.get("input", "")
    if input == "":
        return {
            "code": "400",
            "msg": "input cannot be empty"
        }

    dtm = DTM(
        states=states,
        input_symbols=input_symbols,
        tape_symbols=tape_symbols,
        transitions=transitions,
        initial_state=initial_state,
        blank_symbol=blank_symbol,
        final_states=final_states,
    )
    if dtm.accepts_input(input):
        print('accepted')
        result = "accepted"
    else:
        print('rejected')
        result = "rejected"

    history = schemas.History(query=str(info), result=result)
    crud.create_history(db=db, history=history)

    return {
        "code": result == "accepted" and "200" or "400",
        "msg": result
    }
