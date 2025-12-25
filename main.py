from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# DATABASE SETUP 
SQLALCHEMY_DATABASE_URL = "sqlite:///./fitness.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DATABASE TABLE 
class WorkoutModel(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    exercise = Column(String)
    reps = Column(Integer)
    weight = Column(Float)
    notes = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

#  Pydantic Validation 
class WorkoutSchema(BaseModel):
    exercise: str
    reps: int
    weight: float
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

#  API SETUP 
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Welcome to the Iron Calculator API"}

#  CRUD 

# 1. CREATE (POST)
@app.post("/workouts", response_model=WorkoutSchema)
def create_workout(workout: WorkoutSchema, db: Session = Depends(get_db)):
    new_workout = WorkoutModel(
        exercise=workout.exercise,
        reps=workout.reps,
        weight=workout.weight,
        notes=workout.notes
    )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    return new_workout

# 2. READ (GET)
@app.get("/workouts", response_model=List[WorkoutSchema])
def get_workouts(db: Session = Depends(get_db)):
    return db.query(WorkoutModel).all()

# 3. READ ONE (GET /id)
@app.get("/workouts/{workout_id}")
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    # Find the workout with this specific ID
    workout = db.query(WorkoutModel).filter(WorkoutModel.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

# 4. UPDATE (PUT)
@app.put("/workouts/{workout_id}")
def update_workout(workout_id: int, workout: WorkoutSchema, db: Session = Depends(get_db)):
    # Find the workout
    db_workout = db.query(WorkoutModel).filter(WorkoutModel.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Update the fields
    db_workout.exercise = workout.exercise
    db_workout.reps = workout.reps
    db_workout.weight = workout.weight
    db_workout.notes = workout.notes
    
    # Save changes
    db.commit()
    return db_workout

# 5. DELETE (DELETE)
@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    # Find the workout
    db_workout = db.query(WorkoutModel).filter(WorkoutModel.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Delete it
    db.delete(db_workout)
    db.commit()
    return {"message": "Workout deleted successfully"}