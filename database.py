import os
import datetime
import base64
import uuid
import time
import requests
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class NyaySetuDB:
    def __init__(self, uri=None):
        self.uri = uri or os.environ.get('MONGODB_URI')
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        if not self.uri:
            print("WARNING: MONGODB_URI not set. Database features will be disabled.")
            return

        try:
            self.client = MongoClient(self.uri)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            self.db = self.client.get_database('nyaysetu_blockchain')
            print("✅ Successfully connected to MongoDB Atlas")
        except ConnectionFailure:
            print("❌ Server not available")
            self.client = None
        except Exception as e:
            print(f"❌ MongoDB Connection Error: {e}")
            self.client = None

    def store_document(self, doc_type, user_data, pdf_path, doc_hash, ref_num=None):
        """
        Store document metadata and content in the internal NyaySetu tracking DB
        """
        if self.db is None:
            return None

        # Check for blockchain specific data
        user_key = user_data.get('userKey')
        username = user_data.get('username')
        
        # If userKey is provided, also store in the blockchain file_storage
        if user_key:
            print(f"DEBUG: userKey detected, storing in blockchain as well...")
            filename = os.path.basename(pdf_path)
            self.store_in_blockchain(user_key, username, pdf_path, filename)

        try:
            with open(pdf_path, "rb") as pdf_file:
                encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')

            document = {
                "type": doc_type,
                "user_name": user_data.get('name') or user_data.get('deponent_name'),
                "metadata": user_data,
                "hash": doc_hash,
                "reference_number": ref_num,
                "file_content_base64": encoded_string,
                "created_at": datetime.datetime.utcnow(),
                "status": "DRAFTED"
            }

            result = self.db.documents.insert_one(document)
            print(f"✅ Document stored in 'blockchain' section: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing document: {e}")
            return None

    def store_in_blockchain(self, user_key, username, pdf_path, original_filename):
        """
        Store document directly in the format expected by the Blockchain service's 'file_storage' DB
        """
        if self.client is None: return None

        try:
            # Connect to the file_storage database (used by blockchain service)
            bc_db = self.client.get_database('file_storage')
            files_col = bc_db["files"]

            with open(pdf_path, "rb") as pdf_file:
                file_content = pdf_file.read()
                file_size = len(file_content)
                file_base64 = base64.b64encode(file_content).decode('utf-8')

            file_key = str(uuid.uuid4())
            unique_id = str(uuid.uuid4())[:8]
            secure_name = f"{int(time.time()*1000)}_{unique_id}_{original_filename}"

            doc = {
                "file_key": file_key,
                "filename": original_filename, 
                "secure_name": secure_name,   
                "owner": user_key,
                "shared_with": [],
                "file_content": file_base64,
                "file_size": file_size,
                "created_at": time.time()
            }

            files_col.insert_one(doc)
            print(f"✅ Document injected into Blockchain 'file_storage': {file_key}")

            # Notify the blockchain service to add a transaction if URL is known
            bc_service_url = os.environ.get('BLOCKCHAIN_SERVICE_URL')
            if bc_service_url:
                try:
                    tx = {
                        "user": username or "NyaySetu_AI",
                        "v_file": original_filename,
                        "file_key": file_key,
                        "file_data": "Binary Content Stored in DB",
                        "file_size": file_size
                    }
                    requests.post(f"{bc_service_url}/new_transaction", json=tx, timeout=2)
                    print(f"✅ Transaction announced to Blockchain service")
                except Exception as ex:
                    print(f"⚠️ Could not announce to blockchain service: {ex}")

            return file_key
        except Exception as e:
            print(f"❌ Error injecting into Blockchain DB: {e}")
            return None

    def get_lifecycles(self):
        if self.db is None: return {}
        try:
            cursor = self.db.lifecycles.find({})
            return {item['hash']: item for item in cursor}
        except:
            return {}

    def save_lifecycle(self, doc_hash, doc_type, metadata, deadlines):
        if self.db is None: return
        try:
            lifecycle = {
                "hash": doc_hash,
                "document_type": doc_type,
                "created_date": datetime.datetime.utcnow().isoformat(),
                "current_state": "DRAFTED",
                "state_history": [{
                    "state": "DRAFTED",
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "notes": "Document generated"
                }],
                "metadata": metadata,
                "deadlines": deadlines,
                "last_updated": datetime.datetime.utcnow()
            }
            self.db.lifecycles.update_one(
                {"hash": doc_hash},
                {"$set": lifecycle},
                upsert=True
            )
        except Exception as e:
            print(f"❌ Error saving lifecycle to DB: {e}")

    def update_lifecycle_state(self, doc_hash, new_state, notes):
        if self.db is None: return False
        try:
            self.db.lifecycles.update_one(
                {"hash": doc_hash},
                {
                    "$set": {"current_state": new_state, "last_updated": datetime.datetime.utcnow()},
                    "$push": {
                        "state_history": {
                            "state": new_state,
                            "timestamp": datetime.datetime.utcnow().isoformat(),
                            "notes": notes
                        }
                    }
                }
            )
            return True
        except Exception as e:
            print(f"❌ Error updating lifecycle state: {e}")
            return False
