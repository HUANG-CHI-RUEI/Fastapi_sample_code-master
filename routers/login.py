from fastapi import APIRouter, Request
from sqlalchemy import delete
from influxdb import InfluxDBClient

router = APIRouter()
CLIENT = InfluxDBClient('127.0.0.1', 8086, 'root', 'password', 'testdb')


@router.post("/create_user")
def create_user():
    # 溫度
    user_info = [
        {
            "measurement": "user_info",
            "tags": {
                "topic": "account"
            },
            "fields": {
                "account": "auoread",
                "password": "auoread123",
                "user_type": "only_read"

            }
        }
    ]
    CLIENT.write_points(user_info)

    return {"result": "Done"}


@router.get("/read_user")
def read_user():
    sql = 'select * from user_info'
    result = list(CLIENT.query(sql).get_points())
    return result
