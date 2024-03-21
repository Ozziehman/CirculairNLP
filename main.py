# IMPORT EVERYTHING HERE
from Utils.FileDataExtraction import muPDF_read_layer
from Utils.FileDataStorage import neo4j_upload_layer

mprl = muPDF_read_layer.muPDF_reader_layer()
n4ul = neo4j_upload_layer.neo4j_upload_layer()

mprl.ParseAllFiles("InputFiles") #parse all files in the input folder
n4ul.upload_all_files("OutputFiles") #upload all files in the output folder