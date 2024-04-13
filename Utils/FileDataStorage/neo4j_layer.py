import os
from Utils.FileDataStorage import neo4j_upload
from Utils.FileDataStorage import neo4j_structure
 
class neo4j_layer:
    def __init__(self):
        pass
    
    def upload_all_files(self, output_folder: str, upload_text: bool = True, upload_tables: bool = True, upload_images: bool = True, interpreted_structure: bool = True):
        """upload all files in this path to the neo4j database, input should be the folder of the output files
        Interpreted structure is like the name states an interpreted structure of the fil ein the neo4j database, this can be used for coreferencing for example."""
        output_files = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if os.path.isdir(os.path.join(output_folder, f))] #list of paths
        for output_file in output_files:
            n4ju = neo4j_upload.Neo4j_Uploader()
            n4ju.upload_data(output_file, upload_text=upload_text, upload_tables=upload_tables, upload_images=upload_images, interpreted_structure=interpreted_structure) #output file is the path of the full folders with contents
            
    def structurize_neo4j_database(self):
        """Structurize the neo4j database"""
        n4st = neo4j_structure.Neo4j_Structurizer()
        n4st.structurize_neo4j_database()
        
    def entity_replacement(self, id):
        """ Replace all references to the entity within a specified paragraph with the entity """
        n4st = neo4j_structure.Neo4j_Structurizer()
        return n4st.coref_replacement(id)