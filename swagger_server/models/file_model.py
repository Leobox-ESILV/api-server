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

## GENERIQUE FUNCTION FOR MODEL FILE

def get_user_info(username):
    connection = get_connexion()
    
    with connection.cursor() as cursor:
        sql = """SELECT `ld_accounts`.`user_id`, `oc_storages`.`path_home`, `oc_storages`.`id` as id_storage, `oc_storages`.`quota`, `oc_storages`.`used_space`  
        FROM `ld_accounts` JOIN `oc_storages` ON (ld_accounts.user_id=oc_storages.uid) 
        WHERE `ld_accounts`.`display_name`=%s"""
        cursor.execute(sql, (username))
        info_user = cursor.fetchone()
        return info_user

def recursive_create_dir(path, info_user):
    path_file = normalize_path(path)
    tab_folder = path_file.split('/')
    tstamp_now = int(time.time())
    path_final = info_user['path_home']

    connection = get_connexion()
    with connection.cursor() as cursor:
        for folder in tab_folder:
            path_final = os.path.join(path_final, folder)
            if not os.path.exists(path_final):
                os.makedirs(path_final)
                hash_pathfinal = dirhash(path_final, 'md5')
                sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `encrypted`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql2, (info_user['id_storage'],path_final.replace(info_user['path_home']+"/",""),hash_pathfinal,"Folder","inode/directory",0,tstamp_now,0))

    connection.commit()
    connection.close()
    return path_final

## END GENERIQUE FUNCTION FOR MODEL FILE

def upload_file_model(username, path_file, file, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()
        
        with connection.cursor() as cursor:
            # get info of user
            info_user = get_user_info(username)

            # Create folder if not exists !
            path_final = recursive_create_dir(path_file, info_user)
            tstamp_now = int(time.time())

            # Upload file on the server
            filename = file.filename
            path_upload = os.path.join(path_final, filename)

            if os.path.isfile(path_upload):
                return json_output(409,"a file with the same name and extension already exists")

            file.save(path_upload)

            # Check if space enough

            file_size = os.path.getsize(path_upload)
            if info_user['quota'] < (info_user['used_space']+file_size):
                os.remove(path_upload)
                return json_output(409,"not enough space available")

            # Insert info file in BDD

            hash_pathupload = dirhash(path_final, 'md5')
            sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `encrypted`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql2, (info_user['id_storage'],path_upload.replace(info_user['path_home']+"/",""),hash_pathupload,magic.from_file(path_upload),magic.from_file(path_upload, mime=True),file_size,tstamp_now,0))
            
            # Update folder of file in BDDD

            sql3 = "UPDATE `ld_filecache` SET `size`=`size`+%s WHERE `id_storage`=%s AND `path`=%s"
            cursor.execute(sql3, (file_size,info_user['id_storage'],path_final.replace(info_user['path_home']+"/","")))

            sql4 = "UPDATE `oc_storages` SET `used_space`=`used_space`+%s WHERE `id`=%s AND `uid`=%s"
            cursor.execute(sql4, (file_size,info_user['id_storage'],info_user['user_id']))
            
        connection.commit()
        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")    
    return json_output(200,"successful operation")

def get_list_file_model(username):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()
        
        with connection.cursor() as cursor:
            # get info of user
            info_user = get_user_info(username)
            
            sql2 = "SELECT * FROM ld_filecache WHERE id_storage=%s"
            cursor.execute(sql2, (info_user["id_storage"]))
            list_file = cursor.fetchall()
            for idx, val in enumerate(list_file):
                del list_file[idx]['id_storage']
            json_file = {}
            json_file['list_file'] = list_file
            return json_output(200,"successful operation",json_file)
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")    
    return json_output(400,"bad request, check information passed through API") 

def create_directory_model(username, path_dir, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        # get info of user
        info_user = get_user_info(username)

        # Create folder if not exists !
        recursive_create_dir(path_dir, info_user)
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")    
    return json_output(200,"successful operation")

def get_file_model(username, id_file):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()
        
        with connection.cursor() as cursor:
            # get info of user
            info_user = get_user_info(username)

            sql2 = "SELECT * FROM ld_filecache WHERE id_storage=%s AND id=%s"
            cursor.execute(sql2, (info_user["id_storage"],id_file))
            info_file = cursor.fetchone()
            path_file = os.path.join(info_user["path_home"], info_file['path'])
            
            return send_file(path_file,
                mimetype=info_file['mime_type'],
                as_attachment=True
            )
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")  
    return json_output(400,"bad request, check information passed through API")  