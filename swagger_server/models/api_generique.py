import connexion
import six
import pymysql.cursors
import json, os
import traceback
import secrets
from flask import Response, jsonify
from jsonmerge import merge
import time, datetime, calendar
import configparser

db_file = configparser.ConfigParser()
db_file.read('/pwd_dir/db_mysql.ini')
HOST = db_file.get('connexion', 'host')
USER = db_file.get('connexion', 'user')
PASSWORD = db_file.get('connexion', 'password')
DB = db_file.get('connexion', 'db')

def json_output(status_code,comment,json_input=None):
    is_status = False
    if str(status_code)[0]=="2" : 
        is_status = True
    message = {
            'is_status': is_status,
            'comment': comment,
    }
    result = message
    if json_input is not None:
        result = merge(message, json_input)
    resp = jsonify(result)
    resp.status_code = status_code
    return resp

def get_connexion():
    connection = pymysql.connect(host=HOST,user=USER,password=PASSWORD,db=DB,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    return connection

def check_APIKeyUser(username):
    try:
        token = connexion.request.headers['ApiKeyUser']
        connection = get_connexion()
        with connection.cursor() as cursor:
            sql = "SELECT `expiration` FROM `ld_authtoken` WHERE `token`=%s AND `login_name`=%s"
            cursor.execute(sql, (token,username))
            info_key = cursor.fetchone()
            tstamp_now = int(time.time())
            tstamp_expire = info_key['expiration']
            if tstamp_now < tstamp_expire:
                return True
    except:
        return False
    return False

def normalize_path(path_file):
    path_return = path_file
    if path_return.startswith('/'):
        path_return = path_return[1:]
    if path_return.endswith('/'):
        path_return = path_return[:-1]
    return path_return