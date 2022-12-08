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
def get_parameter_by_toolid(tool_id: str = Query('1', enum=['1', '2', '3']),
                            name: str = Query("atp", enum=['atp', 'uvp', 'uv_hour', 'water', 'carbon'])):
    sql = '''select * from "parameter" where "tool_id" = '{}' AND "topic" = '{}' LIMIT 1
    '''.format(tool_id, name)

    result = list(CLIENT.query(sql).get_points())
    return result


@ router.get("/carbon")
def get_carbon_tool_id():

    sql = '''
    SELECT * 
    FROM
        (SELECT * FROM "parameter" WHERE (topic = 'carbon') GROUP BY tool_id, topic)  LIMIT 3
    '''
    result = list(CLIENT.query(sql).get_points())

    return result


@ router.get("/tool_id")
def get_all_tool_id():

    sql = '''
    SELECT * 
    FROM
        (SELECT * FROM "parameter" WHERE (topic = 'uvp') GROUP BY tool_id, topic )  LIMIT 3
    '''
    result = list(CLIENT.query(sql).get_points())
    uvp_df = pd.DataFrame.from_dict(result)

    sql_atp = '''
    SELECT * 
    FROM
        (SELECT * FROM "parameter" WHERE (topic = 'atp') GROUP BY tool_id, topic)  LIMIT 3
    '''
    result_atp = list(CLIENT.query(sql_atp).get_points())
    atp_df = pd.DataFrame.from_dict(result_atp)

    sql_uvh = '''
    SELECT * FROM (SELECT * FROM "parameter" WHERE (topic = 'uv_hour') GROUP BY tool_id, topic)  LIMIT 3
    '''
    result_uvp = list(CLIENT.query(sql_uvh).get_points())
    uvh_df = pd.DataFrame.from_dict(result_uvp)

    sql_water = '''
    SELECT * FROM (SELECT * FROM "parameter" WHERE (topic = 'water') GROUP BY tool_id) LIMIT 3 
    '''
    result_water = list(CLIENT.query(sql_water).get_points())
    water_df = pd.DataFrame.from_dict(result_water)

    df = pd.concat([atp_df, uvp_df, uvh_df, water_df],
                   axis=0, ignore_index=True)
    pivot_df = df.pivot(index=['tool_id'],
                        columns='topic', values='value').reset_index()

    return pivot_df.to_dict('records')


@ router.post("/parameters")
def write_parameter(tool_id: str = Query('1', enum=['1', '2', '3']),
                    name: str = Query("atp", enum=['atp', 'uvp', 'uv_hour', 'water', 'carbon'])):
    value = random.randint(10, 100)

    param = [
        {
            "measurement": "parameter",
            "tags": {
                "topic": name,
                "tool_id": tool_id
            },
            "fields": {
                "value": value

            }
        }
    ]
    CLIENT.write_points(param)

    return {"result": "Done"}
