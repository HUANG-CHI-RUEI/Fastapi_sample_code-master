import enum
import json
import pandas as pd
from pathlib import Path
import random

from fastapi import APIRouter, Request, Query
from influxdb import InfluxDBClient
from typing import Optional


router = APIRouter()
CLIENT = InfluxDBClient('127.0.0.1', 8086, 'root', 'password', 'testdb')


@router.delete("/del_param")
def delete_table():
    drop_temp = CLIENT.query('delete from parameter')
    return {"result": "delete completed!"}


@router.get("/parameters")
def get_parameter_by_tool_id(tool_id: str = Query('1', enum=['1', '2', '3']),
                             param_name: str = Query("temperature", enum=['atp', 'temperature', 'atp_hour'])):
    sql = '''select * from "parameter" where "tool_id" = '{}' AND "topic" = '{}' LIMIT 1
    '''.format(tool_id, param_name)

    result = list(CLIENT.query(sql).get_points())
    return result


@ router.get("/tool_id")
def get_all_tool_id():

    sql = '''
    SELECT * 
    FROM
        (SELECT * FROM "parameter" WHERE (topic = 'atp_hour') GROUP BY tool_id, topic ) LIMIT 3
    '''
    result = list(CLIENT.query(sql).get_points())
    atp_hour_df = pd.DataFrame.from_dict(result)

    sql_atp = '''
    SELECT * 
    FROM
        (SELECT * FROM "parameter" WHERE (topic = 'atp') GROUP BY tool_id, topic) LIMIT 3
    '''
    result_atp = list(CLIENT.query(sql_atp).get_points())
    atp_df = pd.DataFrame.from_dict(result_atp)

    sql_temp = '''
    SELECT * FROM (SELECT * FROM "parameter" WHERE (topic = 'temperature') GROUP BY tool_id, topic)  LIMIT 3
    '''
    result_temp = list(CLIENT.query(sql_temp).get_points())
    temp_df = pd.DataFrame.from_dict(result_temp)

    sql_ph = '''
    SELECT * FROM (SELECT * FROM "parameter" WHERE (topic = 'pH') GROUP BY tool_id) LIMIT 3
    '''
    result_ph = list(CLIENT.query(sql_ph).get_points())
    ph_df = pd.DataFrame.from_dict(result_ph)

    df = pd.concat([atp_df, atp_hour_df, temp_df, ph_df],
                   axis=0, ignore_index=True)
    pivot_df = df.pivot(index=['tool_id'],
                        columns='topic', values='value').reset_index()

    return pivot_df.to_dict('records')


@ router.post("/parameters")
def write_parameter(tool_id: str = Query('1', enum=['1', '2', '3']),
                    param_name: str = Query("atp", enum=['atp', 'temperature', 'atp_hour', 'pH'])):
    value = random.randint(10, 30)

    param = [
        {
            "measurement": "parameter",
            "tags": {
                "topic": param_name,
                "tool_id": tool_id
            },
            "fields": {
                "value": value

            }
        }
    ]
    CLIENT.write_points(param)

    return {"result": "Done"}
