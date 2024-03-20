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
                    // Create a file node if it doesn't exist
                    MERGE (f:File {name: 'File', file: $file, metadata: $metadata})

                    // Create a page node if it doesn't exist
                    MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                    MERGE (f)-[:CONTAINS]->(p)

                    // Create a block node if it doesn't exist
                    MERGE (b:Block {name: 'Block', block_lines: $block_lines, page_num: $page_num, block_no: $block_no, block_from_file: $file})
                    MERGE (p)-[:CONTAINS]->(b)
                    
                    // Create a sentence node if it doesn't exist
                    MERGE (s:Sentence {name: 'Sentence' , sentence: $sentence, page_num: $page_num, block_no: $block_no, sentence_from_file: $file, sentence_no: $sentence_no})
                    MERGE (b)-[:CONTAINS]->(s)
                    
                    // Create a word node if it doesn't exist
                    MERGE (w:Word {name: 'Word', word: $word, page_num: $page_num, block_no: $block_no, sentence_no: $sentence_no, word_from_file: $file, word_no: $word_no})
                    MERGE (s)-[:CONTAINS]->(w)
                """, file=file, metadata=metadata, block_lines=block_lines, sentence=sentence, page_num=page_num, 
                block_no=block_no, word=word, sentence_no=sentence_no, word_no=word_no)
    
    def neo4j_query_organize_pages(self, tx):
        tx.run("""
            // Organize pages in order
            MATCH (f:File)-[:CONTAINS]->(p:Page)
            WITH f, p ORDER BY p.page_num
            WITH f, collect(p) as pages
            WITH f, apoc.coll.pairsMin(pages) as pairs
            UNWIND pairs as pair
            WITH f, pair[0] as page1, pair[1] as page2
            MERGE (page1)-[:NEXT_PAGE]->(page2)
        """)
        
    def neo4j_query_organize_blocks(self, tx):
        tx.run("""
            // Organize blocks in order
            MATCH (p:Page)-[:CONTAINS]->(b:Block)
            WITH p, b ORDER BY b.block_no
            WITH p, collect(b) as blocks
            WITH p, apoc.coll.pairsMin(blocks) as pairs
            UNWIND pairs as pair
            WITH pair[0] as block1, pair[1] as block2
            MERGE (block1)-[:NEXT_BLOCK]->(block2)
        """)
    
    def neo4j_query_organize_sentences(self, tx):
        tx.run("""
            // Organize sentences in order
            MATCH (b:Block)-[:CONTAINS]->(s:Sentence)
            WITH b, s ORDER BY s.sentence_no
            WITH b, collect(s) as sentences
            WITH b, apoc.coll.pairsMin(sentences) as pairs
            UNWIND pairs as pair
            WITH pair[0] as sentence1, pair[1] as sentence2
            MERGE (sentence1)-[:NEXT_SENTENCE]->(sentence2)
        """)

    def neo4j_query_organize_words(self, tx):
        tx.run("""
            // Organize words in order
            MATCH (s:Sentence)-[:CONTAINS]->(w:Word)
            WITH s, w ORDER BY w.word_no
            WITH s, collect(w) as words
            WITH s, apoc.coll.pairsMin(words) as pairs
            UNWIND pairs as pair
            WITH pair[0] as word1, pair[1] as word2
            MERGE (word1)-[:NEXT_WORD]->(word2)
        """)

    def neo4j_query_connect_matching_words(self, tx):
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
            
        
        with driver.session() as session:
            print("Making relations in between pages, blocks, sentences and words. . . ")
            session.execute_write(self.neo4j_query_organize_pages)
            session.execute_write(self.neo4j_query_organize_blocks)
            session.execute_write(self.neo4j_query_organize_sentences)
            session.execute_write(self.neo4j_query_organize_words)
            print("Matching similar words. . . ")
            session.execute_write(self.neo4j_query_connect_matching_words)
        
            
    def find_page_number(self, input_string):
        substrings = input_string.split('_')
        return substrings[1]
    
# delete all nodes:  MATCH (n) DETACH DELETE n