from __future__ import annotations
import math, os
from datetime import date, datetime
from decimal import Decimal
from typing import Any
import pymysql
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymysql.cursors import DictCursor

DB_HOST=os.getenv('DISNAKER_DB_HOST','127.0.0.1')
DB_PORT=int(os.getenv('DISNAKER_DB_PORT','3306'))
DB_USER=os.getenv('DISNAKER_DB_USER','root')
DB_PASSWORD=os.getenv('DISNAKER_DB_PASSWORD','')
DB_NAME=os.getenv('DISNAKER_DB_NAME','db_disnaker')
PAGE_SIZE_DEFAULT=100
PAGE_SIZE_MAX=1000

TABLES={
 'kasus-hi':'tb_kasus_hi',
 'lowongan':'tb_lowongan',
 'pelatihan-blk':'tb_pelatihan_blk',
 'penduduk-pencaker':'tb_penduduk_pencaker',
 'penempatan':'tb_penempatan',
 'perusahaan':'tb_perusahaan',
 'peserta-pelatihan':'tb_peserta_pelatihan',
}

app=FastAPI(title='REST API db_disnaker',description='REST API read-only untuk ETL/Airflow.',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['GET'],allow_headers=['*'])

def get_connection():
 return pymysql.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD,database=DB_NAME,cursorclass=DictCursor,charset='utf8mb4',autocommit=True)

def json_safe(v:Any)->Any:
 if isinstance(v,(datetime,date)): return v.isoformat()
 if isinstance(v,Decimal): return int(v) if v==int(v) else float(v)
 if isinstance(v,bytes): return v.decode('utf-8',errors='replace')
 return v

def rows_to_json(rows): return [{k:json_safe(v) for k,v in r.items()} for r in rows]

@app.get('/',tags=['Health'])
def root(): return {'success':True,'service':'REST API db_disnaker','version':app.version,'docs':'/docs'}

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

@app.get('/api/{endpoint}',tags=['Data'])
def get_table_data(endpoint:str,page:int=Query(1,ge=1),limit:int=Query(PAGE_SIZE_DEFAULT,ge=1,le=PAGE_SIZE_MAX)):
 table=TABLES.get(endpoint)
 if table is None:
  raise HTTPException(status_code=404,detail={'success':False,'error':f"Endpoint '{endpoint}' tidak tersedia.",'available_endpoints':list(TABLES)})
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
