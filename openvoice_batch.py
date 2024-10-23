import os
import mysql.connector
from datetime import datetime
import requests,csv
import uuid

lang="JP";

class DatabaseConnector:
    def __init__(self):
        self.host = 'xxx'
        self.user = 'xxx'
        self.password = 'xxx'
        self.database = 'xxx'
        self.charset = 'utf8mb4'
        
    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset
        )

    def close_connection(self, conn, cursor):
        if cursor:
            cursor.close()
        if conn:
            conn.close()

class OpenvoiceBatch:

    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.mysql_conn = self.db_connector.connect()
        self.mysql_cursor = self.mysql_conn.cursor()


    def fetch_processed_records(self):
        try:
            self.mysql_cursor.execute("SELECT id, answer_memo FROM bot_qanda WHERE status_flg = 1")
            records = self.mysql_cursor.fetchall()
            return records

        except Exception as e:
            print(f"Error fetching processed records from MySQL: {e}")

    def fetch_unprocessed_records(self, limit=1):
        try:
            self.mysql_cursor.execute("SELECT id, answer_memo FROM bot_qanda WHERE status_flg IS NULL LIMIT %s", (limit,))
            records = self.mysql_cursor.fetchall()
            return records
        except Exception as e:
            print(f"Error fetching unprocessed records from MySQL: {e}")
            return []

    def update_record_status(self, record_id,file_path_2, status):
        try:
            self.mysql_cursor.execute("UPDATE bot_qanda SET file_path_2= %s , status_flg = %s , updated_at = NOW() WHERE id = %s", (file_path_2,status, record_id))
            self.mysql_conn.commit()
        except Exception as e:
            print(f"Error updating record status in MySQL: {e}")


    def send_to_openvoice_and_update_records(self):
    
        records = self.fetch_unprocessed_records(limit=1)

        if not records:
            print("No unprocessed records found.")
           
            return

        for record in records:
            record_id, text = record

            # Generate the file path
            random_str = uuid.uuid4().hex[:16]
            file_path = f"{record_id}_{random_str}_{lang}.wav"

            try:
                # Send to OpenVoice
                openvoice_service_url = 'http://localhost:5002/get_openvoice_batch_2'
                payload = {
                    'file_path': file_path,
                    'text': text,
                    'lang': lang
                }
                response = requests.post(openvoice_service_url, json=payload)
                print(text)
                if response.status_code == 200:
                    audio_path = response.json().get('audio_path')
                    self.update_record_status(record_id,audio_path, 1)
                    print(f"OpenVoice processing complete for record id {record_id}")
                else:
                    print(f"Error with id {record_id}: {response.json().get('error')}")
                    self.update_record_status(record_id,null,9)  # Mark as failed to process

            except Exception as e:
                print(f"Error with id {record_id}: {str(e)}")
                self.update_record_status(record_id,null, 9)  # Mark as failed to process  




# Example usage
db_connector = DatabaseConnector()
batch = OpenvoiceBatch(db_connector)
batch.send_to_openvoice_and_update_records()



#audio_mp3 = AudioSegment.from_wav(file_path)
#audio_mp3 = audio_mp3.set_frame_rate(16000)
#mp3_file_path = file_path.replace('.wav', '.mp3')
#audio_mp3.export(result_folder+"audio_files/"+mp3_file_path, format="mp3")
#print("Generated MP3 file path:", result_folder+"audio_files/"+mp3_file_path)



