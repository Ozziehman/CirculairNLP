import os
from neo4j import GraphDatabase
import base64
import json

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

class Neo4j_Structurizer:
    def __init__(self):
        pass

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
            WHERE b.block_no IN t.blocks AND b.page_num = t.page_num
            MERGE (b)-[:APPEARS_IN]->(t)
            """)
        tx.run("""
            MATCH (b:Block), (s:Subtitle)
            WHERE b.block_no IN s.blocks AND b.page_num = s.page_num
            MERGE (b)-[:APPEARS_IN]->(s)
            """)
        tx.run("""
            MATCH (b:Block), (p:Paragraph)
            WHERE b.block_no IN p.blocks AND b.page_num = p.page_num
            MERGE (b)-[:APPEARS_IN]->(p)
            """)
        tx.run("""
            MATCH (b:Block), (s:Subtext)
            WHERE b.block_no IN s.blocks AND b.page_num = s.page_num
            MERGE (b)-[:APPEARS_IN]->(s)
            """)

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
            session.execute_write(self.neo4j_query_connect_block)   
                
# delete all nodes:  MATCH (n) DETACH DELETE n