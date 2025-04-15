
from mlte.backend.db.models import (
    Artifact, Requirement, Category, 
    Feedback, Quality, Critique, 
    RequirementCategory, FeedbackQuality, 
    QualityCritique)

class FeedbackService:
    def __init__(self, db):
        self.db = db
    async def add_feedback_with_quality_and_critiques(
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

        critique_ids = self.db.query(QualityCritique.critique_id).filter(
            QualityCritique.quality_id == quality.quality_id
        ).all()
        critique_ids = [cid[0] for cid in critique_ids]
        
        # delete related quality critiques
        self.db.query(QualityCritique).filter(
            QualityCritique.quality_id == quality.quality_id
        ).delete(synchronize_session=False)
        
        # delete critiques
        if critique_ids:
            self.db.query(Critique).filter(
                Critique.critique_id.in_(critique_ids)
            ).delete(synchronize_session=False)

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
        link = FeedbackQuality(
            feedback_id=feedback.feedback_id,
            quality_id=quality.quality_id
        )
        self.db.add(link)

        # insert critiques
        for content in critique_contents:
            critique = Critique(content=content)
            self.db.add(critique)
            self.db.commit()
            self.db.refresh(critique)

            qc = QualityCritique(
                quality_id=quality.quality_id,
                critique_id=critique.critique_id
            )
            self.db.add(qc)
        self.db.commit()
        return feedback
