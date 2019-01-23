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
                id_parent = get_dir_parent(path_final,info_user)
                os.makedirs(path_final)
                hash_pathfinal = dirhash(path_final, 'md5')
                sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `id_parent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql2, (info_user['id_storage'],path_final.replace(info_user['path_home']+"/",""),hash_pathfinal,"Folder","inode/directory",0,tstamp_now,id_parent))
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

            id_parent = get_dir_parent(path_upload,info_user)

            hash_pathupload = dirhash(path_final, 'md5')
            sql2 = "INSERT INTO `ld_filecache` (`id_storage`, `path`, `path_hash`, `name`, `mime_type`, `size`, `storage_mtime`, `id_parent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql2, (info_user['id_storage'],path_upload.replace(info_user['path_home']+"/",""),hash_pathupload,magic.from_file(path_upload),magic.from_file(path_upload, mime=True),file_size,tstamp_now,id_parent))
            
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

            sql2 = "SELECT * FROM ld_filecache WHERE id_storage="+str(info_user["id_storage"])
            df_files = pd.read_sql(sql2, connection)

            sql3 = "SELECT parent.id AS id_parent, child.id AS id_child FROM ld_filecache parent JOIN ld_filecache child ON parent.id=child.id_parent"
            cursor.execute(sql3, ())
            parent_child = cursor.fetchall()         

            links = []
            tstamp_now = str(int(time.time()))
            root_parent = 'Files'+tstamp_now

            for val in parent_child:
                links.append((str(val['id_parent']),str(val['id_child'])))

            sql4 = "SELECT id as id_child FROM ld_filecache WHERE id_storage=%s AND id_parent is NULL AND name<>%s"
            cursor.execute(sql4, (info_user["id_storage"],"Folder"))
            root_files = cursor.fetchall()  
            
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