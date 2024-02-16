import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)
#_________________ЧТЕНИЕ ПОСЛЕДНИХ ТРЁХ ОТПУСКОВ ПО ID СОТРУДНИКА____________________________________________________________
def test_get_latest_vacations_with_existing_employee_id(client):
    # Предположим, что идентификатор сотрудника 1 существует в базе данных с некоторыми отпусками
    response = client.get('/vacations/read_latest_vacations/1')
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3  # Убедитесь, что сотруднику предоставлено не более 3 последних отпусков

def test_get_latest_vacations_with_nonexistent_employee_id(client):
    # Предполагается, что идентификатор сотрудника 999 не существует в базе данных
    response = client.get('/vacations/read_latest_vacations/999')
    assert response.status_code == 404
    error_detail = response.json()['detail']
    assert error_detail == "Отпусков для данного сотрудника не найдено"

def test_get_latest_vacations_with_incorrect_employee_id(client):
    response = client.get('/vacations/read_latest_vacations/1к')
    assert response.status_code == 422
    error_detail = response.json()['detail']

#_________________СОЗДАНИЕ ОТПУСКА____________________________________________________________
def test_add_vacation_with_incorrect_employee_id(client):
    # Попытка создания отпуска с некорректным ID сотрудника (например, отрицательным числом)
    response = client.post("/vacations/VacationCreate", json={"employee_id": -1, "start_date": "2023-01-10", "end_date": "2023-01-20"})
    assert response.status_code == 422


def test_add_vacation_with_incorrect_dates(client):
    # Попытка создания отпуска с некорректным форматом даты
    response = client.post("/vacations/VacationCreate",json={"employee_id": 1, "start_date": "2023-01-32", "end_date": "2023-01-40"})
    assert response.status_code == 422

#_________________ПРОВЕРКА ОТПУСКОВ ПО ДАТЕ____________________________________________________________
def test_get_vacations_by_date_with_incorrect_dates(client):
    # Попытка получения отпусков с некорректным форматом даты
    response = client.get("/vacations/read_vacations_by_date", params={"start_date": "2023-01-32", "end_date": "2023-01-40"})
    assert response.status_code == 400
    error_detail = response.json()['detail']
    assert error_detail == "Дата должна быть в формате (гггг-мм-дд)"