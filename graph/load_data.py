import pandas as pd
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def clear():
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")

def create_constraints():
    with driver.session() as s:
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (h:Herb) REQUIRE h.name IS UNIQUE")
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Condition) REQUIRE c.name IS UNIQUE")
        s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE")

def upsert_herb(tx, name, properties):
    tx.run("""MERGE (h:Herb {name:$name})
             SET h.properties = $properties""", name=name, properties=properties)

def upsert_condition(tx, name):
    tx.run("MERGE (c:Condition {name:$name})", name=name)

def upsert_symptom(tx, name):
    tx.run("MERGE (s:Symptom {name:$name})", name=name)

def relate_condition_symptom(tx, condition, symptom):
    tx.run("""MATCH (c:Condition {name:$c}),(s:Symptom {name:$s})
             MERGE (c)-[:HAS_SYMPTOM]->(s)""", c=condition, s=symptom)

def relate_herb_condition(tx, herb, condition, evidence):
    tx.run("""MATCH (h:Herb {name:$h}),(c:Condition {name:$c})
             MERGE (h)-[r:HELPS_WITH]->(c)
             SET r.evidence = $evidence""", h=herb, c=condition, evidence=evidence)

def relate_interaction(tx, h1, h2):
    tx.run("""MATCH (a:Herb {name:$h1}),(b:Herb {name:$h2})
             MERGE (a)-[:INTERACTS_WITH]->(b)""", h1=h1, h2=h2)

def load():
    herbs = pd.read_csv("graph/data/herbs.csv")
    conditions = pd.read_csv("graph/data/conditions.csv")
    hc = pd.read_csv("graph/data/herb_conditions.csv")
    inter = pd.read_csv("graph/data/interactions.csv")

    with driver.session() as s:
        # nodes
        for _, row in herbs.iterrows():
            props = [p.strip() for p in str(row.get("properties","")).split("|") if p and str(p) != "nan"]
            s.execute_write(upsert_herb, row["name"], props)
        for _, row in conditions.iterrows():
            s.execute_write(upsert_condition, row["name"])
            # symptoms list pipe-separated
            syms = [x.strip() for x in str(row.get("symptoms","")).split("|") if x and str(x) != "nan"]
            for sy in syms:
                s.execute_write(upsert_symptom, sy)
                s.execute_write(relate_condition_symptom, row["name"], sy)

        # relations
        for _, row in hc.iterrows():
            s.execute_write(relate_herb_condition, row["herb"], row["condition"], row.get("evidence",""))

        for _, row in inter.iterrows():
            s.execute_write(relate_interaction, row["herb1"], row["herb2"])

if __name__ == "__main__":
    print("Clearing graph...")
    clear()
    print("Creating constraints...")
    create_constraints()
    print("Loading data...")
    load()
    print("Done.")
