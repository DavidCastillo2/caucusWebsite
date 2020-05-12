import sqlite3
import db as db


def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData


def insertBLOB(bio, name, photo):
    try:
        sqliteConnection = db.get_db()
        cursor = sqliteConnection.cursor()

        sqlite_insert_blob_query = """ INSERT INTO candidate
                                  (bio, name, img) VALUES (?, ?, ?)"""

        empPhoto = convertToBinaryData(photo)
        # Convert data into tuple format
        data_tuple = (bio, name, empPhoto)
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
