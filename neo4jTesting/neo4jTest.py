from neo4j import GraphDatabase

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

def upload_words(tx, file, chapter, paragraph, sentence, words):
    for word in words:
        tx.run("""
            MERGE (f:File {name: $file})
            MERGE (c:Chapter {name: $chapter})
            MERGE (f)-[:CONTAINS]->(c)
            MERGE (p:Paragraph {name: $paragraph})
            MERGE (c)-[:CONTAINS]->(p)
            MERGE (s:Sentence {name: $sentence})
            MERGE (p)-[:CONTAINS]->(s)
            FOREACH (word IN $words | 
                MERGE (w:Word {name: word}) 
                MERGE (s)-[:CONTAINS]->(w))
        """, file=file, chapter=chapter, paragraph=paragraph, sentence=sentence, words=words)
        
input_files = ["neo4jTesting/exampleText.txt", "neo4jTesting/exampleText2.txt"]

with driver.session() as session:
    for file in input_files:
        text = open(file, "r").read()
        sentences = text.split(".")
        for sentence in sentences:
            words = sentence.split()
            session.execute_write(upload_words, file=f"File: {file}", chapter=f"Chapter 1 from file: {file}", paragraph=f"Paragraph 1 from file {file}", sentence=sentence, words=words)
driver.close()

#run both
# delete all nodes 1:  match (a) -[r] -> () delete a, r 
# delete all nodes 2:  match (a) delete a