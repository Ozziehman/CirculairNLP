import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

from neo4j import GraphDatabase
import base64
import json

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

class neo4j_upload:
    def neo4j_query_text(self, tx, file, metadata, paragraph, sentences, page_num, block_no):
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                tx.run("""
                    MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                    MERGE (p:Paragraph {name: 'Paragraph', paragraph: $paragraph, paragraph_page_num: $page_num, block_no: $block_no})
                    MERGE (f)-[:CONTAINS]->(p)
                    MERGE (s:Sentence {name: 'Sentence' , sentence: $sentence, sentence_page_num: $page_num})
                    MERGE (p)-[:CONTAINS]->(s)
                    MERGE (w:Word {name: 'Word', word: $word, word_page_num: $page_num})
                    MERGE (s)-[:CONTAINS]->(w)
                """, file=file, metadata=metadata, paragraph=paragraph, sentence=sentence, page_num=page_num, block_no=block_no, word=word)
    
    def neo4j_query_image(self, tx, file, images):
        for image_name, image in images:
            tx.run("""
                MERGE (f:File {name: 'File', file: $file})
                MERGE (i:Image {name: 'Image', image: $image_name, contents: $image})
                MERGE (f)-[:CONTAINS]->(i)
            """, file=file, image_name=image_name, image=image)
        
    def neo4j_query_table(self, tx, file, tables):
        for table_name, table in tables:
            tx.run("""
                MERGE (f:File {name: 'File', file: $file})
                MERGE (t:Table {name: 'Table', table: $table_name, contents: $table})
                MERGE (f)-[:CONTAINS]->(t)
            """, file=file, table_name=table_name, table=table)
        
    def main(self, output_file, upload_text: bool, upload_tables: bool, upload_images: bool):
        """Uploads data to Neo4j database."""
        print(f"loaded: {output_file}")
        # Upload text
        if upload_text and os.path.exists(os.path.join(output_file, "extracted_text_blocks.json")):
            print("Uploading text to Neo4j.")
            with driver.session() as session:
                # Read text from file
                with open(os.path.join(output_file, "extracted_text_blocks.json"), "r") as f:
                    text = json.load(f)
                with open(os.path.join(output_file, "metadata.json"), "r") as f:
                    metadata = f.read()
                for json_block in text:
                    paragraph = json_block["lines"]
                    page_num = json_block["page_num"] 
                    block_no = json_block["block_no"]
                    sentences = []   
                    for sentence in paragraph.split("."): # Change later to AI generated sentence splits
                        sentences.append(sentence)
                    session.execute_write(self.neo4j_query_text, file=f"File: {output_file}", metadata=metadata, paragraph=paragraph, sentences=sentences, page_num=page_num, block_no=block_no)
            print("Text uploaded to Neo4j.")
        else:
            print("No text file found.")     
        
        # Upload tables
        if upload_tables and os.path.exists(os.path.join(output_file, "tables")):
            print("Uploading tables to Neo4j.")
            with driver.session() as session:
                table_dir = os.path.join(output_file, "tables")
                table_files = os.listdir(table_dir)
                tables = [] # list of tuples
                for index, table_file in enumerate(table_files):
                    with open(os.path.join(table_dir, table_file), "r", encoding="utf-8") as f:
                        table_content = f.read()
                        table_name = f"{table_file}"
                        tables.append((table_name, table_content))
                            
                session.execute_write(self.neo4j_query_table, file=f"File: {output_file}", tables=tables)
            print("Tables uploaded to Neo4j.")
        else:
            print("No tables found.")
            
        # Upload images
        if upload_images and os.path.exists(os.path.join(output_file, "images")):
            print("Uploading images to Neo4j.")
            with driver.session() as session:
                image_dir = os.path.join(output_file, "images")
                image_files = os.listdir(image_dir)
                images = [] #list of tuples
                for index, image_file in enumerate(image_files):
                    with open(os.path.join(image_dir, image_file), "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("utf-8")
                        image_name = f"{image_file}"
                        images.append((image_name, encoded_image))
                
                session.execute_write(self.neo4j_query_image, file=f"File: {output_file}", images=images)
            print("Images uploaded to Neo4j.")
        else:
            print("No images found.")

# delete all nodes:  MATCH (n) DETACH DELETE n