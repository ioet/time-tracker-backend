import os
from azure.storage.blob import BlobServiceClient
from utils.azure_users import AzureConnection 


class FileStream():
    CONNECTION_STRING = AzureConnection().get_blob_storage_connection_string() 
    container_name: str

    def __init__(self, container_name: str):
        """
        Initialize the FileStream object. which is used to get the file stream from Azure Blob Storage.
        `container_name`: The name of the Azure Storage container.
        """
        self.container_name = container_name

    def get_file_stream(self, file_name: str):
        if self.CONNECTION_STRING is None:
            print("No connection string")
            return None

        try:
            account = BlobServiceClient.from_connection_string(
                self.CONNECTION_STRING)
            value = account.get_blob_client(self.container_name, file_name)
            file = value.download_blob().readall()
            print("Connection string is valid")
            return file
        except Exception as e:
            print(f'Error: {e}')
            return None
