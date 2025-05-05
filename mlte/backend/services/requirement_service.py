import hashlib
from typing import List, Union
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from mlte.backend.db.models import (
    Artifact, Requirement, Category, 
    Feedback, Quality, Critique, 
    RequirementCategory, FeedbackQuality)
from mlte.backend.dto import requirement as req_dto
from mlte.backend.dto import critique as crit_dto

class RequirementService:
    def __init__(self, db: Session):
        self.db = db
        
    def create_requirement(self, artifact_id: int, card_index: int, content: str) -> req_dto.RequirementCreateResponse:
        req = Requirement(artifact_id=artifact_id, card_index=card_index, content=content)
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        response = req_dto.RequirementCreateResponse(requirement_id=req.requirement_id)
        return response

    def update_requirement(self, artifact_id: int, card_index: int, content: str) -> req_dto.RequirementCreateResponse:
        req = self.db.query(Requirement).filter_by(
            artifact_id=artifact_id,
            card_index=card_index
        ).first()
        if not req:
            raise ValueError("Requirement not found")
        
        req.content = content
        self.db.commit()
        self.db.refresh(req)
        response = req_dto.RequirementCreateResponse(requirement_id=req.requirement_id)
        return response

    def add_categories_to_requirement(
        self,
        artifact_id: int,
        card_index: int,
        category_names: list[str]
    ):
        # delete old links
        requirement_id = self._get_requirement_id(artifact_id, card_index)
        self.db.query(RequirementCategory).filter_by(
            requirement_id=requirement_id
        ).delete()
        self.db.commit()
        print("Deleted old links")

        results = []
        for name in category_names:
            # check if category exists
            category = self.db.query(Category).filter_by(name=name).first()
            if not category:
                category = Category(name=name)
                self.db.add(category)
                self.db.commit()
                self.db.refresh(category)

            link = self.db.query(RequirementCategory).filter_by(
                requirement_id=requirement_id,
                category_id=category.category_id
            ).first()

            if not link:
                link = RequirementCategory(
                    requirement_id=requirement_id,
                    category_id=category.category_id
                )
                self.db.add(link)
                self.db.commit()
                self.db.refresh(link)
            results.append(category)
        
        return results

    def delete_all_feedbacks_for_requirement(self, requirement_id: int):
        # delete all feedbacks for this requirement
        self.db.query(Feedback).filter_by(requirement_id=requirement_id).delete()
        self.db.commit()


    def add_feedback_with_quality_and_critiques(
        self,
        requirement_id: int,
        level: str,
        quality_name: str,
        critique_contents: list[str]
    ):
        # find or create quality
        quality = self.db.query(Quality).filter_by(name=quality_name).first()
        if not quality:
            quality = Quality(name=quality_name)
            self.db.add(quality)
            self.db.commit()
            self.db.refresh(quality)

        # find if exists this quality
        existing_feedbacks = self.db.query(Feedback).join(
            FeedbackQuality, 
            Feedback.feedback_id == FeedbackQuality.feedback_id
        ).filter(
            Feedback.requirement_id == requirement_id,
            FeedbackQuality.quality_id == quality.quality_id
        ).all()
        
        # delete related quality critiques
        for existing_feedback in existing_feedbacks:
            self.db.delete(existing_feedback)
        
        self.db.commit()


        # create feedback
        feedback = Feedback(
            requirement_id=requirement_id,
            level=level,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        # connect feedback and quality
        feedback_quality = FeedbackQuality(
            feedback_id=feedback.feedback_id,
            quality_id=quality.quality_id
        )
        self.db.add(feedback_quality)
        self.db.commit()
        self.db.refresh(feedback_quality)

        # insert critiques
        for content in critique_contents:
            critique = Critique(
                feedback_quality_id=feedback_quality.feedback_quality_id,
                content=content
            )
            self.db.add(critique)
        
        self.db.commit()
        return feedback

    # get a requirements' categories
    def get_categories_for_requirement(self, requirement_id: int):
        return self.db.query(RequirementCategory).filter_by(requirement_id=requirement_id).all()

    def get_requirements_by_artifact_id(self, artifact_id: int) -> List[req_dto.RequirementResponse]:
        try:
            requirements = (
                self.db.query(Requirement)
                .filter(Requirement.artifact_id == artifact_id)
                .order_by(Requirement.requirement_id)
                .options(
                    joinedload(Requirement.categories).joinedload(RequirementCategory.category),
                    joinedload(Requirement.feedbacks)
                    .joinedload(Feedback.feedback_qualities)
                    .joinedload(FeedbackQuality.quality)
                )
                .all()
            )

            result = []
            for req in requirements:
                requirement_data = self._format_requirement(req)
                result.append(requirement_data)

            return result
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            raise

    def get_requirement_by_id(self, artifact_id: int, requirement_id: int) -> Union[req_dto.RequirementResponse, None]:
        try:
            requirement = (
                self.db.query(Requirement)
                .filter(Requirement.requirement_id == requirement_id)
                .options(
                    joinedload(Requirement.categories).joinedload(RequirementCategory.category),
                    joinedload(Requirement.feedbacks)
                    .joinedload(Feedback.qualities)
                    .joinedload(FeedbackQuality.quality)
                )
                .first()
            )

            if requirement:
                return self._format_requirement(requirement)
            else:
                return None
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            raise

    def _format_requirement(self, requirement: Requirement) -> req_dto.RequirementResponse:
        categories = [cat.category.name for cat in requirement.categories]

        feedbacks = []
        for feedback in requirement.feedbacks:
            qualities_data = []
            
            for fq in feedback.feedback_qualities:
                quality = fq.quality
                
                critiques = (
                    self.db.query(Critique)
                    .filter(Critique.feedback_quality_id == fq.feedback_quality_id)
                    .all()
                )
                
                critique_contents = [critique.content for critique in critiques]
                
                qualities_data.append(
                    crit_dto.QualityWithCritiquesResponse(
                        name=quality.name,
                        critiques=critique_contents
                    )
                )
            
            feedbacks.append(
                crit_dto.FeedbackResponse(
                    level=feedback.level,
                    qualities=qualities_data
                )
            )
        
        return req_dto.RequirementResponse(
            requirement_id=requirement.requirement_id,
            content=requirement.content,
            categories=categories,
            feedbacks=feedbacks
        )
    
    def get_critique_stats(self, requirement_id: int) -> crit_dto.CritiqueStats:
        try:
            # Fetch feedbacks for the requirement
            feedbacks = (
                self.db.query(Feedback)
                .filter(Feedback.requirement_id == requirement_id)
                .options(
                    joinedload(Feedback.feedback_qualities)
                    .joinedload(FeedbackQuality.quality),
                    joinedload(Feedback.feedback_qualities)
                    .joinedload(FeedbackQuality.critiques)
                )
                .all()
            )
            # Get warnings and errors (only record quality name)
            warnings = []
            errors = []
            for feedback in feedbacks:
                for fq in feedback.feedback_qualities:
                    quality = fq.quality
                    if feedback.level == "warning":
                        warnings.append(quality.name)
                    elif feedback.level == "error":
                        errors.append(quality.name)

            return crit_dto.CritiqueStats(warnings=warnings, errors=errors)
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
            raise

    def get_requirements_version(self, artifact_id: int, filter_criteria: str) -> str:
        if filter_criteria == "All":
            # get all requirements for the artifact
            requirements = self.db.query(Requirement).filter_by(artifact_id=artifact_id).all()
        else:
            category_names = filter_criteria.split(",")
            # get requirements for the artifact that belong to the specified categories
            requirements = (
                self.db.query(Requirement)
                .join(Requirement.categories)
                .filter(
                    Requirement.artifact_id == artifact_id,
                    Category.name.in_(category_names)
                )
                .all()
            )
        
        timestamps = [req.content_updated_at.isoformat() for req in requirements]
        timestamps.sort()
        combined_timestamps = "".join(timestamps)
        version = hashlib.md5(combined_timestamps.encode()).hexdigest()

        return version
    
    def _get_requirement_id(self, artifact_id: int, card_index: int) -> int:
        requirement = self.db.query(Requirement).filter_by(
            artifact_id=artifact_id,
            card_index=card_index
        ).first()
        if not requirement:
            return None
        
        return requirement.requirement_id