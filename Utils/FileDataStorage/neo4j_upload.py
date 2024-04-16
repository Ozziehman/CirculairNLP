import os
from neo4j import GraphDatabase
import base64
import json
import nltk
from nltk.stem import WordNetLemmatizer

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))


class Neo4j_Uploader:
    def __init__(self):
        nltk.download("wordnet")
        self.lemmatizer = WordNetLemmatizer()
        self.last_title = None
        self.last_subtitle = None
        self.last_paragraph = None
    
    def neo4j_query_interpreted_structure(self, tx, file, json_block, metadata):
        for key, value in json_block.items():
            text_type = key
            for inner_key, inner_value in value.items():
                if inner_key == "text":
                    text = inner_value
                elif inner_key == "blocks":
                    blocks = inner_value
                elif inner_key == "page_num":
                    page_num = inner_value + 1  #page_num+1 because page_num starts from 0 in the json file this makes it match with tables and image
            if "title" in text_type and "sub" not in text_type:  # store title for future connection with subtitles and/or paragraphs
                self.last_title = text
                self.last_subtitle = None  # reset last subtitle when encountered new title
                tx.run("""
                    MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                    MERGE (p:Page {name: 'Page', page_num: $page_num, page_from_file: $file})
                    MERGE (p)-[:BELONGS_TO]->(f)
                    // Create a title node if it doesn't exist
                    MERGE (t:Title {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, title_from_file: $file})
                    MERGE (t)-[:BELONGS_TO]->(p)
                    """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file, metadata=metadata)
            elif "subtitle" in text_type:  # store subtitle for future connection with paragraphs
                self.last_subtitle = text
                tx.run("""
                    // Create a subtitle node if it doesn't exist
                    MERGE (s:Subtitle {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, subtitle_from_file: $file})
                    """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
                if self.last_title: # connect subtitle to the last encountered title if available
                    tx.run("""
                        // Create a title node if it doesn't exist
                        MATCH (t:Title {text: $last_title, page_num: $page_num, title_from_file: $file})
                        MATCH (s:Subtitle {text: $text, page_num: $page_num, subtitle_from_file: $file})
                        MERGE (s)-[:BELONGS_TO]->(t)
                        """, last_title=self.last_title, text=text, file=file, page_num=page_num)
                else: # create standalone subtitle if no title is available
                    tx.run("""
                        // Create a subtitle node if it doesn't exist
                        MERGE (s:Subtitle {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, subtitle_from_file: $file})
                        """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
            elif "paragraph" in text_type:  # connect paragraph to the last encountered subtitle if available
                if self.last_subtitle:
                    tx.run("""
                        // Create a subtitle node if it doesn't exist
                        MATCH (s:Subtitle {text: $last_subtitle, page_num: $page_num, subtitle_from_file: $file})
                        MERGE (p:Paragraph {text: $text, blocks: $blocks, page_num: $page_num, paragraph_from_file: $file})
                        MERGE (p)-[:BELONGS_TO]->(s)
                        """, last_subtitle=self.last_subtitle, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
                else: # create standalone paragraph if no subtitle is available
                    tx.run("""
                        // Create a paragraph node if it doesn't exist
                        MERGE (p:Paragraph {text: $text, blocks: $blocks, page_num: $page_num, paragraph_from_file: $file})
                        """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
            elif "subtext" in text_type: # create standalone subtext as this is not reliable connected to any other node
                tx.run("""
                    // Create a subtext node if it doesn't exist
                    MERGE (t:Subtext {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, subtext_from_file: $file})
                    """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
            else: print("error")
      
    def neo4j_query_hierarchial_interpreted_structure(self, tx, file, json_block, metadata):
        """
        Parses a hierarchical interpreted structure from a JSON block and stores it in a Neo4j graph database.

        Args:
            tx: The Neo4j transaction object.
            file (str): The name of the file being processed.
            json_block (dict): The JSON block containing hierarchical interpreted structure.
            metadata: Additional metadata related to the file.

        Returns:
            None

        """
        for key, value in json_block.items():  
            #print(key)  
            text_type = key
            for inner_key, inner_value in value.items():
                if inner_key == "text":
                    text = inner_value
                elif inner_key == "blocks":
                    blocks = inner_value
                elif inner_key == "page_nums":
                    page_num = inner_value[0] + 1 # TODO Need to implement logic to handle multiple page_nums (maybe)
            if "title" in text_type and "sub" not in text_type:
                self.last_title = text
                tx.run("""
                    MERGE (f:File {name: 'File', file: $file, metadata: $metadata})
                    MERGE (t:Title {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, title_from_file: $file})
                    MERGE (t)-[:BELONGS_TO]->(f)
                    """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file, metadata=metadata)
            elif "subtitle" in text_type:
                self.last_subtitle = text
                tx.run("""
                    MERGE (s:Subtitle {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, subtitle_from_file: $file})
                    WITH s
                    MATCH (t:Title {text: $last_title, title_from_file: $file})
                    MERGE (s)-[:BELONGS_TO]->(t)
                    """, text=text, last_title=self.last_title, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
            elif "paragraph" in text_type:
                self.last_paragraph = text
                tx.run("""
                    MERGE (p:Paragraph {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, paragraph_from_file: $file})
                    """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
                if self.last_subtitle:
                    tx.run("""
                        MATCH (s:Subtitle {text: $last_subtitle, page_num: $page_num, subtitle_from_file: $file})
                        MATCH (p:Paragraph {text: $text, page_num: $page_num, paragraph_from_file: $file})
                        MERGE (p)-[:BELONGS_TO]->(s)
                        """, last_subtitle=self.last_subtitle, text=text, file=file, page_num=page_num)
            elif "subtext" in text_type:
                tx.run("""
                    MERGE (t:Subtext {name: $text_type, text: $text, blocks: $blocks, page_num: $page_num, subtext_from_file: $file})
                    """, text=text, blocks=blocks, page_num=page_num, text_type=text_type, file=file)
                if self.last_paragraph:
                    tx.run("""
                        MATCH (p:Paragraph {text: $last_paragraph, page_num: $page_num, paragraph_from_file: $file})
                        MATCH (t:Subtext {text: $text, page_num: $page_num, subtext_from_file: $file})
                        MERGE (t)-[:BELONGS_TO]->(p)
                        """, last_paragraph=self.last_paragraph, text=text, file=file, page_num=page_num)
                
    def neo4j_query_unravel_paragraphs(self, tx, file):
        """
        Creates paragraph_word nodes from all words in a paragraph and connects each word to paragraphs with BELONGS_TO relation.

        Args:
            tx: The Neo4j transaction object.
            file (str): The name of the file containing the paragraphs.

        Returns:
            None

        """
        tx.run("""
            // Split paragraph into Paragraph_Word nodes
            MATCH (p:Paragraph {paragraph_from_file: $file})
            WITH p, split(p.text, ' ') as words
            UNWIND range(0, size(words)-1) as index
            MERGE (w:Paragraph_Word {word: words[index], index: index, word_from_file: $file, page_num: p.page_num})
            MERGE (w)-[:BELONGS_TO]->(p)
        """, file=file)

        paragraph_word_nodes = tx.run("MATCH (pw:Paragraph_Word {word_from_file: $file}) RETURN pw", file=file).data()

        for node in paragraph_word_nodes:
            word = node['pw']['word']
            lemma = self.lemmatizer.lemmatize(word)
            tx.run("MATCH (pw:Paragraph_Word {word: $word, word_from_file: $file}) SET pw.lemma = $lemma", word=word, lemma=lemma, file=file)
    
    def neo4j_query_text(self, tx, file, metadata, json_block):
        """
        Stores text data into a Neo4j graph database.

        Args:
            tx: The Neo4j transaction object.
            file (str): The name of the file containing the text.
            metadata: Additional metadata related to the file.
            json_block (dict): The JSON block containing text data.

        Returns:
            None

        """
        # get data from json block
        lines = json_block["lines"]
        page_num = json_block["page_num"] + 1  #page_num+1 because page_num starts from 0 in the json file this makes it match with tables and image
        block_no = json_block["block_no"] 
        block_coords = json_block["coords"]

        words = lines.split()     
        for word_no, word in enumerate(words, start=0):
            lemma = self.lemmatizer.lemmatize(word)
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
                MERGE (w:Word {name: 'Word', word: $word, page_num: $page_num, block_no: $block_no, word_from_file: $file, word_no: $word_no, lemma: $lemma})
                MERGE (l)-[:CONTAINS]->(w)
            """, file=file, metadata=metadata, lines=lines, page_num=page_num, 
            block_no=block_no, word=word, word_no=word_no, block_coords=block_coords, lemma=lemma) 
        
    def neo4j_query_image(self, tx, file, metadata):
        """
        Stores image data into a Neo4j graph database.

        Args:
            tx: The Neo4j transaction object.
            file (str): The name of the file containing the images.
            metadata: Additional metadata related to the file.

        Returns:
            None

        """
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
        """
        Stores table data into a Neo4j graph database.

        Args:
            tx: The Neo4j transaction object.
            file (str): The name of the file containing the tables.
            metadata: Additional metadata related to the file.

        Returns:
            None

        """
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
        
    def upload_text(self, output_file, upload_text: bool):
        """
        Uploads text to Neo4j database.

        Args:    
            output_file (str): The directory path where the text files are located.
            upload_text (bool): Flag indicating whether text upload is enabled or not.

        Returns:
            None

        """
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
            else:
                print("No 'extracted_text_blocks.json' file found.")

    def upload_tables(self, output_file, upload_tables: bool):
        """
        Uploads tables to Neo4j database.

        Args:   
            output_file (str): The directory path where the table files are located.
            upload_tables (bool): Flag indicating whether table upload is enabled or not.

        Returns:
            None

        """
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
            else:
                print("No tables found.")

    def upload_images(self, output_file, upload_images: bool):
        """
        Uploads images to Neo4j database.

        Args:
            output_file (str): The directory path where the image files are located.
            upload_images (bool): Flag indicating whether image upload is enabled or not.

        Returns:
            None

        """
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
            else:
                print("No images found.")

    def upload_interpreted_structure(self, output_file, interpreted_structure: bool):
        """
        Uploads interpreted structure data to Neo4j database.

        Args:
            output_file (str): The directory path where the interpreted structure files are located.
            interpreted_structure (bool): Flag indicating whether interpreted structure upload is enabled or not.

        Returns:
            None

        """
        if interpreted_structure and os.path.exists(os.path.join(output_file, "page_layout_structured_per_page.json")):
            print("Uploading interpreted structure to Neo4j.")
            with driver.session() as session:
                # Read text from file
                with open(os.path.join(output_file, "metadata.json"), "r") as f:
                    metadata = f.read()
                with open(os.path.join(output_file, "page_layout_structured_per_page.json"), "r") as f:
                    json_file = json.load(f)
                for key, json_block in json_file.items():
                    session.execute_write(self.neo4j_query_interpreted_structure, file=output_file, json_block=json_block, metadata=metadata)
                # Get interpreted word structure to use in coreference
                session.execute_write(self.neo4j_query_unravel_paragraphs, file=output_file)
            print("Interpreted structure uploaded to Neo4j.")
        else:
            if not interpreted_structure:
                print("Interpreted structure upload disabled.")
            else:
                print("No 'page_layout_structured_per_page.json' file found.")     
      
    def upload_hierarchial_interpreted_structure(self, output_file, interpreted_structure: bool):
        """
        Uploads hierarchical interpreted structure data to Neo4j database.

        Args: 
            output_file (str): The directory path where the hierarchical interpreted structure files are located.
            interpreted_structure (bool): Flag indicating whether hierarchical interpreted structure upload is enabled or not.

        Returns:
            None

        """
        if interpreted_structure and os.path.exists(os.path.join(output_file, "hierarchical_structure_for_file.json")):
            print("Uploading interpreted structure to Neo4j.")
            with driver.session() as session:
                # Read text from file
                with open(os.path.join(output_file, "metadata.json"), "r") as f:
                    metadata = f.read()
                with open(os.path.join(output_file, "hierarchical_structure_for_file.json"), "r") as f:
                    json_file = json.load(f)
                    
                def process_json_block(json_block):
                    for key, value in json_block.items():
                        if isinstance(value, dict):
                            # Extract "text", "blocks", and "page_nums" properties
                            text = value.get('text')
                            blocks = value.get('blocks')
                            page_nums = value.get('page_nums')
                            yield {key: {'text': text, 'blocks': blocks, 'page_nums': page_nums}}

                            # Check if the dictionary contains any other dictionaries
                            if any(isinstance(v, dict) for v in value.values()):
                                yield from process_json_block(value)

                for json_block in process_json_block(json_file):
                    #print(json_block, "\n")
                    session.execute_write(self.neo4j_query_hierarchial_interpreted_structure, file=output_file, json_block=json_block, metadata=metadata)
                    
                # Get interpreted word structure to use in coreference
                session.execute_write(self.neo4j_query_unravel_paragraphs, file=output_file)
            print("Interpreted structure uploaded to Neo4j.")
        else:
            if not interpreted_structure:
                print("Interpreted structure upload disabled.")
            else:
                print("No 'page_layout_structured_per_page.json' file found.")    
      
    def find_page_number(self, input_string):
        """
        Extracts the page number from a string.

        Args:  
            input_string (str): The string containing the page number.

        Returns:
            str: The extracted page number.

        """
        substrings = input_string.split('_')
        return substrings[1]
                
    def upload_data(self, output_file, upload_text: bool, upload_tables: bool, upload_images: bool, interpreted_structure: bool):
        """
        Uploads data to Neo4j database.

        Args:
            output_file (str): The directory path where the data files are located.
            upload_text (bool): Flag indicating whether text upload is enabled or not.
            upload_tables (bool): Flag indicating whether table upload is enabled or not.
            upload_images (bool): Flag indicating whether image upload is enabled or not.
            interpreted_structure (bool): Flag indicating whether interpreted structure upload is enabled or not.

        Returns:
            None

        """
        # walk through all the options
        print(f"\nloaded: {output_file}")
        # absolute data
        self.upload_text(output_file, upload_text)
        self.upload_tables(output_file, upload_tables)
        self.upload_images(output_file, upload_images)
        
        # interpreted data
        #self.upload_interpreted_structure(output_file, interpreted_structure)
        self.upload_hierarchial_interpreted_structure(output_file, interpreted_structure)
