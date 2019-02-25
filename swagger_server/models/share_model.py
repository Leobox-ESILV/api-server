import connexion
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Request, Response
from swagger_server import util
import os, traceback, time, datetime, calendar, magic
from flask import Flask, request, abort, jsonify, send_from_directory, send_file
from swagger_server.models.api_generique import json_output
from swagger_server.models.api_generique import get_connexion
from swagger_server.models.api_generique import check_APIKeyUser
from swagger_server.models.api_generique import normalize_path
from checksumdir import dirhash
import json
import pandas as pd
import shutil

def get_user_info(username):
    connection = get_connexion()

    with connection.cursor() as cursor:
        sql = """SELECT `ld_accounts`.`user_id`, `oc_storages`.`path_home`, `oc_storages`.`id` as id_storage, `oc_storages`.`quota`, `oc_storages`.`used_space`
        FROM `ld_accounts` JOIN `oc_storages` ON (ld_accounts.user_id=oc_storages.uid)
        WHERE `ld_accounts`.`display_name`=%s"""
        cursor.execute(sql, (username))
        info_user = cursor.fetchone()
        return info_user

def adduser(username, username_shared, id_file, expiration):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            # get info of user
            info_user_sender = get_user_info(username)
            info_user_receiver = get_user_info(username_shared)
            timenow=int(time.time())
            # Insert info file in BDD

            sql2 = "INSERT INTO `ld_share` (`uid_owner`, `uid_recipient`, `uid_file`, `stime`, `expiration`) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql2, (info_user_sender['user_id'],info_user_receiver['user_id'],id_file,timenow,expiration))
            connection.commit()
            connection.close()



            return json_output(200,"successful operation")
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(200,"successful operation")

def removeuser(username, username_shared, id_file):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            # get info of user
            info_user_sender = get_user_info(username)
            info_user_receiver = get_user_info(username_shared)
            timenow=int(time.time())
            # Insert info file in BDD

            sql2 = "DELETE FROM `ld_share` WHERE `uid_owner`=%s AND `uid_recipient`=%s AND `uid_file`=%s"
            cursor.execute(sql2, (info_user_sender['user_id'],info_user_receiver['user_id'],id_file))
            connection.commit()
            connection.close()



            return json_output(200,"successful operation")
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(200,"successful operation")
