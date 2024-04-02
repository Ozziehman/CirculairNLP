# IMPORT EVERYTHING HERE
from Utils.FileDataExtraction import muPDF_reader_layer
from Utils.FileDataStorage import neo4j_layer


mprl = muPDF_reader_layer.muPDF_reader_layer()
n4l = neo4j_layer.neo4j_layer()


#mprl.ParseAllFiles("InputFiles") #parse all files in the input folder
n4l.upload_all_files("OutputFiles", upload_text=True, upload_tables=True, upload_images=True, interpreted_structure=True) #upload all files in the output folder
n4l.structurize_neo4j_database() #structurize the db