import os
from neo4j import GraphDatabase
import base64
import json

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

class Neo4j_Uploader:
    def __init__(self):
        pass
    
    def neo4j_query_text(self, tx, file, metadata, json_block):
        # get data from json block
        lines = json_block["lines"]
        page_num = json_block["page_num"]
        block_no = json_block["block_no"] 
        block_coords = json_block["coords"]

        words = lines.split()     
        for word_no, word in enumerate(words, start=0):
            tx.run("""
                // Create a file node if it doesn't exist
                MERGE (f:File {name: 'File', file: $file, metadata: $metadata})

                // Create a page node if it doesn't exist
                MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                MERGE (f)-[:CONTAINS]->(p)

                // Create a block node if it doesn't exist
                MERGE (b:Block {name: 'Block', page_num: $page_num, block_no: $block_no, block_coords: $block_coords, block_from_file: $file})
                MERGE (p)-[:CONTAINS]->(b)
                
                // Create a lines node if it doesn't exist
                MERGE (l:Lines {name: 'Lines' , lines: $lines, page_num: $page_num, block_no: $block_no, lines_from_file: $file})
                MERGE (b)-[:CONTAINS]->(l)
                
                // Create a word node if it doesn't exist
                MERGE (w:Word {name: 'Word', word: $word, page_num: $page_num, block_no: $block_no, word_from_file: $file, word_no: $word_no})
                MERGE (l)-[:CONTAINS]->(w)
            """, file=file, metadata=metadata, lines=lines, page_num=page_num+1,  #page_num+1 because page_num starts from 0 in the json file this makes it match with tables and image
            block_no=block_no, word=word, word_no=word_no, block_coords=block_coords)
    
    def neo4j_query_organize_pages(self, tx):
        """Organizes pages in order."""
        tx.run("""
            // Organize pages in order
            MATCH (f:File)-[:CONTAINS]->(p:Page)
            WITH f, p ORDER BY toInteger(p.page_num)
            WITH f, collect(p) as pages
            WITH f, apoc.coll.pairsMin(pages) as pairs
            UNWIND pairs as pair
            WITH f, pair[0] as page1, pair[1] as page2
            MERGE (page1)-[:NEXT_PAGE]->(page2)
        """)

    def neo4j_query_organize_blocks(self, tx):
        """Organizes blocks in order."""
        tx.run("""
            // Organize blocks in order
            MATCH (p:Page)-[:CONTAINS]->(b:Block)
            WITH p, b ORDER BY toInteger(b.block_no)
            WITH p, collect(b) as blocks
            WITH p, apoc.coll.pairsMin(blocks) as pairs
            UNWIND pairs as pair
            WITH pair[0] as block1, pair[1] as block2
            MERGE (block1)-[:NEXT_BLOCK]->(block2)
        """)

    # def neo4j_query_organize_lines(self, tx):
    #     """Organizes lines in order."""
    #     tx.run("""
    #         // Organize lines in order
    #         MATCH (b:Block)-[:CONTAINS]->(l:line)
    #         WITH b, l ORDER BY toInteger(l.line_no)
    #         WITH b, collect(s) as lines
            # WITH b, apoc.coll.pairsMin(lines) as pairs
    #         UNWIND pairs as pair
            # WITH pair[0] as line1, pair[1] as line2
    #         MERGE (line1)-[:NEXT_LINE]->(line2)
    #     """)

    def neo4j_query_organize_words(self, tx):
        """Organizes words in order."""
        tx.run("""
            // Organize words in order
            MATCH (l:Lines)-[:CONTAINS]->(w:Word)
            WITH l, w ORDER BY toInteger(w.word_no)
            WITH l, collect(w) as words
            WITH l, apoc.coll.pairsMin(words) as pairs
            UNWIND pairs as pair
            WITH pair[0] as word1, pair[1] as word2
            MERGE (word1)-[:NEXT_WORD]->(word2)
        """)

    def neo4j_query_connect_matching_words(self, tx):
        """Connects matching words in the Neo4j database, withing the same page."""
        tx.run("""
            // Connect matching words
            MATCH (w1:Word)
            // Parameters on what to match on, this can be changed but will heavily impact performance
            WITH w1.word as word, w1.word_from_file as file, w1.page_num as page, collect(w1) as words
            UNWIND words as w1
            UNWIND words as w2
            WITH w1, w2 WHERE id(w1) < id(w2)
            MERGE (w1)-[:MATCHES]-(w2)
        """)
        
        
    def neo4j_query_image(self, tx, file, metadata): 
        images = []
        image_dir = os.path.join(file, "images")
        image_files = os.listdir(image_dir)
        for index, image_file in enumerate(image_files):
            # image files have the format "page_{page number}_image_{index}.png"
            with open(os.path.join(image_dir, image_file), "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
                image_name = f"{image_file}"
                image_page_num = int(self.find_page_number(f"{image_file}"))
                images.append((image_name, encoded_image, image_page_num))
        for image_name, image, page_num in images:
            tx.run("""
                // Create a file node if it doesn't exist
                MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                
                // Create a page node if it doesn't exist
                MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                MERGE (f)-[:CONTAINS]->(p)
                
                // Create an image node if it doesn't exist
                MERGE (i:Image {name: 'Image', imagename: $image_name, contents: $image, page: $page_num, file: $file})
                MERGE (p)-[:CONTAINS]->(i)
            """, file=file, image_name=image_name, page_num=page_num+1, image=image, metadata=metadata)
        
    def neo4j_query_table(self, tx, file, metadata):
        tables = []
        table_dir = os.path.join(file, "tables")
        table_files = os.listdir(table_dir)
        for index, table_file in enumerate(table_files):
            # table files have the format "page_{page number}_table_{index}.md"
            with open(os.path.join(table_dir, table_file), "r", encoding="utf-8") as f:
                table_content = f.read()
                table_name = f"{table_file}"
                table_page_num = int(self.find_page_number(f"{table_file}"))
                tables.append((table_name, table_content, table_page_num))
        for table_name, table, page_num in tables:
            tx.run("""
                // Create a file node if it doesn't exist
                MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                
                // Create a page node if it doesn't exist
                MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                MERGE (f)-[:CONTAINS]->(p)
                
                // Create a table node if it doesn't exist
                MERGE (t:Table {name: 'Table', tablename: $table_name, contents: $table, page: $page_num, file: $file})
                MERGE (p)-[:CONTAINS]->(t)
            """, file=file, table_name=table_name, page_num=page_num, table=table, metadata=metadata)
        
    def upload_data(self, output_file, upload_text: bool, upload_tables: bool, upload_images: bool):
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
                # iterate over text blocks(json_block) and upload them to Neo4j
                for json_block in text:
                    session.execute_write(self.neo4j_query_text, file=output_file, metadata=metadata, json_block=json_block)
            print("Text uploaded to Neo4j.")
        else:
            if not upload_text:
                print("Text upload disabled.")
            print("No 'extracted_text_blocks.json' file found.")     
        
        # Upload tables
        if upload_tables and os.path.exists(os.path.join(output_file, "tables")):
            print("Uploading tables to Neo4j.")
            with open(os.path.join(output_file, "metadata.json"), "r") as f:
                metadata = f.read()
            with driver.session() as session:
                session.execute_write(self.neo4j_query_table, file=output_file, metadata=metadata)
            print("Tables uploaded to Neo4j")
        else:
            if not upload_tables:
                print("Table upload disabled.")
            print("No tables found.")
            
        # Upload images
        if upload_images and os.path.exists(os.path.join(output_file, "images")):
            print("Uploading images to Neo4j.")
            with open(os.path.join(output_file, "metadata.json"), "r") as f:
                metadata = f.read()
            with driver.session() as session:
                session.execute_write(self.neo4j_query_image, file=output_file, metadata=metadata)
            print("Images uploaded to Neo4j")
        else:
            if not upload_images:
                print("Image upload disabled.")
            print("No images found.")

    def structurize_neo4j_database(self):       
        """"Structurizes the Neo4j database. Puts Pages, blocks, lines and words in order. Connects matching words."""
        with driver.session() as session:
            print("Making relations in between pages, blocks, lines and words. . . ")
            session.execute_write(self.neo4j_query_organize_pages)
            session.execute_write(self.neo4j_query_organize_blocks)
            #session.execute_write(self.neo4j_query_organize_lines)
            session.execute_write(self.neo4j_query_organize_words)
            print("Matching similar words. . . ")
            session.execute_write(self.neo4j_query_connect_matching_words)    
                
    def find_page_number(self, input_string):
        substrings = input_string.split('_')
        return substrings[1]
    
# delete all nodes:  MATCH (n) DETACH DELETE n