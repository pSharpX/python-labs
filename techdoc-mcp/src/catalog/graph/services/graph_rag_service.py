from typing import List, Optional

from neo4j import Driver, GraphDatabase

from settings import GraphSettings
from src.catalog.graph.domain.graph_rag_domain import ProductServiceDTO, TargetSegment, HourlyRateDTO, \
    ServiceFootprintDTO


# =========================================================================
# Neo4j GraphRAG Service Class
# =========================================================================

class GraphRAGService:
    def __init__(self, ):
        self.settings = GraphSettings()
        self.driver: Driver = GraphDatabase.driver(
            uri=self.settings.url,
            auth=(self.settings.username, self.settings.password)
        )

    def close(self):
        self.driver.close()

    # =========================================================================
    # Strongly-Typed Query Methods
    # =========================================================================

    def get_full_taxonomy_context(
        self, business_line_name: str
    ) -> List[ProductServiceDTO]:
        """Pattern 1: Hierarchical Context Retrieval.

        Retrieves the complete subtree (Line -> Family -> Product) to construct
        structured domain context for LLM prompts.
        """
        query = """
        MATCH (b:BusinessLine)
        WHERE b.name CONTAINS $business_line_name
        MATCH (b)<-[:BELONGS_TO]-(f:Family)<-[:BELONGS_TO]-(p:ProductService)
        RETURN b.name AS business_line,
               f.name AS family,
               p.code AS product_code,
               p.name AS product_name,
               p.type AS type,
               p.smbApplicable AS smb_applicable,
               p.corpApplicable AS corp_applicable,
               p.description AS description
        ORDER BY family, product_name
        """
        with self.driver.session() as session:
            result = session.run(query, {"business_line_name": business_line_name})
            return [ProductServiceDTO(**record.data()) for record in result]

    def find_roles_by_category_and_budget(
        self,
        category: str,
        max_rate: float,
        target_segment: TargetSegment = TargetSegment.CORPORATE,
    ) -> List[HourlyRateDTO]:
        """Pattern 2: Multi-Factor Constraint Filtering.

        Filters rate nodes by category and financial limits, returning validated HourlyRate DTOs.
        """
        rate_field = (
            "h.corporateRate"
            if target_segment == TargetSegment.CORPORATE
            else "h.smbRate"
        )

        query = f"""
        MATCH (h:HourlyRate)
        WHERE h.category = $category
          AND {rate_field} <= $max_rate
        RETURN h.roleCode AS role_code,
               h.category AS category,
               h.position AS position,
               h.level AS level,
               h.smbRate AS smb_rate,
               h.corporateRate AS corporate_rate,
               h.description AS description
        ORDER BY {rate_field} ASC
        """
        with self.driver.session() as session:
            result = session.run(query, {"category": category, "max_rate": max_rate})
            return [HourlyRateDTO(**record.data()) for record in result]

    def get_service_delivery_footprint(
        self, product_code: str
    ) -> Optional[ServiceFootprintDTO]:
        """Pattern 3: Entity Subgraph Extraction.

        Extracts a detailed 2-hop neighborhood around a product node.
        """
        query = """
        MATCH (p:ProductService {code: $product_code})-[:BELONGS_TO]->(f:Family)-[:BELONGS_TO]->(b:BusinessLine)
        OPTIONAL MATCH (p)-[:REQUIRES_ROLE]->(h:HourlyRate)
        RETURN p.code AS product_code,
               p.name AS product_name,
               p.description AS product_description,
               f.name AS family,
               b.name AS business_line,
               collect(DISTINCT {role: h.position, rate: h.corporateRate}) AS associated_roles
        """
        with self.driver.session() as session:
            result = session.run(query, {"product_code": product_code})
            single_record = result.single()
            if single_record:
                data = single_record.data()
                # Clean up empty optional relationships if no roles are mapped
                data["associated_roles"] = [
                    r for r in data["associated_roles"] if r.get("role") is not None
                ]
                return ServiceFootprintDTO(**data)
            return None

    def search_similar_roles(self, keyword: str) -> List[HourlyRateDTO]:
        """Pattern 4: Hybrid Keyword Matching.

        Finds matching role nodes using property filtering.
        """
        query = """
        MATCH (h:HourlyRate)
        WHERE h.position CONTAINS $keyword 
           OR h.description CONTAINS $keyword
           OR h.category CONTAINS $keyword
        RETURN h.roleCode AS role_code,
               h.category AS category,
               h.position AS position,
               h.level AS level,
               h.smbRate AS smb_rate,
               h.corporateRate AS corporate_rate,
               h.description AS description
        LIMIT 5
        """
        with self.driver.session() as session:
            result = session.run(query, {"keyword": keyword})
            return [HourlyRateDTO(**record.data()) for record in result]