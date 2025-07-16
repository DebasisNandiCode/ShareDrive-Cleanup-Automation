from datetime import datetime
import pytz
import os
import pyodbc
import socket
import getpass
import re
import ast  # Safer alternative to eval()
from urllib.parse import quote_plus
from dotenv import load_dotenv

class Logger:

    # Load environment variables from .env file
    load_dotenv()

    # Get database credentials
    CentDB_HOST = os.getenv("CentDB_HOST")
    CentDB_DATABASE = os.getenv("CentDB_DATABASE")
    CentDB_USER = os.getenv("CentDB_USER")
    CentDB_PASSWORD = os.getenv("CentDB_PASSWORD")

    # Properly encode password for SQLAlchemy
    encoded_password = quote_plus(CentDB_PASSWORD)

    # Raise an error if any variable is missing
    if not all([CentDB_HOST, CentDB_DATABASE, CentDB_USER, CentDB_PASSWORD]):
        raise ValueError("Missing credentials! Please check the .env file.")
    

    # CONNECTION_STRING = 'DRIVER={SQL Server};SERVER={DB_HOST};DATABASE={DB_DATABASE};UID={DB_USER};PWD={DB_PASSWORD}'
    # CONNECTION_STRING = f"DRIVER={{SQL Server}};SERVER={CentDB_HOST};DATABASE={CentDB_DATABASE};UID={CentDB_USER};PWD={encoded_password}"
    CONNECTION_STRING = f"DRIVER={{SQL Server}};SERVER={CentDB_HOST};DATABASE={CentDB_DATABASE};UID={CentDB_USER};PWD={CentDB_PASSWORD}"
    
    LOG_FOLDER_PATH = os.path.join(os.path.expanduser("~"), "Documents", "LogFolder")
    LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, "dbErrorLog.txt")

    def __init__(self):
        """Ensure log folder exists."""
        os.makedirs(self.LOG_FOLDER_PATH, exist_ok=True)
    
    def replace_datetime(self, match):
        """Replaces datetime.datetime(...) with a properly formatted string."""
        dt_args = match.group(1)
        try:
            dt_tuple = ast.literal_eval(f"({dt_args})")
            dt_obj = datetime(*dt_tuple)  # Convert to datetime object
            return f"'{dt_obj.strftime('%Y-%m-%d %H:%M:%S')}'"
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing datetime: {e}")
            return match.group(0)  # Return original if parsing fails

    def log_to_database(self, tskID, logType, logCode, currentStatus, logRemarksUser, logMessage, logDetails):

        # log_to_database(self, tskID, logType, logCode, logDetails, logMessage, currentStatus, logRemarksUser):

        """Logs an event to the database and writes failed queries to a log file."""
        ip_address = socket.gethostbyname(socket.gethostname())
        username = getpass.getuser()

        est = pytz.timezone("US/Eastern")
        getDate = datetime.now().astimezone(est)

        lastErrorStatusTimestamp = datetime.strptime("1900-01-01 12:00:00", "%Y-%m-%d %H:%M:%S") \
            if currentStatus == "NA" else datetime.now()
        
        log_query = """INSERT INTO DailyTaskLogs 
                (Log_TimeStamp, Task_ID, Log_Type, Log_Code, Error_Current_Status, Log_Remarks_User, 
                 Last_Error_Status_TimeStamp, Log_Remarks_System, Log_Details,
                 System_IP, System_User_Name) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        try:
            connection = pyodbc.connect(self.CONNECTION_STRING)
            cursor = connection.cursor()
            logMessage = logMessage.replace("\r", "").replace("\n", "").replace("\t", "")
            cursor.execute(log_query,
                           getDate.strftime("%Y-%m-%d %H:%M:%S"), tskID, logType, logCode, currentStatus, logRemarksUser,
                           lastErrorStatusTimestamp.strftime("%Y-%m-%d %H:%M:%S"),logMessage,
                           logDetails, ip_address, username)
            
            connection.commit()
            cursor.close()
            connection.close()

            self.process_old_log_entries()

        except Exception as ex:
            self.log_to_file(log_query, (getDate.strftime("%Y-%m-%d %H:%M:%S"), tskID, logType, logCode, 
                                         currentStatus + '- PendingUpdated', logRemarksUser,
                                        lastErrorStatusTimestamp.strftime("%Y-%m-%d %H:%M:%S"), logMessage,
                                        logDetails, ip_address, username ))
            print(f"SQL Error: {ex}")

    def log_to_file(self, query, params):
        """Logs failed SQL queries to a file."""
        try:
            with open(self.LOG_FILE_PATH, "a") as file:
                file.write(f"Query: {query}\nParams: {params}\n")
        except Exception as ex:
            print(f"Error writing to log file: {ex}")

    def process_old_log_entries(self):
        """Processes and executes previously failed SQL queries from the log file."""
        if not os.path.exists(self.LOG_FILE_PATH):
            return

        failed_queries = []
        datetime_pattern = re.compile(r"datetime\.datetime\((.*?)\)")
        
        try:
            with open(self.LOG_FILE_PATH, "r") as file:
                log_lines = file.readlines()

            queries = []
            params = []
            for i in range(0, len(log_lines), 6):
                query = " ".join(log_lines[i:i+5]).replace("Query:", "").strip()
                param = log_lines[i+5].replace("Params:", "").strip()
                param_cleaned = datetime_pattern.sub(self.replace_datetime, param)
                try:
                    param_tuple = ast.literal_eval(param_cleaned)
                    queries.append(query)
                    params.append(param_tuple)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing params: {e}")

            for query, param in zip(queries, params):
                with pyodbc.connect(self.CONNECTION_STRING) as connection:
                    cursor = connection.cursor()
                    try:
                        cursor.execute(query, *param)
                        connection.commit()
                    except Exception as sql_ex:
                        print(f"SQL Execution Error: {sql_ex}")
                        failed_queries.append((query, param))

            if failed_queries:
                with open(self.LOG_FILE_PATH, "w") as file:
                    for q, p in failed_queries:
                        file.write(f"Query: {q}\nParams: {p}\n")
            else:
                os.remove(self.LOG_FILE_PATH)

        except Exception as ex:
            print(f"Error processing log file: {ex}")
