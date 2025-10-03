from neo4j import GraphDatabase
from typing import List, Dict, Any
from ..utils.config import settings

class GraphService:
    def __init__(self):
        self.driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))

    def close(self):
        self.driver.close()

    def search_herbs(self, q: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (h:Herb)
        WHERE toLower(h.name) CONTAINS toLower($q) OR $q = ''
        RETURN h.name as name, h.properties as properties
        ORDER BY name
        LIMIT 50
        """
        with self.driver.session() as session:
            res = session.run(query, q=q)
            return [{"name": r["name"], "properties": r.get("properties", []) or []} for r in res]

    def herbs_for_symptoms(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        # Find herbs linked to conditions that match symptoms
        query = """
        WITH $symptoms AS symptoms
        MATCH (c:Condition)-[:HAS_SYMPTOM]->(s:Symptom)
        WHERE toLower(s.name) IN [x IN symptoms | toLower(x)]
        MATCH (h:Herb)-[r:HELPS_WITH]->(c)
        RETURN h.name AS herb, c.name AS condition, r.evidence AS evidence, h.properties AS properties
        """
        with self.driver.session() as session:
            res = session.run(query, symptoms=symptoms)
            return [dict(r) for r in res]

    def contraindications(self, herbs: List[str]) -> Dict[str, List[str]]:
        # Herb-Herb interactions to avoid combos
        query = """
        MATCH (h1:Herb)-[:INTERACTS_WITH]->(h2:Herb)
        WHERE toLower(h1.name) IN [x IN $herbs | toLower(x)]
        RETURN h1.name AS herb, collect(DISTINCT h2.name) AS avoid
        """
        with self.driver.session() as session:
            res = session.run(query, herbs=herbs)
            m = {}
            for r in res:
                m[r["herb"]] = r["avoid"]
            return m

    def conditions_from_symptoms(self, symptoms: List[str]) -> List[str]:
        query = """
        WITH $symptoms AS symptoms
        MATCH (c:Condition)-[:HAS_SYMPTOM]->(s:Symptom)
        WHERE toLower(s.name) IN [x IN symptoms | toLower(x)]
        RETURN DISTINCT c.name AS condition
        LIMIT 10
        """
        with self.driver.session() as session:
            res = session.run(query, symptoms=symptoms)
            return [r["condition"] for r in res]

    def all_symptoms(self) -> List[str]:
        query = "MATCH (s:Symptom) RETURN s.name AS name ORDER BY name"
        with self.driver.session() as session:
            res = session.run(query)
            return [r["name"] for r in res]
