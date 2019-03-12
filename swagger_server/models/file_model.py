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

## GENERIQUE FUNCTION FOR MODEL FILE
def getdirsize(path_final,info_user):
    connection = get_connexion()

    with connection.cursor() as cursor:
        sizetot = 0
        if not (os.path.exists(path_final)):
            return sizetot
        else:
            if not (path_final == info_user['path_home']):
                sql = """SELECT SUM(size) as total_size FROM `ld_filecache` WHERE  path LIKE %s and id_storage=%s"""
                cursor.execute(sql,  (path_final.replace(info_user['path_home']+"/","")+"/%",info_user['id_storage']))
                size = cursor.fetchone()
                if size['total_size'] is not None:
                    sizetot = size['total_size']

                return sizetot
            else:
                sql = """SELECT SUM(size) as total_size FROM `ld_filecache` WHERE  id_parent IS NULL and id_storage=%s"""
                cursor.execute(sql,  (info_user['id_storage']))
                size = cursor.fetchone()
                if size['total_size'] is not None:
                    sizetot = size['total_size']
                return sizetot
    connection.close()

def recursive_update_size(path_final, info_user):
    connection = get_connexion()

    with connection.cursor() as cursor:
        if not (os.path.exists(path_final)):
            path_final = path_final.rsplit('/',1)[0]
        else:
            size = 0
            sql = """UPDATE `ld_filecache`SET `size`=%s WHERE path = %s and id_storage=%s"""
            if os.path.isfile(path_final):
                size = os.path.getsize(path_final)
                path_final = path_final.rsplit('/',1)[0]
            else:
                if path_final[-1] =="/":
                    path_final = path_final.rsplit('/',1)[0]
                size = getdirsize(path_final, info_user)
            cursor.execute(sql,  (size,path_final.replace(info_user['path_home']+"/",""),info_user['id_storage']))
            connection.commit()

        while (path_final != info_user['path_home']):
            sql = """UPDATE `ld_filecache`SET `size`=%s WHERE path = %s and id_storage=%s"""
            size = getdirsize(path_final, info_user)
            cursor.execute(sql,  (size,path_final.replace(info_user['path_home']+"/",""),info_user['id_storage']))
            connection.commit()
            path_final = path_final.rsplit('/',1)[0]
        sql = """UPDATE `oc_storages`SET `used_space`=%s WHERE uid = %s"""
        cursor.execute(sql,  (getdirsize(info_user['path_home'], info_user),info_user['user_id']))
        connection.commit()
    connection.close()
def get_user_info(username):
    connection = get_connexion()

    with connection.cursor() as cursor:
        sql = """SELECT `ld_accounts`.`user_id`, `oc_storages`.`path_home`, `oc_storages`.`id` as id_storage, `oc_storages`.`quota`, `oc_storages`.`used_space`
        FROM `ld_accounts` JOIN `oc_storages` ON (ld_accounts.user_id=oc_storages.uid)
        WHERE `ld_accounts`.`display_name`=%s"""
        cursor.execute(sql, (username))
        info_user = cursor.fetchone()
        return info_user

def get_dir_parent(path_final, info_user):
    connection = get_connexion()
    with connection.cursor() as cursor:
        path_parent = path_final.rsplit('/',1)[0]

        id_parent = None
        sql3 = "SELECT id as id_parent FROM ld_filecache WHERE path=%s AND id_storage=%s"
        cursor.execute(sql3, (path_parent.replace(info_user['path_home']+"/",""),info_user['id_storage']))
        info_parent = cursor.fetchone()

        try:
            id_parent = info_parent['id_parent']
        except TypeError:
            id_parent = None

        return id_parent

def get_jsonanwser(path_final, info_user,fileoverwrite = None):
    connection = get_connexion()
    with connection.cursor() as cursor:
        info_fileinsert = {}
        if not fileoverwrite :
            sql2 = "SELECT * FROM ld_filecache WHERE path = %s and id_storage = %s"
            cursor.execute(sql2, (path_final.replace(info_user['path_home']+"/",""),info_user['id_storage']))
            info_file = cursor.fetchone()
            info_fileinsert['id'] = info_file['id']
            info_fileinsert['mime_type'] = info_file['mime_type']
            info_fileinsert['name'] =  path_final.rsplit('/',1)[-1]
            info_fileinsert['path_file'] = info_file['path']
            info_fileinsert['size'] = info_file['size']
            info_fileinsert['storage_mtime'] = info_file['storage_mtime']
            info_fileinsert['type'] = info_file['name']
        else:
            info_fileinsert['id'] = fileoverwrite['id']
            info_fileinsert['mime_type'] = fileoverwrite['mime_type']
            info_fileinsert['name'] =  path_final.rsplit('/',1)[-1]
            info_fileinsert['path_file'] = fileoverwrite['path_file']
            info_fileinsert['size'] = fileoverwrite['size']
            info_fileinsert['storage_mtime'] = fileoverwrite['storage_mtime']
            info_fileinsert['type'] = fileoverwrite['name']
        sql3 = "select id_storage, count(*) total,sum(case when name = 'Folder' then 1 else 0 end) count_folders, sum(case when name = 'Folder' then 0 else 1 end) count_files from ld_filecache WHERE id_storage = %s group by  id_storage"
        cursor.execute(sql3, (info_user["id_storage"]))
        filecount = cursor.fetchone()
        if filecount is not None:
            info_fileinsert['file_count'] = filecount['count_files']
            info_fileinsert['dir_count'] = filecount['count_folders']
        else:
            info_fileinsert['file_count'] = 0
            info_fileinsert['dir_count'] = 0
        info_fileinsert['quota'] = info_user['quota']
        info_fileinsert['used_space'] = info_user['used_space']
        return info_fileinsert


def recursive_create_dir(path, info_user, is_info=False):
    path_file = normalize_path(path)
    tab_folder = path_file.split('/')
    tstamp_now = int(time.time())
    path_final = info_user['path_home']
    info_dossiercreated = None
    connection = get_connexion()
    with connection.cursor() as cursor:
        for folder in tab_folder:
            path_final = os.path.join(path_final, folder)
            if not os.path.exists(path_final):
                id_parent = get_dir_parent(path_final,info_user)
                os.makedirs(path_final)
                hash_pathfinal = dirhash(path_final, 'md5')
                sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `id_parent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql2, (info_user['id_storage'],path_final.replace(info_user['path_home']+"/",""),hash_pathfinal,"Folder","inode/directory",0,tstamp_now,id_parent))
                connection.commit()
                if is_info==True:
                     sql45 = "SELECT id, mime_type, path as path_file, name as type, storage_mtime, size FROM ld_filecache WHERE id=(SELECT LAST_INSERT_ID())"
                     cursor.execute(sql45)
                     info_dossiercreated = cursor.fetchone()

    connection.close()
    if is_info==True and info_dossiercreated is not None:
        return info_dossiercreated
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

            id_parent = get_dir_parent(path_upload,info_user)

            hash_pathupload = dirhash(path_final, 'md5')
            sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `id_parent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql2, (info_user['id_storage'],path_upload.replace(info_user['path_home']+"/",""),hash_pathupload,magic.from_file(path_upload),magic.from_file(path_upload, mime=True),file_size,tstamp_now,id_parent))
            connection.commit()
            connection.close()

            recursive_update_size(path_upload, info_user)
            info_fileinsert=get_jsonanwser(path_upload, info_user)

            return json_output(200,"successful operation",info_fileinsert)
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

            sql2 = "SELECT * FROM ld_filecache WHERE id_storage="+str(info_user["id_storage"])
            df_files = pd.read_sql(sql2, connection)

            # If any file on the folder of user (new user)

            if df_files.empty:
                json_list = {}
                json_list['sub_dir'] = []
                return json_output(200,"successful operation",json_list)

            sql3 = "SELECT parent.id AS id_parent, child.id AS id_child FROM ld_filecache parent JOIN ld_filecache child ON parent.id=child.id_parent WHERE parent.id_storage=%s AND child.id_storage=%s"
            cursor.execute(sql3, (info_user["id_storage"],info_user["id_storage"]))
            parent_child = cursor.fetchall()

            links = []
            tstamp_now = str(int(time.time()))
            root_parent = 'Files'+tstamp_now

            for val in parent_child:
                links.append((str(val['id_parent']),str(val['id_child'])))

            sql4 = "SELECT id as id_child FROM ld_filecache WHERE id_storage=%s AND id_parent is NULL AND id not in (SELECT parent.id FROM ld_filecache parent JOIN ld_filecache child ON parent.id=child.id_parent)"
            cursor.execute(sql4, (info_user["id_storage"]))
            root_files = cursor.fetchall()

            # If only file on root dir and no tree json

            if len(links)==0:
                sql45 = "SELECT id, mime_type, path as path_file, name as type, storage_mtime, size FROM ld_filecache WHERE id_storage=%s"
                cursor.execute(sql45, (info_user["id_storage"]))
                list_file = cursor.fetchall()

                for i, val in enumerate(list_file):
                    list_file[i]['name'] = list_file[i]['path_file'].split('/')[-1]

                json_list = {}
                json_list['sub_dir'] = list_file
                return json_output(200,"successful operation",json_list)

            parents, children = zip(*links)
            root_nodes = {x for x in parents if x not in children}
            for node in root_nodes:
                links.append((root_parent, node))

            for val in root_files:
                links.append((root_parent,val['id_child']))

            def get_nodes(node):
                d = {}
                d['name'] = node

                if node!=root_parent:
                    d['name'] = df_files.loc[df_files['id'] == int(node)]['path'].values[0].split('/')[-1]

                try:
                    d['path_file'] = df_files.loc[df_files['id'] == int(node)]['path'].values[0]
                    d['type'] = df_files.loc[df_files['id'] == int(node)]['name'].values[0]
                    d['id'] = int(df_files.loc[df_files['id'] == int(node)]['id'].values[0])
                    d['mime_type'] = df_files.loc[df_files['id'] == int(node)]['mime_type'].values[0]
                    d['size'] = int(df_files.loc[df_files['id'] == int(node)]['size'].values[0])
                    d['storage_mtime'] = int(df_files.loc[df_files['id'] == int(node)]['storage_mtime'].values[0])
                except ValueError:
                    pass
                children = get_children(node)
                if children:
                    d['sub_dir'] = [get_nodes(child) for child in children]
                return d

            def get_children(node):
                return [x[1] for x in links if x[0] == node]

            json_tree = get_nodes(root_parent)
            del json_tree["name"]
            return json_output(200,"successful operation",json_tree)
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
        info_dossiercreated = recursive_create_dir(path_dir, info_user, True)
        if info_dossiercreated==False:
            return json_output(409,"Folder already exists !")
        info_dossiercreated['name'] = info_dossiercreated['path_file'].split('/')[-1]
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(200,"successful operation",info_dossiercreated)

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

def delete_file_model(username, id_file):
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
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")
            path_file = os.path.join(info_user["path_home"], info_file['path'])
            size = info_file['size']
            fileoverwrite=get_jsonanwser(path_file, info_user)

            if (info_file['name'] == 'Folder'):
                shutil.rmtree(path_file)
                path_sql = info_file['path'] + '%'
                sql4 = "DELETE FROM ld_filecache WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (info_user["id_storage"],path_sql))

            else:
                os.remove(path_file)
                sql5 = "DELETE FROM ld_filecache WHERE id_storage=%s AND id=%s"
                cursor.execute(sql5, (info_user["id_storage"],id_file))


            connection.commit()
            connection.close()
            recursive_update_size(path_file, info_user)
            anwser = get_jsonanwser(path_file, info_user,fileoverwrite)
            return json_output(200,"successful operation",anwser)

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
            tstamp_now = int(time.time())
            # get info of user
            info_user = get_user_info(username)
            sql2 = "SELECT * FROM ld_filecache WHERE id_storage=%s AND id=%s"
            cursor.execute(sql2, (info_user["id_storage"],id_file))
            info_file = cursor.fetchone()
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")
            old_path = info_user['path_home']+'/'+info_file['path']
            new_path = old_path.rsplit('/',1)[0]+'/'+path_file
            #Rename folder
            if os.path.isdir(old_path):
                os.rename(old_path,new_path)
                path_sql = info_file['path'] + '%'
                sql4 = "UPDATE `ld_filecache` SET `path` = REPLACE(path, %s, %s),`storage_mtime`=%s  WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (info_file['path'],new_path.replace(info_user['path_home']+"/",""),tstamp_now,info_user["id_storage"],path_sql))
            else:
                os.rename(old_path,new_path)
                sql4 = "UPDATE `ld_filecache` SET `path` = %s,`storage_mtime`=%s WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (new_path.replace(info_user['path_home']+"/",""),tstamp_now,info_user["id_storage"],info_file['path']))

        connection.commit()
        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(200,"successful operation")

def move_file_model(username, id_file, path_file, propertyname, propertyvalue):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:


            # get info of user
            tstamp_now = int(time.time())
            info_user = get_user_info(username)
            sql2 = "SELECT * FROM ld_filecache WHERE id_storage=%s AND id=%s"
            cursor.execute(sql2, (info_user["id_storage"],id_file))
            info_file = cursor.fetchone()
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")
            old_path = info_user['path_home']+'/'+info_file['path']
            filename = old_path.rsplit('/',1)[-1]
            id_parent = None
            if path_file != "/":
                new_path = info_user['path_home']+'/'+path_file
                sql2 = "SELECT * FROM ld_filecache WHERE id_storage=%s AND path=%s"
                cursor.execute(sql2, (info_user["id_storage"],path_file.rsplit('/',1)[0]))
                info_parent = cursor.fetchone()
                id_parent = info_parent["id"]
            else:
                new_path = info_user['path_home']+'/'
                path_file = ""
            #Rename folder
            if os.path.isdir(old_path):
                newfilepathfull= new_path+filename
                if os.path.isdir(newfilepathfull):
                    return json_output(400,"Error, folder with the same name aleady exist in this directory")
                sql4 = "UPDATE `ld_filecache` SET id_parent=%s  WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (id_parent,info_user["id_storage"],info_file['path']))
                connection.commit()
                path_sql = info_file['path'] + '%'
                sql4 = "UPDATE `ld_filecache` SET `path` = REPLACE(path, %s, %s),`storage_mtime`=%s  WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (info_file['path'],path_file+filename,tstamp_now,info_user["id_storage"],path_sql))
                connection.commit()
                shutil.move(old_path,new_path)

            else:
                newfilepathfull= new_path+filename
                if os.path.isfile(newfilepathfull):
                    sql2 = "SELECT * FROM ld_filecache WHERE id_storage=%s AND path=%s"
                    cursor.execute(sql2, (info_user["id_storage"],newfilepathfull.replace(info_user['path_home']+"/","")))
                    info_newfile = cursor.fetchone()
                    delete_file_model(username, info_newfile["id"])
                shutil.move(old_path,new_path)
                sql4 = "UPDATE `ld_filecache` SET `path` = %s, id_parent=%s,  `storage_mtime`=%s WHERE id_storage=%s AND  path LIKE %s"
                cursor.execute(sql4, (path_file+filename,id_parent,tstamp_now,info_user["id_storage"],info_file['path']))
                connection.commit()
            recursive_update_size(old_path, info_user)
            recursive_update_size(new_path, info_user)
        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(200,"successful operation")

def update_file_model(username, id_file, file, propertyname, propertyvalue):
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
            if not info_file:
                return json_output(400,"Fichier introuvable dans la BDD")

            # Create folder if not exists !
            tstamp_now = int(time.time())
            os_path = info_user['path_home']+"/"+info_file['path']
            if not (os.path.isfile(os_path)):
                return json_output(409,"File doesn't exist")


            os.remove(os_path)
            file.save(os_path)

            # Check if space enough

            file_size = os.path.getsize(os_path)
            if info_user['quota'] < (info_user['used_space']+file_size):
                os.remove(os_path)
                return json_output(409,"not enough space available")


            sql2 = "UPDATE `ld_filecache` SET `name` = %s, `mime_type`=%s, `size`=%s, `storage_mtime`=%s WHERE id=%s AND id_storage=%s"
            cursor.execute(sql2, (magic.from_file(os_path),magic.from_file(os_path, mime=True),file_size,tstamp_now,id_file, info_user["id_storage"]))
            connection.commit()
            recursive_update_size(os_path, info_user)



        connection.close()

    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")
    return json_output(200,"successful operation")
