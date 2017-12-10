from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
 
 
def connect():
    """ Connect to MySQL database """
 
    db_config = read_db_config()
 
    try:
        print('Connecting to MySQL database...')
        conn = MySQLConnection(**db_config)
 
        if conn.is_connected():
            print('connection established.')
        else:
            print('connection failed.')
 
    except Error as error:
        print(error)
 
    finally:
        conn.close()
        print('Connection closed.')
 
 
def iter_row(cursor, size=10):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def getRoomType():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
 
        cursor.execute("""SELECT 
                       bot_table.roomType 
                       FROM botdb.bot_table""")
 
        for row in iter_row(cursor, 10):
            print(row)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

def getRoomInfo():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
 
        cursor.execute(""" SELECT bot_table.roomNo, 
                       bot_table.roomType, 
                       bot_table.amenities 
                       FROM botdb.bot_table""")
 
        for row in iter_row(cursor, 10):
            print(row)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

def getAvailableRoomInfo():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
 
        cursor.execute(""" SELECT bot_table.roomNo, 
                       bot_table.roomType, 
                       bot_table.amenities 
                       FROM botdb.bot_table 
                       WHERE bot_table.available = 1""")
 
        for row in iter_row(cursor, 10):
            print(row)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()


def getRoomAvailabilityByType(type):
    arrAvailableRoomNo = []

    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
 
        cursor.execute(" SELECT bot_table.roomno AS ROOMNO \
                          FROM botdb.bot_table \
                          WHERE ( (bot_table.checkInDate = '0000-00-00 00:00:00' or bot_table.checkInDate is NULL) and \
                                 (bot_table.checkOutDate = '0000-00-00 00:00:00' or bot_table.checkOutDate is NULL) )and \
                                 bot_table.roomType = '" + type + "'")
 
        for row in iter_row(cursor, 10):
            print(row[0])
            arrAvailableRoomNo.append(row[0])
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

        return arrAvailableRoomNo

def getRoomAvailabilityByDate(date):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
 
        cursor.execute(""" SELECT bot_table.roomNo, 
                       bot_table.roomType 
                       FROM botdb.bot_table 
                       WHERE '" + date +
                       "' NOT BETWEEN CAST(checkInDate AS DATE) 
                       and CAST(checkOutDate AS DATE)""")
 
        for row in iter_row(cursor, 10):
            print(row)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

def getBookingByEmail(email):
    room_info = None
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        
        queryString = "SELECT bot_table.roomNo,bot_table.roomType, bot_table.checkInDate, bot_table.checkOutDate FROM botdb.bot_table WHERE bot_table.email = '" + email + "' LIMIT 1"
        query = (queryString)
        cursor.execute(query)
 
        for row in cursor:
            print(row)
            room_info = row

    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()
    
    return room_info

def bookRoom(available, checkInDate,checkOutDate,firstName,lastName,address,
             city,state,postalCode,email,phone,cardNo,cardExpiryYear,
             cardExpiryMonth,arrivalInfo,remarks,roomNo):
    # read database configuration
    db_config = read_db_config()
 
    # prepare query and data
    query = """ UPDATE botdb.bot_table 
            SET 
            available = %s, 
            checkInDate = %s, 
            checkOutDate = %s, 
            firstName = %s, 
            lastName = %s,
            address = %s, 
            city = %s,
            state = %s, 
            postalCode = %s,
            email = %s, 
            phone = %s, 
            cardNo = %s, 
            cardExpiryYear = %s, 
            cardExpiryMonth = %s, 
            arrivalInfo = %s, 
            remarks = %s 
            WHERE roomNo = %s """
 
    data = (available, checkInDate,checkOutDate,firstName,lastName,address,
             city,state,postalCode,email,phone,cardNo,cardExpiryYear,
             cardExpiryMonth,arrivalInfo,remarks,roomNo)
 
    try:
        conn = MySQLConnection(**db_config)
 
        # update book title
        cursor = conn.cursor()
        cursor.execute(query, data)
 
        # accept the changes
        conn.commit()
 
    except Error as error:
        print(error)
 
    finally:
        cursor.close()
        conn.close()
 
def cancelBookingByRoomId(roomNo):
    bookRoom(1,None,None,'','','','','','','','','',00,00,'','',roomNo)

if __name__ == '__main__':
    #check if the connection works
    connect()
    
    #get the types of rooms 
    # getRoomType()
    # #get the room information
    # getRoomInfo();
    # #get information of rooms available 
    # getAvailableRoomInfo()
    # #get availability of rooms by type of the room
    print(getRoomAvailabilityByType('single'))
    getBookingByEmail("anuj251293@gmail1.com")
    cancelBookingByRoomId(8) 
    bookRoom(1,None,None,'','','','','','','','','',00,00,'','',8)
    # #get availability of rooms by date (format yyyy-mm-dd)
    #getRoomAvailabilityByDate('2017-12-06')
    # #room booking
    #bookRoom(0, '2017-12-01','2017-12-31','Julia','Roberts','9, Marine Parkway',
    #         'Redwood City','CA','94093','julia.roberts@gmail.com',
    #         '6549871524','9854759832158746',22,
    #         11,'soon','',11)
    