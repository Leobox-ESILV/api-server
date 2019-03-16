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
    connection.close()

def get_username(uid):
    connection = get_connexion()

    with connection.cursor() as cursor:
        sql = """SELECT `display_name` FROM ld_accounts WHERE user_id=%s"""
        cursor.execute(sql, (uid))
        username = cursor.fetchone()
        return username
def isSharedWith(uid_file,username):
    connection = get_connexion()

    with connection.cursor() as cursor:
        userinfo = get_user_info(username)
        fileid = uid_file

        sql31 = """SELECT uid_file
        FROM `ld_share`
        WHERE `uid_recipient`=%s"""
        cursor.execute(sql31, (userinfo['user_id']))
        directoryaccess = cursor.fetchall()
        if cursor.rowcount == 0:
            print("Aucun fichier chez le user")
            return False
        for val in directoryaccess:
            print("Check if "+str(val['uid_file']) +"="+str(uid_file))
            if val['uid_file'] == uid_file:
                print("Permission accordé")
                return True

        while True:
            print("Test avec "+str(fileid))
            sql32 = """SELECT id_parent
            FROM `ld_filecache`
            WHERE `id`=%s"""
            cursor.execute(sql32, (fileid))
            sharedwithlist2 = cursor.fetchall()
            if cursor.rowcount == 0:
                print("Aucun avec l'id "+str(fileid))
                return False

            for val in directoryaccess:
                print("Check if "+str(val['uid_file']) +"="+str(sharedwithlist2[0]['id_parent']))
                if val['uid_file'] == sharedwithlist2[0]['id_parent']:
                    print("Permission accordé")
                    return True
            if sharedwithlist2[0]['id_parent'] is None:
                print("Check if "+str(sharedwithlist2[0]['id_parent'])+" exist = FALSE")
                return False
            fileid = sharedwithlist2[0]['id_parent']


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

def getsharedlistfile(username):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            # get info of user
            info_user = get_user_info(username)

            sql3 = "SELECT DISTINCT uid_owner FROM ld_share WHERE uid_recipient=%s"
            cursor.execute(sql3, (info_user["user_id"]))
            sharedwithlist = cursor.fetchall()
            # If any file on the folder of user (new user)

            if sharedwithlist is None:
                return json_output(200,"successful operation",[])

            listfolder = []
            for val in sharedwithlist:
                info_user_shared = get_username(val['uid_owner'])
                listfolder.append((info_user_shared['display_name'],val['uid_owner']))
            connection.close()

            return json_output(200,"successful operation",listfolder)
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")

def getsharedlistfile2(username,uid_owner):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            # get info of user
            info_user = get_user_info(username)

            sql3 = """SELECT *
            FROM `ld_share` JOIN `ld_filecache` ON (ld_share.uid_file=ld_filecache.id)
            WHERE `ld_share`.`uid_recipient`=%s AND `ld_share`.`uid_owner`=%s"""
            cursor.execute(sql3, (info_user["user_id"],uid_owner))
            sharedwithlist = cursor.fetchall()
            # If any file on the folder of user (new user)

            if sharedwithlist is None:
                return json_output(200,"successful operation",[])

            listfolder = []
            for val in sharedwithlist:
                listfolder.append(val)
            connection.close()

            return json_output(200,"successful operation",listfolder)
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")

def getsharedlistfile3(username,uid_file):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            # get info of user
            info_user = get_user_info(username)

            sql3 = """SELECT `ld_filecache`.*
            FROM `ld_share` JOIN `ld_filecache` ON (ld_share.uid_file=ld_filecache.id_parent)
            WHERE `ld_share`.`uid_recipient`=%s AND `ld_share`.`uid_file`=%s"""
            cursor.execute(sql3, (info_user["user_id"],uid_file))
            sharedwithlist = cursor.fetchall()
            # If any file on the folder of user (new user)
            listfolder = []
            if cursor.rowcount == 0:
                if isSharedWith(uid_file,username):
                    sql31 = """SELECT *
                    FROM `ld_filecache`
                    WHERE `id_parent`=%s"""
                    cursor.execute(sql31, (uid_file))
                    sharedwithlist2 = cursor.fetchall()
                    if sharedwithlist2 is None:
                        return json_output(200,"successful operation",listfolder)
                    for val in sharedwithlist2:
                        listfolder.append(val)
                    return json_output(200,"successful operation",listfolder)
                else:
                    return json_output(400,"Access denied to the folder")

            for val in sharedwithlist:
                listfolder.append(val)
            connection.close()

            return json_output(200,"successful operation",listfolder)
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")

def get_file_model(username, id_file):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            # get info of user
            if not isSharedWith(id_file,username):
                return json_output(400,"File is not shared with this user")



            sql2 = """SELECT *
                    FROM ld_filecache JOIN `oc_storages` ON (ld_filecache.id_storage=oc_storages.id)
                    WHERE ld_filecache.id=%s"""
            cursor.execute(sql2, (id_file))
            info_file = cursor.fetchone()
            path_file = os.path.join(info_file["path_home"], info_file['path'])

            return send_file(path_file,
                mimetype=info_file['mime_type'],
                as_attachment=True
            )
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")
def delete_file_model(username, id_file):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            if not isSharedWith(id_file,username):
                return json_output(400,"File is not shared with this user")
            # get info of user

            sql2 = """SELECT *
                    FROM ld_filecache JOIN `oc_storages` ON (ld_filecache.id_storage=oc_storages.id)
                    WHERE ld_filecache.id=%s"""
            cursor.execute(sql2, (id_file))
            info_file = cursor.fetchone()
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")
            path_file = os.path.join(info_file["path_home"], info_file['path'])
            size = info_file['size']
            #fileoverwrite=get_jsonanwser(path_file, info_user)


            if (info_file['name'] == 'Folder'):
                shutil.rmtree(path_file)
                path_sql = info_file['path'] + '%'
                sql4 = "DELETE FROM ld_filecache WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (info_file["id_storage"],path_sql))

            else:
                os.remove(path_file)
                sql5 = "DELETE FROM ld_filecache WHERE id_storage=%s AND id=%s"
                cursor.execute(sql5, (info_file["id_storage"],id_file))


            connection.commit()
            connection.close()
            #recursive_update_size(path_file, info_user)
            #anwser = get_jsonanwser(path_file, info_user,fileoverwrite)
            return json_output(200,"successful operation")

    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")
def rename_file_model(username, id_file, path_file, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            if not isSharedWith(id_file,username):
                return json_output(400,"File is not shared with this user")
            # get info of user

            tstamp_now = int(time.time())
            # get info of user
            sql2 = """SELECT *
                    FROM ld_filecache JOIN `oc_storages` ON (ld_filecache.id_storage=oc_storages.id)
                    WHERE ld_filecache.id=%s"""
            cursor.execute(sql2, (id_file))
            info_file = cursor.fetchone()
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")
            old_path = info_file['path_home']+'/'+info_file['path']
            new_path = old_path.rsplit('/',1)[0]+'/'+path_file
            #Rename folder
            if os.path.isdir(old_path):
                os.rename(old_path,new_path)
                path_sql = info_file['path'] + '%'
                sql4 = "UPDATE `ld_filecache` SET `path` = REPLACE(path, %s, %s),`storage_mtime`=%s  WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (info_file['path'],new_path.replace(info_file['path_home']+"/",""),tstamp_now,info_file["id_storage"],path_sql))
            else:
                os.rename(old_path,new_path)
                sql4 = "UPDATE `ld_filecache` SET `path` = %s,`storage_mtime`=%s WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (new_path.replace(info_file['path_home']+"/",""),tstamp_now,info_file["id_storage"],info_file['path']))


            connection.commit()
            connection.close()
            #recursive_update_size(path_file, info_user)
            #anwser = get_jsonanwser(path_file, info_user,fileoverwrite)
            return json_output(200,"successful operation")

    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")

def update_file_model(username, id_file, file, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            if not isSharedWith(id_file,username):
                return json_output(400,"File is not shared with this user")
            # get info of user

            # get info of user
            sql2 = """SELECT *
                    FROM ld_filecache JOIN `oc_storages` ON (ld_filecache.id_storage=oc_storages.id)
                    WHERE ld_filecache.id=%s"""
            cursor.execute(sql2, (id_file))
            info_file = cursor.fetchone()
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")

            # Create folder if not exists !
            tstamp_now = int(time.time())
            os_path = info_file['path_home']+"/"+info_file['path']
            if not (os.path.isfile(os_path)):
                return json_output(409,"File doesn't exist")


            os.remove(os_path)
            file.save(os_path)


            sql2 = "UPDATE `ld_filecache` SET `name` = %s, `mime_type`=%s, `size`=%s, `storage_mtime`=%s WHERE id=%s AND id_storage=%s"
            cursor.execute(sql2, (magic.from_file(os_path),magic.from_file(os_path, mime=True),file_size,tstamp_now,id_file, info_file["id_storage"]))
            connection.commit()

            connection.close()
            #recursive_update_size(path_file, info_user)
            #anwser = get_jsonanwser(path_file, info_user,fileoverwrite)
            return json_output(200,"successful operation")

    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")
def upload_file_model(username, parent_id, file, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            if not isSharedWith(parent_id,username):
                return json_output(400,"File is not shared with this user")

            sql2 = """SELECT *
                    FROM ld_filecache JOIN `oc_storages` ON (ld_filecache.id_storage=oc_storages.id)
                    WHERE ld_filecache.id=%s"""
            cursor.execute(sql2, (parent_id))
            info_file = cursor.fetchone()
            filename = file.filename
            tstamp_now = int(time.time())
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")

            # Create folder if not exists !
            os_path = info_file['path_home']+"/"+info_file['path']+"/"+filename

            file.save(os_path)
            file_size = os.path.getsize(os_path)
            hash_pathupload = dirhash(info_file['path_home']+"/"+info_file['path']+"/", 'md5')

            sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `id_parent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql2, (info_file['id_storage'],os_path.replace(info_file['path_home']+"/",""),hash_pathupload,magic.from_file(os_path),magic.from_file(os_path, mime=True),file_size,tstamp_now,parent_id))
            connection.commit()

            connection.close()
            #recursive_update_size(path_file, info_user)
            #anwser = get_jsonanwser(path_file, info_user,fileoverwrite)
            return json_output(200,"successful operation")

    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")
def create_directory_model(username, path_dir,parent_id, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            if not isSharedWith(parent_id,username):
                print("Here is the prob")
                return json_output(400,"File is not shared with this user")

            sql2 = """SELECT *
                    FROM ld_filecache JOIN `oc_storages` ON (ld_filecache.id_storage=oc_storages.id)
                    WHERE ld_filecache.id=%s"""
            cursor.execute(sql2, (parent_id))
            info_file = cursor.fetchone()
            tstamp_now = int(time.time())
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")

            # Create folder if not exists !
            os_path = info_file['path_home']+"/"+info_file['path']+"/"+path_dir
            os.makedirs(os_path)
            hash_pathupload = dirhash(os_path, 'md5')

            sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `id_parent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql2, (info_file['id_storage'],os_path.replace(info_file['path_home']+"/",""),hash_pathupload,"Folder","inode/directory",0,tstamp_now,parent_id))
            connection.commit()

            connection.close()
            #recursive_update_size(path_file, info_user)
            #anwser = get_jsonanwser(path_file, info_user,fileoverwrite)
            return json_output(200,"successful operation")

    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(400,"bad request, check information passed through API")
