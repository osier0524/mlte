from sqlalchemy.orm import Session
from mlte.backend.db.models import *
from mlte.backend.dto import artifact as art_dto

class ArtifactRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Artifact).all()

    @staticmethod
    def get_by_id(db: Session, artifact_id: int):
        return db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()

    @staticmethod
    def create(db: Session, artifact_data: art_dto.ArtifactCreate):
        artifact = Artifact(
            name=artifact_data.name,
            project_description=artifact_data.project_description,
            ml_task=artifact_data.ml_task,
            usage_context=artifact_data.usage_context,
            target_audience=artifact_data.target_audience,
            dataset_description=artifact_data.dataset_description
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        return artifact
    
    @staticmethod
    def update(db: Session, artifact_id: int, artifact_data: art_dto.ArtifactCreate):
        artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
        if artifact:
            artifact.name = artifact_data.name
            artifact.project_description = artifact_data.project_description
            artifact.ml_task = artifact_data.ml_task
            artifact.usage_context = artifact_data.usage_context
            artifact.target_audience = artifact_data.target_audience
            artifact.dataset_description = artifact_data.dataset_description
            db.commit()
            db.refresh(artifact)
        return artifact

    @staticmethod
    def delete(db: Session, artifact_id: int):
        artifact = db.query(Artifact).filter_by(artifact_id=artifact_id).first()
        if artifact:
            db.delete(artifact)
            db.commit()
        return artifact
    

class RequirementRepository:
    @staticmethod
    def get_all(db: Session, artifact_id: int):
        return db.query(Requirement).filter(Requirement.artifact_id == artifact_id).all()

    @staticmethod
    def get_by_id(db: Session, requirement_id: int):
        return db.query(Requirement).filter(Requirement.requirement_id == requirement_id).first()
    
    @staticmethod
    def create(db: Session, artifact_id: int, content: str):
        new_requirement = Requirement(artifact_id=artifact_id, content=content)
        db.add(new_requirement)
        db.commit()
        db.refresh(new_requirement)
        return new_requirement

    @staticmethod
    def delete(db: Session, requirement_id: int):
        requirement = db.query(Requirement).filter_by(requirement_id=requirement_id).first()
        if requirement:
            db.delete(requirement)
            db.commit()
        return requirement

class CategoryRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Category).all()

    @staticmethod
    def get_by_id(db: Session, category_id: int):
        return db.query(Category).filter_by(category_id=category_id).first()

    @staticmethod
    def create(db: Session, name: str):
        cat = Category(name=name)
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat

    @staticmethod
    def delete(db: Session, category_id: int):
        cat = db.query(Category).filter_by(category_id=category_id).first()
        if cat:
            db.delete(cat)
            db.commit()
        return cat

class RequirementCategoryRepository:
    def get_requirementcategory(db: Session, requirement_id: int, category_id: int):
        return db.query(RequirementCategory).filter_by(requirement_id=requirement_id, category_id=category_id).first()

    def create_requirementcategory(db: Session, obj: RequirementCategory):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete_requirementcategory(db: Session, requirement_id: int, category_id: int):
        obj = db.query(RequirementCategory).filter_by(requirement_id=requirement_id, category_id=category_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
class FeedbackRepository:
    @staticmethod
    def get_all(db: Session, requirement_id: int):
        return db.query(Feedback).filter(Feedback.requirement_id == requirement_id).all()

    @staticmethod
    def get_by_id(db: Session, feedback_id: int):
        return db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()

    @staticmethod
    def create(db: Session, requirement_id: int, level: str, description: str):
        feedback = Feedback(requirement_id=requirement_id, level=level, description=description)
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def delete(db: Session, feedback_id: int):
        feedback = db.query(Feedback).filter_by(feedback_id=feedback_id).first()
        if feedback:
            db.delete(feedback)
            db.commit()
        return feedback
    
class QualityRepository:
    @staticmethod
    def get_all(db: Session):
        return db.query(Quality).all()

    @staticmethod
    def get_by_id(db: Session, quality_id: int):
        return db.query(Quality).filter_by(quality_id=quality_id).first()

    @staticmethod
    def create(db: Session, name: str):
        quality = Quality(name=name)
        db.add(quality)
        db.commit()
        db.refresh(quality)
        return quality

    @staticmethod
    def delete(db: Session, quality_id: int):
        quality = db.query(Quality).filter_by(quality_id=quality_id).first()
        if quality:
            db.delete(quality)
            db.commit()
        return quality

class FeedbackQualityRepository:
    @staticmethod
    def get_feedbackquality(db: Session, feedback_id: int, quality_id: int):
        return db.query(FeedbackQuality).filter_by(feedback_id=feedback_id, quality_id=quality_id).first()

    @staticmethod
    def create_feedbackquality(db: Session, obj: FeedbackQuality):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete_feedbackquality(db: Session, feedback_id: int, quality_id: int):
        obj = db.query(FeedbackQuality).filter_by(feedback_id=feedback_id, quality_id=quality_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

class CritiqueRepository:
    @staticmethod
    def get_critique_by_id(db: Session, id: int):
        return db.query(Critique).filter(Critique.critique_id == id).first()

    @staticmethod
    def get_all_critiques(db: Session):
        return db.query(Critique).all()

    @staticmethod
    def create_critique(db: Session, obj: Critique):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete_critique(db: Session, id: int):
        obj = db.query(Critique).filter(Critique.critique_id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

class SetEvaluationRepository:
    @staticmethod
    def get_setevaluation_by_id(db: Session, id: int):
        return db.query(SetEvaluation).filter(SetEvaluation.evaluation_id == id).first()

    @staticmethod
    def get_all_setevaluations(db: Session):
        return db.query(SetEvaluation).all()

    @staticmethod
    def create_setevaluation(db: Session, obj: SetEvaluation):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete_setevaluation(db: Session, id: int):
        obj = db.query(SetEvaluation).filter(SetEvaluation.evaluation_id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

class EvaluationQualityRepository:
    @staticmethod
    def get_eval_quality_by_id(db: Session, id: int):
        return db.query(EvaluationQuality).filter(EvaluationQuality.set_quality_id == id).first()

    @staticmethod
    def get_all_setqualities(db: Session):
        return db.query(EvaluationQuality).all()

    @staticmethod
    def create_eval_quality(db: Session, obj: EvaluationQuality):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete_eval_quality(db: Session, id: int):
        obj = db.query(EvaluationQuality).filter(EvaluationQuality.set_quality_id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj