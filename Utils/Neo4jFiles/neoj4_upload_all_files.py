import os
from neo4j_upload import neo4j_upload


output_files = "OutputFiles"
output_files = [os.path.join(output_files, f) for f in os.listdir(output_files) if os.path.isdir(os.path.join(output_files, f))]
for output_file in output_files:
    print(output_file)
    n4ju = neo4j_upload()
    n4ju.main(output_file, upload_text=True, upload_tables=True, upload_images=True) #output file is the path of the full folders with contents