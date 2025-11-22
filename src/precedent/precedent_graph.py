"""
Precedent graph for tracking case citations and legal precedent relationships.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CaseNode:
    """Represents a case in the precedent graph."""
    case_id: str
    case_name: str
    citation: str
    court: str
    date_decided: datetime
    jurisdiction: str
    summary: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    
    # Graph properties
    cited_by: Set[str] = field(default_factory=set)  # Cases that cite this one
    cites: Set[str] = field(default_factory=set)      # Cases this one cites
    
    # Precedential value
    is_binding: bool = False
    is_overruled: bool = False
    treatment: str = "neutral"  # positive, negative, neutral


@dataclass
class CitationEdge:
    """Represents a citation relationship between cases."""
    source_case_id: str
    target_case_id: str
    citation_type: str  # followed, distinguished, overruled, etc.
    context: Optional[str] = None


class PrecedentGraph:
    """
    Graph database for tracking precedent relationships between cases.
    """
    
    def __init__(self):
        """Initialize precedent graph."""
        self.cases: Dict[str, CaseNode] = {}
        self.edges: List[CitationEdge] = []
    
    def add_case(self, case_node: CaseNode):
        """
        Add a case to the precedent graph.
        
        Args:
            case_node: Case to add
        """
        self.cases[case_node.case_id] = case_node
    
    def add_citation(
        self, 
        source_case_id: str,
        target_case_id: str,
        citation_type: str = "cited",
        context: Optional[str] = None
    ):
        """
        Add a citation relationship between cases.
        
        Args:
            source_case_id: ID of citing case
            target_case_id: ID of cited case
            citation_type: Type of citation relationship
            context: Optional context of citation
        """
        if source_case_id in self.cases and target_case_id in self.cases:
            self.cases[source_case_id].cites.add(target_case_id)
            self.cases[target_case_id].cited_by.add(source_case_id)
            
            edge = CitationEdge(
                source_case_id=source_case_id,
                target_case_id=target_case_id,
                citation_type=citation_type,
                context=context
            )
            self.edges.append(edge)
    
    def find_related_cases(
        self, 
        case_id: str,
        max_depth: int = 2,
        limit: int = 10
    ) -> List[CaseNode]:
        """
        Find cases related to a given case through citations.
        
        Args:
            case_id: ID of the source case
            max_depth: Maximum depth to traverse
            limit: Maximum number of results
            
        Returns:
            List of related cases
        """
        if case_id not in self.cases:
            return []
        
        related = set()
        visited = set()
        queue = [(case_id, 0)]
        
        while queue and len(related) < limit:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            current_case = self.cases[current_id]
            
            # Add cited cases
            for cited_id in current_case.cites:
                if cited_id != case_id and cited_id in self.cases:
                    related.add(cited_id)
                    if depth < max_depth:
                        queue.append((cited_id, depth + 1))
            
            # Add citing cases
            for citing_id in current_case.cited_by:
                if citing_id != case_id and citing_id in self.cases:
                    related.add(citing_id)
                    if depth < max_depth:
                        queue.append((citing_id, depth + 1))
        
        return [self.cases[case_id] for case_id in list(related)[:limit]]
    
    def find_precedent_chain(
        self, 
        case_id: str,
        target_case_id: Optional[str] = None
    ) -> List[List[str]]:
        """
        Find precedent chains from a case to its foundations.
        
        Args:
            case_id: Starting case ID
            target_case_id: Optional target case ID
            
        Returns:
            List of citation chains (each chain is a list of case IDs)
        """
        # Stub implementation - simple DFS for citation chains
        if case_id not in self.cases:
            return []
        
        chains = []
        visited = set()
        
        def dfs(current_id: str, path: List[str]):
            if current_id in visited:
                return
            
            visited.add(current_id)
            path = path + [current_id]
            
            if target_case_id and current_id == target_case_id:
                chains.append(path)
                return
            
            current_case = self.cases.get(current_id)
            if not current_case:
                return
            
            # Follow citations
            if current_case.cites:
                for cited_id in current_case.cites:
                    dfs(cited_id, path)
            else:
                # Reached a leaf node
                chains.append(path)
        
        dfs(case_id, [])
        return chains[:10]  # Limit to 10 chains
    
    def get_citation_count(self, case_id: str) -> Dict[str, int]:
        """
        Get citation statistics for a case.
        
        Args:
            case_id: Case ID
            
        Returns:
            Dictionary with citation counts
        """
        if case_id not in self.cases:
            return {"cited_by": 0, "cites": 0}
        
        case = self.cases[case_id]
        return {
            "cited_by": len(case.cited_by),
            "cites": len(case.cites)
        }
    
    def get_most_cited_cases(self, limit: int = 10) -> List[CaseNode]:
        """
        Get most frequently cited cases.
        
        Args:
            limit: Number of cases to return
            
        Returns:
            List of most cited cases
        """
        sorted_cases = sorted(
            self.cases.values(),
            key=lambda c: len(c.cited_by),
            reverse=True
        )
        return sorted_cases[:limit]
    
    def find_overruled_cases(self, case_id: str) -> List[CaseNode]:
        """
        Find cases that have been overruled by or overrule this case.
        
        Args:
            case_id: Case ID
            
        Returns:
            List of overruled/overruling cases
        """
        if case_id not in self.cases:
            return []
        
        overruled = []
        for edge in self.edges:
            if edge.citation_type == "overruled":
                if edge.source_case_id == case_id:
                    overruled.append(self.cases[edge.target_case_id])
                elif edge.target_case_id == case_id:
                    overruled.append(self.cases[edge.source_case_id])
        
        return overruled
    
    def search_by_topic(
        self, 
        topic: str,
        jurisdiction: Optional[str] = None
    ) -> List[CaseNode]:
        """
        Search cases by legal topic.
        
        Args:
            topic: Legal topic to search for
            jurisdiction: Optional jurisdiction filter
            
        Returns:
            List of matching cases
        """
        results = []
        for case in self.cases.values():
            if topic.lower() in [t.lower() for t in case.topics]:
                if jurisdiction is None or case.jurisdiction == jurisdiction:
                    results.append(case)
        
        return results
    
    def export_graph(self, format: str = "json") -> Any:
        """
        Export precedent graph in specified format.
        
        Args:
            format: Export format ('json', 'graphml', 'cytoscape')
            
        Returns:
            Graph data in specified format
        """
        # Stub implementation
        if format == "json":
            return {
                "nodes": [
                    {
                        "id": case.case_id,
                        "name": case.case_name,
                        "citation": case.citation
                    }
                    for case in self.cases.values()
                ],
                "edges": [
                    {
                        "source": edge.source_case_id,
                        "target": edge.target_case_id,
                        "type": edge.citation_type
                    }
                    for edge in self.edges
                ]
            }
        
        return None
