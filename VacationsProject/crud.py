from sqlalchemy.orm import Session
from models import VacationCreate, VacationModel
from sqlalchemy import desc
from datetime import date
from fastapi import HTTPException

def create_vacation(db: Session, vacation: VacationCreate):
    # Проверяем наличие пересечений с существующими отпусками
    overlapping_vacations = db.query(VacationModel).filter(
        VacationModel.employee_id == vacation.employee_id,
        VacationModel.start_date <= vacation.end_date,
        VacationModel.end_date >= vacation.start_date
    ).first()

    # Если нашлись пересекающие отпуски, возвращаем ошибку
    if overlapping_vacations:
        raise HTTPException(status_code=400, detail="Новый отпуск пересекается с уже существующими.")

    # Если пересечений нет, создаем новый отпуск
    new_vacation = VacationModel(
        employee_id=vacation.employee_id,
        start_date=vacation.start_date,
        end_date=vacation.end_date
    )
    db.add(new_vacation)
    db.commit()
    db.refresh(new_vacation)
    return new_vacation.id

def read_vacations_by_date(db: Session, start_date: date, end_date: date):
    return db.query(VacationModel).filter(VacationModel.start_date <= end_date, VacationModel.end_date >= start_date).all()

def read_latest_vacations(db: Session, employee_id: int):
    return db.query(VacationModel).filter(VacationModel.employee_id == employee_id).order_by(desc(VacationModel.id)).limit(3).all()

def read_latest_ten_vacations(db: Session): #(нет в техническом задании, реализовано на всякий случай)
    return db.query(VacationModel).order_by(desc(VacationModel.id)).limit(10).all()

def delete_vacation(db: Session, vacation_id: int):
    vacation = db.query(VacationModel).filter(VacationModel.id == vacation_id).first()
    if vacation:
        db.delete(vacation)
        db.commit()
        return True
    return False