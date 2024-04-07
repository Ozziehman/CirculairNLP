import os
from neo4j import GraphDatabase
import base64
import json
import nltk
from nltk.stem import WordNetLemmatizer
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Coreference.coreference_resolution import CoreferenceResolver

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

class Neo4j_Structurizer:
    def __init__(self):
        coreference_model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Coreference")
        self.coreference_resolver = CoreferenceResolver(coreference_model_path)
        self.MIN_CHAR_FOR_COREF = 100

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

    def neo4j_query_connect_block(self, tx):
        tx.run("""
            MATCH (b:Block), (t:Title)
            WHERE b.block_no IN t.blocks AND b.page_num = t.page_num AND b.block_from_file = t.title_from_file
            MERGE (b)-[:APPEARS_IN]->(t)
            """)
        tx.run("""
            MATCH (b:Block), (s:Subtitle)
            WHERE b.block_no IN s.blocks AND b.page_num = s.page_num AND b.block_from_file = s.subtitle_from_file
            MERGE (b)-[:APPEARS_IN]->(s)
            """)
        tx.run("""
            MATCH (b:Block), (p:Paragraph)
            WHERE b.block_no IN p.blocks AND b.page_num = p.page_num AND b.block_from_file = p.paragraph_from_file
            MERGE (b)-[:APPEARS_IN]->(p)
            """)
        tx.run("""
            MATCH (b:Block), (s:Subtext)
            WHERE b.block_no IN s.blocks AND b.page_num = s.page_num AND b.block_from_file = s.subtext_from_file
            MERGE (b)-[:APPEARS_IN]->(s)
            """)
 
    def neo4j_query_make_lemmetized_nodes(self, tx):
        """Make lemmetized nodes in the Neo4j database."""
        tx.run("""
            // Make lemmetized nodes for Word nodes
            MATCH (w:Word)
            MERGE (l:LemmetizedWord {lemma: w.lemma})
        """)

        tx.run("""
            // Make lemmetized nodes for Paragraph_Word nodes
            MATCH (pw:Paragraph_Word)
            MERGE (l2:LemmetizedWord {lemma: pw.lemma})
        """)

    def neo4j_query_connect_words_to_lemmetized_nodes(self, tx):
        """Connect words to lemmetized nodes in the Neo4j database."""
        tx.run("""
            // Connect Word nodes to lemmetized nodes
            MATCH (w:Word)
            MATCH (l:LemmetizedWord {lemma: w.lemma})
            MERGE (w)-[:IS_LEMMETIZED]->(l)
        """)

        tx.run("""
            // Connect Paragraph_Word nodes to lemmetized nodes
            MATCH (pw:Paragraph_Word)
            MATCH (l2:LemmetizedWord {lemma: pw.lemma})
            MERGE (pw)-[:IS_LEMMETIZED]->(l2)
        """)

    def neo4j_query_resolve_coreferences_and_connect_words(self, tx):
        # Retrieve paragraphs from Neo4j
        paragraphs = tx.run("MATCH (p:Paragraph) RETURN p").values()

        for paragraph_node in paragraphs:
            paragraph_text = paragraph_node['text']
            if len(paragraph_text) >= self.MIN_CHAR_FOR_COREF:
                resolved_coreferences = self.coreference_resolver.resolve_coreferences(paragraph_text)
                if resolved_coreferences:
                    # Iterate over resolved coreferences
                    for location, word in resolved_coreferences:
                        # Extract start and end indices
                        start, end = location
                        # Find the referred word
                        referred_word = tx.run(
                            "MATCH (p:Paragraph)-[:CONTAINS]->(w:Word) WHERE p = $paragraph_node AND w.word_no >= $start AND w.word_no <= $end AND w.word = $word RETURN w",
                            paragraph_node=paragraph_node, start=start, end=end, word=word).single()
                        if referred_word:
                            referred_word_node = referred_word['w']
                            # Connect the referring word to the referred word
                            referring_word = tx.run(
                                "MATCH (p:Paragraph)-[:CONTAINS]->(w:Word) WHERE p = $paragraph_node AND w.word_no = $start RETURN w",
                                paragraph_node=paragraph_node, start=start).single()
                            if referring_word:
                                referring_word_node = referring_word['w']
                                tx.run("MERGE (w1:Word {word_no: $referring_start})-[:REFERS_TO]->(w2:Word {word_no: $referred_start})",
                                       referring_start=referring_word_node['word_no'], referred_start=referred_word_node['word_no'])

    def structurize_neo4j_database(self):       
        """"Structurizes the Neo4j database."""
        with driver.session() as session:
            print("Making relations in between pages, blocks, lines and words. . . ")
            session.execute_write(self.neo4j_query_organize_pages)
            print("Organizing blocks in order. . . ")
            session.execute_write(self.neo4j_query_organize_blocks)
            print("Organizing words in order. . . ")
            session.execute_write(self.neo4j_query_organize_words)
            print("Matching similar words. . . ")
            session.execute_write(self.neo4j_query_connect_matching_words) 
            print("Connecting blocks to interpreted titles, subtitles, paragraphs and subtexts. . . ")
            session.execute_write(self.neo4j_query_connect_block)  
            print("Making lemmetized nodes. . . ")
            session.execute_write(self.neo4j_query_make_lemmetized_nodes)
            print("Connecting words to lemmetized nodes. . . ")
            session.execute_write(self.neo4j_query_connect_words_to_lemmetized_nodes)
            print("Resolving coreferences and connecting the words. . . ")
            session.write_transaction(self.neo4j_query_resolve_coreferences_and_connect_words)
                
# delete all nodes:  MATCH (n) DETACH DELETE n