import os
current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

from neo4j import GraphDatabase
import base64

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

class neo4j_upload:
    def neo4j_query_text(self, tx, file, chapter, paragraph, sentence):
        words = sentence.split()
        for word in words:
            tx.run("""
                MERGE (f:File {name: $file})
                MERGE (c:Chapter {name: $chapter})
                MERGE (f)-[:CONTAINS]->(c)
                MERGE (p:Paragraph {name: $paragraph})
                MERGE (c)-[:CONTAINS]->(p)
                MERGE (s:Sentence {name: $sentence})
                MERGE (p)-[:CONTAINS]->(s)
                MERGE (w:Word {name: 'Word', contents: $word})
                MERGE (s)-[:CONTAINS]->(w)
            """, file=file, chapter=chapter, paragraph=paragraph, sentence=sentence, word=word)
    
    def neo4j_query_image(self, tx, file, chapter, images):
        for image_name, image in images:
            tx.run("""
                MERGE (f:File {name: $file})
                MERGE (c:Chapter {name: $chapter})
                MERGE (f)-[:CONTAINS]->(c)
                MERGE (i:Image {name: $image_name, contents: $image})
                MERGE (c)-[:CONTAINS]->(i)
            """, file=file, chapter=chapter, image_name=image_name, image=image)
    
    def neo4j_query_table(self, tx, file, chapter, paragraph, tables):
        for table_name, table in tables:
            tx.run("""
                MERGE (f:File {name: $file})
                MERGE (c:Chapter {name: $chapter})
                MERGE (f)-[:CONTAINS]->(c)
                MERGE (p:Paragraph {name: $paragraph})
                MERGE (c)-[:CONTAINS]->(p)  
                MERGE (t:Table {name: $table_name, contents: $table})
                MERGE (p)-[:CONTAINS]->(t)
            """, file=file, chapter=chapter, paragraph=paragraph, table_name=table_name, table=table)
        
    def main(self, output_file, upload_text: bool, upload_tables: bool, upload_images: bool):
        """Uploads data to Neo4j database."""
        # Upload text
        if upload_text and os.path.exists(os.path.join(output_file, "text.txt")):
            with driver.session() as session:
                # Read text from file
                text = open(os.path.join(output_file, "text.txt"), "r", encoding='utf-8').read()
                sentences = text.split(".")
                for sentence in sentences:
                    # Replace with actual chapters and paragraphs
                    session.execute_write(self.neo4j_query_text, file=f"File: {output_file}", chapter=f"Chapter 1 from file: {output_file}", paragraph=f"Paragraph 1 from file {output_file}", sentence=sentence)
        else:
            print("No text file found.")     
        
        # Upload tables
        if upload_tables and os.path.exists(os.path.join(output_file, "tables")):
            with driver.session() as session:
                table_dir = os.path.join(output_file, "tables")
                table_files = os.listdir(table_dir)
                tables = [] # list of tuples
                for index, table_file in enumerate(table_files):
                    with open(os.path.join(table_dir, table_file), "r", encoding="utf-8") as f:
                        table_content = f.read()
                        table_name = f"{table_file}_{index}"
                        tables.append((table_name, table_content))
                            
                session.write_transaction(self.neo4j_query_table, file=f"File: {output_file}", chapter=f"Chapter 1 from file: {output_file}", paragraph=f"Paragraph 1 from file {output_file}", tables=tables)
        else:
            print("No tables found.")
            
        # Upload images
        if upload_images and os.path.exists(os.path.join(output_file, "images")):
            with driver.session() as session:
                image_dir = os.path.join(output_file, "images")
                image_files = os.listdir(image_dir)
                images = [] #list of tuples
                for index, image_file in enumerate(image_files):
                    with open(os.path.join(image_dir, image_file), "rb") as f:
                        encoded_image = base64.b64encode(f.read()).decode("utf-8")
                        image_name = f"{image_file}_{index}"
                        images.append((image_name, encoded_image))
                
                session.write_transaction(self.neo4j_query_image, file=f"File: {output_file}", chapter=f"Chapter 1 from file: {output_file}", images=images)
        else:
            print("No images found.")

# delete all nodes:  MATCH (n) DETACH DELETE n