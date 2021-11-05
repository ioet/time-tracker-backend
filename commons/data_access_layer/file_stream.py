import os
from azure.storage.blob.blockblobservice import BlockBlobService

ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')

class FileStream:
    def __init__(self, account_name:str, container_name:str):
        """
        Initialize the FileStream object. which is used to get the file stream from Azure Blob Storage.
        `account_name`: The name of the Azure Storage account.
        `container_name`: The name of the Azure Storage container.
        """
        self.account_name = account_name
        self.container_name = container_name
        self.blob_service = BlockBlobService(account_name=self.account_name, account_key=ACCOUNT_KEY)

    def get_file_stream(self, filename:str):
        import tempfile 
        try:
            local_file = tempfile.NamedTemporaryFile()
            self.blob_service.get_blob_to_stream(self.container_name, filename, stream=local_file)

            local_file.seek(0)
            return local_file
        except Exception as e:
            print(e)
            return None