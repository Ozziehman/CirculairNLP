import os
from Utils.FileDataStorage import neo4j_upload
 
class neo4j_upload_layer:
    def __init__(self):
        pass
    
    def upload_all_files(self, output_folder: str):
        """upload all files in this path to the neo4j database, input should be the folder of the output files"""
        output_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if os.path.isdir(os.path.join(output_folder, f))] #list of paths
        for output_file in output_files:
            n4ju = neo4j_upload.Neo4j_Uploader()
            n4ju.upload_data(output_file, upload_text=True, upload_tables=True, upload_images=True) #output file is the path of the full folders with contents
            # strucurize the database
            n4ju.structurize_neo4j_database()
    
    def upload_single_file(self, output_file: str):
        """upload a sing output file to the neo4j database, input should be the path of the output file folder"""
        n4ju = neo4j_upload.Neo4j_Uploader()
        n4ju.upload_data(output_file, upload_text=True, upload_tables=True, upload_images=True) #output file is the path of the full folders with contents
        # strucurize the database
        n4ju.structurize_neo4j_database()