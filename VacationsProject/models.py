from pydantic import BaseModel
from datetime import date
from database import Base
from sqlalchemy import Column, Integer, Date

# Базовая модель для отпуска с использованием Pydantic
class VacationBase(BaseModel):
    employee_id: int
    start_date: date
    end_date: date

# Модель данных для создания нового отпуска
class VacationCreate(VacationBase):
    pass

# Модель данных для представления отпуска в API
class Vacation(VacationBase):
    id: int

    class Config:
        orm_mode = True # Позволяет возвращать объекты SQLAlchemy как словари для Pydantic


# SQLAlchemy модель для хранения отпусков в базе данных
class VacationModel(Base):
    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, index=True)
    start_date = Column(Date)
    end_date = Column(Date)