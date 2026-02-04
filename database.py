import os
import datetime
import base64
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
        Store document metadata and content (simulating blockchain/secure storage)
        """
        if not self.db:
            return None

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

    def get_lifecycles(self):
        if not self.db: return {}
        try:
            cursor = self.db.lifecycles.find({})
            return {item['hash']: item for item in cursor}
        except:
            return {}

    def save_lifecycle(self, doc_hash, doc_type, metadata, deadlines):
        if not self.db: return
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
        if not self.db: return False
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
