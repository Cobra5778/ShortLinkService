#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import configparser
import time
import MySQLdb
import redis

import logging
import logging.config

# Defining the path to the configuration
path_to_cfg = os.path.abspath('config/' + os.curdir)

# Uploading the logging configuration
logging.config.fileConfig('{}/logging.conf'.format(path_to_cfg))
logger = logging.getLogger("clrsrptlog")

def main():

    logger.info("Script started")

    # Loading the configuration to connect to the database
    config = configparser.RawConfigParser()
    config.read('{}/config.cfg'.format(path_to_cfg))

    try:
        dbuser = config.get('client', 'user')
        dbpass = config.get('client', 'password')
        dbdatabase = config.get('client', 'database')
        dbhost = config.get('client', 'host')
    except Exception as e:
        logger.critical("Can't read data for DB from file {}/config.cfg. {}".format(path_to_cfg, e))
        return 0
    # Connecting to REDIS
    try:
        r = redis.StrictRedis(
            host=config.get('redis', 'host'),
            port=config.get('redis', 'port'),
            db=config.get('redis', 'db'))
    except Exception as e:
        logger.critical("Can't read data for REDIS from file {}/config.cfg. {}".format(path_to_cfg, e))
        return 0

    logger.info("The data from the config.cfg has been uploaded successfully.")

    # Connect to DB
    try:
        cnx = MySQLdb.connect(user=dbuser, passwd=dbpass, db=dbdatabase, host=dbhost, charset="utf8")
        logger.info("Successful connection to the database.")
    except Exception as e:
        logger.critical("Can't connect to DB. {}".format(e))
        return 0

    # Looking for expired records
    cursor = cnx.cursor()
    try:
        myQuery = "SELECT id, shortlink FROM shortlink_shortlinks " \
                  "WHERE DATE_ADD(crt_date, INTERVAL valid_days DAY) < NOW()"
        cursor.execute(myQuery)
        logger.info("Running QUERY:`{}`".format(myQuery))
    except Exception as e:
        logger.critical("Can't Run Query:`{}`. {}".format(myQuery, e))
        return 0

    # Go through the array and collect the ID of expired records
    id_collect = []
    for (id, shortlink) in cursor:
        id_collect.append(id)
        # Clean the records in REDIS
        r.delete(shortlink)

    logger.info("Records to delete:`{}`".format(len(id_collect)))

    # Clean the records in DB
    for id in id_collect:
        myQuery = "DELETE FROM shortlink_shortlinks WHERE id={}".format(id)
        cursor.execute(myQuery)
    # Confirm the transaction and close the session
    cnx.commit()
    cnx.close()

    logger.info("Done!")


if __name__ == "__main__":

    # Loading the configuration frequency of the script operation - clear_interval_hours
    config = configparser.RawConfigParser()
    config.read('{}/config.cfg'.format(path_to_cfg))

    try:
        clear_interval_hours = float(config.get('clearscrpit', 'clear-interval-hours'))
    except:
        # If the value is not defined, the default is 24 hours
        logger.warning("Something's wrong. Not correct value `clear-interval-hours` in config file. "
                       "Curent `clear-interval-hours` set's to 24 hours.")
        clear_interval_hours = 24

    logger.info("`clear-interval-hours` set's to {} hours ({} sek).".format(clear_interval_hours,
                                                                     int(round(clear_interval_hours * 3600, 0))))
    # Repeat indefinitely at a given interval
    while True:
        main()
        try:
            time.sleep(int(round(clear_interval_hours * 3600, 0)))
        except:
            logger.warning("The value is beyond the limit, set `clear-interval-hours` to 24 hours.")
            time.sleep(86400)