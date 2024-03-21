import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)
from neo4j_upload import neo4j_upload
 
class neo4j_upload_layer:
    def upload_all_files(self, output_files: str):
        """upload all files in this path to the neo4j database, input should be the fodler of the output files"""
        output_files = [os.path.join(output_files, f) for f in os.listdir(output_files) if os.path.isdir(os.path.join(output_files, f))] #list of paths
        for output_file in output_files:
            n4ju = neo4j_upload()
            n4ju.main(output_file, upload_text=True, upload_tables=True, upload_images=True) #output file is the path of the full folders with contents
            # strucurize the database
            n4ju.structurize_neo4j_database()
    
    def upload_single_file(self, output_file: str):
        """upload a sing output file to the neo4j database, input should be the path of the output file folder"""
        n4ju = neo4j_upload()
        n4ju.main(output_file, upload_text=True, upload_tables=True, upload_images=True) #output file is the path of the full folders with contents
        # strucurize the database
        n4ju.structurize_neo4j_database()

neo4j_upload_layer().upload_all_files("OutputFiles") #upload all files in the output folder