from neo4j import GraphDatabase

url = "neo4j://localhost:7687"
driver = GraphDatabase.driver(url, auth=("neo4j", "password"))

def upload_words(tx, sentence, words):
    for word in words:
        # Hij maakt als het er nog niet is en merged dan alle worde in die zin.
        tx.run("MERGE (s:Sentence {name: $sentence}) " # s is de variable naam
           "FOREACH (word IN $words | " # $words is de words vanuit python
           "  MERGE (w:Word {name: word}) " # word is de variable naam
           "  MERGE (s)-[:CONTAINS]->(w))",  
           sentence=sentence, words=words)
        
text = """
The quick brown fox jumps over the lazy dog.
Programming in Python is both fun and educational.
Artificial intelligence is transforming the world of technology.
"""
sentences = text.split("\n")
words = [word for sentence in sentences for word in sentence.split()]
with driver.session() as session:
    for sentence in sentences:
        words = sentence.split()
        session.execute_write(upload_words, sentence, words)
driver.close()

#run both
# delete all nodes 1:  match (a) -[r] -> () delete a, r 
# delete all nodes 2:  match (a) delete a