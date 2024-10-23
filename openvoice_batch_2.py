import os
import mysql.connector
from datetime import datetime
import requests,csv


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
            self.mysql_cursor.execute("SELECT id, word_1 FROM bot_mecab_words2 WHERE status_flg = 1")
            records = self.mysql_cursor.fetchall()
            return records

        except Exception as e:
            print(f"Error fetching processed records from MySQL: {e}")

    def fetch_unprocessed_records(self, limit=1):
        try:
            self.mysql_cursor.execute("SELECT id, word_1 FROM bot_mecab_words2 WHERE status_flg IS NULL LIMIT %s", (limit,))
            records = self.mysql_cursor.fetchall()
            return records
        except Exception as e:
            print(f"Error fetching unprocessed records from MySQL: {e}")
            return []

    def update_record_status(self, record_id, status):
        try:
            self.mysql_cursor.execute("UPDATE bot_mecab_words2 SET status_flg = %s , updated_at = NOW() WHERE id = %s", (status, record_id))
            self.mysql_conn.commit()
        except Exception as e:
            print(f"Error updating record status in MySQL: {e}")


    def send_to_openvoice_and_update_records(self):
    
        records = self.fetch_unprocessed_records(limit=1)

        if not records:
            print("No unprocessed records found.")
            self.generate_csv()
            return

        for record in records:
            record_id, text = record

            # Generate the file path
            file_path = f"{record_id}_{lang}.wav"

            try:
                # Send to OpenVoice
                openvoice_service_url = 'http://localhost:5001/get_openvoice_batch'
                payload = {
                    'file_path': file_path,
                    'text': text,
                    'lang': lang
                }
                response = requests.post(openvoice_service_url, json=payload)

                if response.status_code == 200:
                    audio_path = response.json().get('audio_path')
                    self.update_record_status(record_id, 1)
                    print(f"OpenVoice processing complete for record id {record_id}")
                else:
                    print(f"Error with id {record_id}: {response.json().get('error')}")
                    self.update_record_status(record_id, 9)  # Mark as failed to process

            except Exception as e:
                print(f"Error with id {record_id}: {str(e)}")
                self.update_record_status(record_id, 9)  # Mark as failed to process  


    def generate_csv(self):
        records = self.fetch_processed_records()
        if not records:
            print("No processed records found.")
            return

        # Define the CSV file path
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        csv_file_path = f"/data/openv_{lang}.csv"

        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['audio_file', 'transcription'])
                for record in records:
                    record_id, text = record
                    writer.writerow([f"audio_files/{record_id}_{lang}.wav", text])

            print(f"CSV file created at: {csv_file_path}")

        except Exception as e:
            print(f"Error creating CSV file: {e}")

# Example usage
db_connector = DatabaseConnector()
batch = OpenvoiceBatch(db_connector)
batch.send_to_openvoice_and_update_records()






