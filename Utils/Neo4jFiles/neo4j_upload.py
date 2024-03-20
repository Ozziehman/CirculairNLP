import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

from neo4j import GraphDatabase
import base64
import json

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

class neo4j_upload:
    def neo4j_query_text(self, tx, file, metadata, json_block):
        block_lines = json_block["lines"]
        page_num = json_block["page_num"]
        block_no = json_block["block_no"]
        sentences = block_lines.split(".")   

        for sentence_no, sentence in enumerate(sentences, start=0):
            words = sentence.split()     
            for word_no, word in enumerate(words, start=0):
                tx.run("""
                    MERGE (f:File {name: 'File', file: $file, metadata: $metadata})

                    MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                    MERGE (f)-[:CONTAINS]->(p)

                    MERGE (b:Block {name: 'Block', block_lines: $block_lines, page_num: $page_num, block_no: $block_no, block_from_file: $file})
                    MERGE (p)-[:CONTAINS]->(b)
                    
                    MERGE (s:Sentence {name: 'Sentence' , sentence: $sentence, page_num: $page_num, block_no: $block_no, sentence_from_file: $file, sentence_no: $sentence_no})
                    MERGE (b)-[:CONTAINS]->(s)
                    
                    MERGE (w:Word {name: 'Word', word: $word, page_num: $page_num, block_no: $block_no, sentence_no: $sentence_no, word_from_file: $file, word_no: $word_no})
                    MERGE (s)-[:CONTAINS]->(w)
                """, file=file, metadata=metadata, block_lines=block_lines, sentence=sentence, page_num=page_num, 
                block_no=block_no, word=word, sentence_no=sentence_no, word_no=word_no)
    
    def neo4j_query_image(self, tx, file, metadata): 
        images = []
        image_dir = os.path.join(file, "images")
        image_files = os.listdir(image_dir)
        for index, image_file in enumerate(image_files):
            with open(os.path.join(image_dir, image_file), "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
                image_name = f"{image_file}"
                image_page_num = self.find_page_number(f"{image_file}")
                images.append((image_name, encoded_image, image_page_num))
        for image_name, image, page_num in images:
            tx.run("""
                MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                MERGE (f)-[:CONTAINS]->(p)
                MERGE (i:Image {name: 'Image', imagename: $image_name, contents: $image, page: $page_num, file: $file})
                MERGE (p)-[:CONTAINS]->(i)
            """, file=file, image_name=image_name, page_num=page_num, image=image, metadata=metadata)
        
    def neo4j_query_table(self, tx, file, metadata):
        tables = []
        table_dir = os.path.join(file, "tables")
        table_files = os.listdir(table_dir)
        for index, table_file in enumerate(table_files):
            with open(os.path.join(table_dir, table_file), "r", encoding="utf-8") as f:
                table_content = f.read()
                table_name = f"{table_file}"
                table_page_num = self.find_page_number(f"{table_file}")
                tables.append((table_name, table_content, table_page_num))
        for table_name, table, page_num in tables:
            tx.run("""
                MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                MERGE (f)-[:CONTAINS]->(p)
                MERGE (t:Table {name: 'Table', tablename: $table_name, contents: $table, page: $page_num, file: $file})
                MERGE (p)-[:CONTAINS]->(t)
            """, file=file, table_name=table_name, page_num=page_num, table=table, metadata=metadata)
        
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
                    session.execute_write(self.neo4j_query_text, file=output_file, metadata=metadata, json_block=json_block)
            print("Text uploaded to Neo4j.")
        else:
            print("No text file found, or option disabled.")     
        
        # Upload tables
        if upload_tables and os.path.exists(os.path.join(output_file, "tables")):
            print("Uploading tables to Neo4j.")
            with open(os.path.join(output_file, "metadata.json"), "r") as f:
                metadata = f.read()
            with driver.session() as session:
                session.execute_write(self.neo4j_query_table, file=output_file, metadata=metadata)
            print("Tables uploaded to Neo4j")
        else:
            print("No tables found, or option disabled.")
            
        # Upload images
        if upload_images and os.path.exists(os.path.join(output_file, "images")):
            print("Uploading images to Neo4j.")
            with open(os.path.join(output_file, "metadata.json"), "r") as f:
                metadata = f.read()
            with driver.session() as session:
                session.execute_write(self.neo4j_query_image, file=output_file, metadata=metadata)
            print("Images uploaded to Neo4j")
        else:
            print("No images found, or option disabled.")

    def find_page_number(self, input_string):
        substrings = input_string.split('_')
        return substrings[1]
    
# delete all nodes:  MATCH (n) DETACH DELETE n