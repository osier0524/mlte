from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from mlte.backend.db.models import (
    SetEvaluation, EvaluationQuality, EvaluationCritique, Quality
)

class SetEvaluationService:
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_evaluation(self, artifact_id: int, filter_criteria: str) -> Optional[Dict[str, Any]]:

        # Find the evaluation record
        evaluation = self.db.query(SetEvaluation).filter_by(
            artifact_id=artifact_id,
            filter_criteria=filter_criteria
        ).first()
        
        if not evaluation:
            return None
            
        # Get all quality evaluations with their critiques
        qualities_data = []
        
        evaluation_qualities = self.db.query(EvaluationQuality).filter_by(
            evaluation_id=evaluation.evaluation_id
        ).all()
        
        for eq in evaluation_qualities:
            # Get the quality name
            quality = self.db.query(Quality).filter_by(quality_id=eq.quality_id).first()
            if not quality:
                continue
            
            # Get critiques for this quality evaluation
            critiques = self.db.query(EvaluationCritique).filter_by(
                evaluation_quality_id=eq.evaluation_quality_id
            ).all()
            
            # Format critiques for frontend
            formatted_critiques = []
            for critique in critiques:
                try:
                    # Parse the JSON string back to structured data
                    critique_data = json.loads(critique.content)
                    formatted_critiques.append(critique_data)
                except (json.JSONDecodeError, TypeError):
                    # Handle legacy format or invalid JSON
                    # Try to extract requirement IDs from the content if it's a string
                    if isinstance(critique.content, str):
                        # Legacy format example: "Issue description (Requirements: 1, 2). Explanation"
                        parts = critique.content.split("(Requirements: ")
                        if len(parts) > 1:
                            issue = parts[0].strip()
                            rest = parts[1].split(").")
                            if len(rest) > 1:
                                req_ids_str = rest[0].strip()
                                explanation = rest[1].strip()
                                
                                # Extract requirement IDs
                                req_ids = [f"R{id.strip()}" for id in req_ids_str.split(",") if id.strip().isdigit()]
                                
                                if len(req_ids) >= 2:  # Only include if there are at least 2 requirements
                                    formatted_critiques.append({
                                        "set": req_ids,
                                        "critics": [f"{issue}. {explanation}"]
                                    })
            
            # Merge critiques that target the same set of requirements
            merged_critiques = self._merge_critiques(formatted_critiques)
            
            # Create the quality response object
            quality_data = {
                "name": quality.name,
                "summary": eq.summary,
                "critique": merged_critiques,
                "percentage": eq.percentage
            }
            
            qualities_data.append(quality_data)
        
        # Create the final response
        result = {
            "evaluation_id": evaluation.evaluation_id,
            "filter_criteria": evaluation.filter_criteria,
            "qualities": qualities_data
        }
        
        return result
    
    def _merge_critiques(self, critiques: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        merged = {}
        
        for critique in critiques:
            # Convert the set of requirements to a tuple for hashing
            req_set_tuple = tuple(sorted(critique["set"]))
            
            if req_set_tuple in merged:
                # Add criticism to existing entry
                merged[req_set_tuple]["critics"].extend(critique["critics"])
            else:
                # Create new entry
                merged[req_set_tuple] = {
                    "set": critique["set"],
                    "critics": critique["critics"]
                }
        
        # Convert back to list
        return list(merged.values())