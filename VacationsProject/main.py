from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models import VacationCreate, Vacation, VacationModel
from crud import create_vacation, delete_vacation, read_latest_vacations, read_vacations_by_date, read_latest_ten_vacations  # read_vacation
from database import SessionLocal
from typing import List
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

# Инициализация приложения FastAPI
app = FastAPI()

# Включение CORS для разрешения всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Функция зависимости для получения экземпляра сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинт для создания нового отпуска
@app.post("/vacations/VacationCreate", response_model=Vacation)
def add_vacation(employee_id: int, start_date: str, end_date: str, db: Session = Depends(get_db)):

    try:
        if employee_id < 0:
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=404, detail="ID сотрудника должен быть больше или равен нулю")

    try:
        start_date_converted = date.fromisoformat(start_date)
        end_date_converted = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Дата должна быть в формате (гггг-мм-дд)")

    if start_date_converted >= end_date_converted:
        raise HTTPException(status_code=400, detail="Дата начала должна быть меньше даты окончания")

    vacation_data = VacationCreate(employee_id=employee_id, start_date=start_date_converted, end_date=end_date_converted)
    created_vacation_id = create_vacation(db, vacation_data)
    return {"employee_id": employee_id, "start_date": start_date_converted, "end_date": end_date_converted, "id": created_vacation_id}


# Эндпоинт для получения трех последних добавленных отпусков для определенного сотрудника
@app.get("/vacations/read_latest_vacations/{employee_id}", response_model=List[Vacation])
def get_latest_vacations(employee_id: int, db: Session = Depends(get_db)):
    try:
        if not isinstance(employee_id, int) or employee_id < 0:
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=400, detail="ID сотрудника должен быть целым неотрицательным числом")

    db_vacations = read_latest_vacations(db, employee_id)

    if not db_vacations:
        raise HTTPException(status_code=404, detail="Отпусков для данного сотрудника не найдено")
    return db_vacations

# Эндпоинт для получения последних 10 добавленных отпусков (нет в техническом задании, реализовано на всякий случай)
@app.get("/vacations/read_latest_ten_vacations", response_model=List[Vacation])
def get_latest_ten_vacations(db: Session = Depends(get_db)):
    db_vacations = read_latest_ten_vacations(db)

    if not db_vacations:
        raise HTTPException(status_code=404, detail="Отпусков не найдено")
    return db_vacations


# Эндпоинт для получения списка отпусков в заданном диапазоне дат
@app.get("/vacations/read_vacations_by_date", response_model=List[Vacation])
def get_vacations_by_date(start_date: str = Query(...), end_date: str = Query(...), db: Session = Depends(get_db)):

    try:
        start_date_converted = date.fromisoformat(start_date)
        end_date_converted = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Дата должна быть в формате (гггг-мм-дд)")

    if start_date_converted >= end_date_converted:
        raise HTTPException(status_code=400, detail="Дата начала должна быть меньше даты окончания")

    db_vacations = read_vacations_by_date(db, start_date_converted, end_date_converted)
    if not db_vacations:
        raise HTTPException(status_code=404, detail="Не найдено ни одного отпуска за указанный период")
    return db_vacations

# Эндпоинт для удаления отпуска по его ID
@app.delete("/vacations/delete/{vacation_id}")
def remove_vacation(vacation_id: int, db: Session = Depends(get_db)):

    try:
        if not isinstance(vacation_id, int) or vacation_id < 0:
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=400, detail="ID сотрудника должен быть целым неотрицательным числом")

    # Проверяем существование отпуска по vacation_id
    db_vacation = db.query(VacationModel).filter(VacationModel.id == vacation_id).first()
    if db_vacation is None:
        raise HTTPException(status_code=404, detail="Отпуск не найден")

    delete_vacation(db, vacation_id)
    return {"message": "Отпуск успешно удален"}

