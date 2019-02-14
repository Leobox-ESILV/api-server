import connexion
import json, os
import traceback
import secrets
from passlib.hash import pbkdf2_sha256
import time, datetime, calendar
from swagger_server.models.api_generique import json_output
from swagger_server.models.api_generique import get_connexion
from swagger_server.models.api_generique import check_APIKeyUser
from validate_email import validate_email


def create_user_model(email, username, password):

    if validate_email(email,verify=True)!=True:
        return json_output(409,"check the email because it does not exist")

    try:
        connection = get_connexion()
        password_hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        with connection.cursor() as cursor:
            sql = "SELECT `email`, `display_name` FROM `ld_accounts` WHERE `email`=%s OR `display_name`=%s"
            cursor.execute(sql, (email,username))
            if cursor.rowcount>0:
                return json_output(409,"check email/username, already exists")

        with connection.cursor() as cursor:
            sql = "INSERT INTO `ld_accounts`(`email`,`display_name`,`last_login`,`password`,`state`)VALUES(%s,%s,%s,%s,%s);"
            cursor.execute(sql, (email, username, 0, password_hash, 0))
            sql2 = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql2)

            id_user = cursor.fetchone()['LAST_INSERT_ID()']
            path_home = "/storageLeo/user/"+username+secrets.token_urlsafe(15)
            os.makedirs(path_home)
            sql3 = "INSERT INTO `oc_storages`(`path_home`,`quota`,`used_space`,`available`,`uid`)VALUES(%s,%s,%s,%s,%s);"
            # QUOTA de 10^12 = 1 GO
            cursor.execute(sql3, (path_home, 1000000000000, 0, 1, id_user))

        connection.commit()
        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")

    return json_output(200,"successful operation")

def get_user_by_name_model(username):

    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            sql = "SELECT `display_name` FROM `ld_accounts`"
            cursor.execute(sql)
            info_name = {}
            info_name['list_name'] = cursor.fetchall()
            return json_output(200,"successful operation",info_name)

        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")

    return json_output(400,"bad request, check information passed through API")

def login_user_model(username, password):
    try:
        connection = get_connexion()

        with connection.cursor() as cursor:
            sql = "SELECT `ld_accounts`.`user_id`, `ld_accounts`.`email`, `ld_accounts`.`display_name`,  `ld_accounts`.`password`, `oc_storages`.`quota`, `oc_storages`.`used_space`,`oc_storages`.`id` as storageid  FROM `ld_accounts` JOIN `oc_storages` ON (ld_accounts.user_id=oc_storages.uid) WHERE `ld_accounts`.`display_name`=%s"
            cursor.execute(sql, (username))
            info_user = cursor.fetchone()

            if cursor.rowcount==0:
                return json_output(409,"username/password wrong !")

            if pbkdf2_sha256.verify(password, info_user['password'])==True:

                expire_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
                convert_timestamp = calendar.timegm(expire_date.timetuple())
                user_token = secrets.token_urlsafe(50)

                sql2 = "INSERT INTO `ld_authtoken` (`uid`, `login_name`, `app_name`, `token`, `expiration`) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(sql2, (info_user['user_id'],info_user['display_name'],"WEB",user_token,convert_timestamp))

                tstamp_now = int(time.time())
                sql3 = "UPDATE `ld_accounts` SET `last_login`=%s WHERE `display_name`=%s"
                cursor.execute(sql3, (tstamp_now,username))

                connection.commit()

                del info_user['password']
                del info_user['user_id']
                info_user['user_token'] = user_token
                info_user['expiration_token'] = convert_timestamp

                sql3 = "select id_storage, count(*) total,sum(case when name = 'Folder' then 1 else 0 end) count_folders, sum(case when name = 'Folder' then 0 else 1 end) count_files from ld_filecache WHERE id_storage = %s group by  id_storage"
                cursor.execute(sql3, (info_user["storageid"]))
                filecount = cursor.fetchone()

                info_user['file_count'] = filecount['count_files']
                info_user['dir_count'] = filecount['count_folders']
                return json_output(200,"successful operation",info_user)
            else:
                return json_output(409,"username/password wrong !")

        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")

    return json_output(400,"bad request, check information passed through API")

def logout_user_model(username):
    if check_APIKeyUser(username)==False:
        return json_output(401,"authorization information is missing or invalid")

    try:
        connection = get_connexion()
        token = connexion.request.headers['ApiKeyUser']
        with connection.cursor() as cursor:
            sql = "DELETE FROM `ld_authtoken` WHERE `login_name`=%s AND `token`=%s"
            cursor.execute(sql, (username,token))

        connection.commit()
        connection.close()
    except:
        traceback.print_exc()
        return json_output(400,"bad request, check information passed through API")

    return json_output(200,"successful operation")
