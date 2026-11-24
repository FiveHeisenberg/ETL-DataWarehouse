from __future__ import annotations
import math, os
from datetime import date, datetime
from decimal import Decimal
from typing import Any
import pymysql
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymysql.cursors import DictCursor

DB_HOST=os.getenv('SDA_DB_HOST','127.0.0.1')
DB_PORT=int(os.getenv('SDA_DB_PORT','3306'))
DB_USER=os.getenv('SDA_DB_USER','root')
DB_PASSWORD=os.getenv('SDA_DB_PASSWORD',None) or None
DB_NAME=os.getenv('SDA_DB_NAME','db_sda_lingkungan')
PAGE_SIZE_DEFAULT=100
PAGE_SIZE_MAX=1000

TABLES={
 'wilayah':'master_wilayah',
 'fasilitas-sampah':'master_fasilitas_sampah',
 'perusahaan':'master_perusahaan',
 'stasiun-pantau':'master_stasiun_pantau',
 'izin-lingkungan':'izin_lingkungan',
 'kualitas-air-sungai':'kualitas_air_sungai',
 'kualitas-udara':'kualitas_udara',
 'timbulan-sampah':'timbulan_sampah',
 'tutupan-lahan-rth':'tutupan_lahan_rth',
}

app=FastAPI(title='REST API db_sda_lingkungan',description='REST API read-only untuk ETL/Airflow - SDA Lingkungan.',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['GET'],allow_headers=['*'])

def get_connection():
 conn_kwargs={
  'host':DB_HOST,
  'port':DB_PORT,
  'user':DB_USER,
  'database':DB_NAME,
  'cursorclass':DictCursor,
  'charset':'utf8mb4',
  'autocommit':True,
  'auth_plugin_map':{'mysql_native_password':None}
 }
 if DB_PASSWORD: conn_kwargs['password']=DB_PASSWORD
 else: conn_kwargs['password']=''
 return pymysql.connect(**conn_kwargs)

def json_safe(v:Any)->Any:
 if isinstance(v,(datetime,date)): return v.isoformat()
 if isinstance(v,Decimal): return int(v) if v==int(v) else float(v)
 if isinstance(v,bytes): return v.decode('utf-8',errors='replace')
 return v

def rows_to_json(rows): return [{k:json_safe(v) for k,v in r.items()} for r in rows]

def fetch_table_data(table:str,page:int=1,limit:int=PAGE_SIZE_DEFAULT):
 offset=(page-1)*limit
 conn=None
 try:
  conn=get_connection()
  with conn.cursor() as c:
   c.execute(f'SELECT COUNT(*) AS total FROM `{table}`')
   total=int(c.fetchone()['total'])
   total_pages=math.ceil(total/limit) if total else 0
   c.execute(f'SELECT * FROM `{table}` LIMIT %s OFFSET %s',(limit,offset))
   rows=c.fetchall()
  return {'success':True,'data':rows_to_json(rows),'pagination':{'current_page':page,'per_page':limit,'total':total,'total_pages':total_pages,'has_next':page<total_pages}}
 except pymysql.MySQLError as exc:
  raise HTTPException(status_code=500,detail={'success':False,'error':'Database error','message':str(exc)})
 finally:
  if conn is not None: conn.close()

@app.get('/',tags=['Health'])
def root(): return {'success':True,'service':'REST API db_sda_lingkungan','version':app.version,'docs':'/docs'}

@app.get('/health',tags=['Health'])
def health():
 try:
  conn=get_connection()
  try:
   with conn.cursor() as c: c.execute('SELECT 1 AS ok'); c.fetchone()
  finally: conn.close()
  return {'success':True,'database':DB_NAME,'status':'connected'}
 except Exception as exc:
  raise HTTPException(status_code=503,detail={'success':False,'database':DB_NAME,'status':'disconnected','error':str(exc)})

@app.get('/api/tables',tags=['Metadata'])
def list_tables():
 return {'success':True,'data':[{'endpoint':f'/api/{e}','table':t} for e,t in TABLES.items()]}

@app.get('/api/wilayah',tags=['Data - Master'])
def get_wilayah(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('master_wilayah',page,limit)

@app.get('/api/fasilitas-sampah',tags=['Data - Master'])
def get_fasilitas_sampah(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('master_fasilitas_sampah',page,limit)

@app.get('/api/perusahaan',tags=['Data - Master'])
def get_perusahaan(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('master_perusahaan',page,limit)

@app.get('/api/stasiun-pantau',tags=['Data - Master'])
def get_stasiun_pantau(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('master_stasiun_pantau',page,limit)

@app.get('/api/izin-lingkungan',tags=['Data - Transaksional'])
def get_izin_lingkungan(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('izin_lingkungan',page,limit)

@app.get('/api/kualitas-air-sungai',tags=['Data - Transaksional'])
def get_kualitas_air_sungai(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('kualitas_air_sungai',page,limit)

@app.get('/api/kualitas-udara',tags=['Data - Transaksional'])
def get_kualitas_udara(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('kualitas_udara',page,limit)

@app.get('/api/timbulan-sampah',tags=['Data - Transaksional'])
def get_timbulan_sampah(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('timbulan_sampah',page,limit)

@app.get('/api/tutupan-lahan-rth',tags=['Data - Transaksional'])
def get_tutupan_lahan_rth(page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 return fetch_table_data('tutupan_lahan_rth',page,limit)

@app.get('/api/{endpoint}',tags=['Data'],include_in_schema=False)
def get_table_data(endpoint:str,page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 table=TABLES.get(endpoint)
 if table is None:
  raise HTTPException(status_code=404,detail={'success':False,'error':f"Endpoint '{endpoint}' tidak tersedia.",'available_endpoints':list(TABLES)})
 return fetch_table_data(table,page,limit)
