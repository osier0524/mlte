from sqlalchemy import (
    Column, DateTime, Integer, String, Text, ForeignKey,
    Table, CheckConstraint, func
)
from sqlalchemy.orm import relationship
from mlte.backend.db.session import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    project_description = Column(Text, nullable=True)
    ml_task = Column(Text, nullable=True)
    usage_context = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    dataset_description = Column(Text, nullable=True)

    requirements = relationship("Requirement", back_populates="artifact", cascade="all, delete")
    set_evaluations = relationship("SetEvaluation", back_populates="artifact", cascade="all, delete")

class Requirement(Base):
    __tablename__ = "requirements"

    requirement_id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    card_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    artifact = relationship("Artifact", back_populates="requirements")
    feedbacks = relationship("Feedback", back_populates="requirement", cascade="all, delete")
    categories = relationship("RequirementCategory", back_populates="requirement", cascade="all, delete")

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)

    requirements = relationship("RequirementCategory", back_populates="category", cascade="all, delete")


class RequirementCategory(Base):
    __tablename__ = "requirement_categories"

    requirement_id = Column(Integer, ForeignKey("requirements.requirement_id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), primary_key=True)

    requirement = relationship("Requirement", back_populates="categories")
    category = relationship("Category", back_populates="requirements")


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    requirement_id = Column(Integer, ForeignKey("requirements.requirement_id", ondelete="CASCADE"), nullable=False)
    level = Column(String, CheckConstraint("level IN ('warning', 'error')"), nullable=False)

    requirement = relationship("Requirement", back_populates="feedbacks")
    feedback_qualities = relationship("FeedbackQuality", back_populates="feedback", cascade="all, delete")


class Quality(Base):
    __tablename__ = "quality"

    quality_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)

    feedback_qualities = relationship("FeedbackQuality", back_populates="quality", cascade="all, delete")

class FeedbackQuality(Base):
    __tablename__ = "feedback_quality"

    feedback_quality_id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(Integer, ForeignKey("feedback.feedback_id", ondelete="CASCADE"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.quality_id", ondelete="CASCADE"), nullable=False)

    feedback = relationship("Feedback", back_populates="feedback_qualities")
    quality = relationship("Quality", back_populates="feedback_qualities")
    critiques = relationship("Critique", back_populates="feedback_quality", cascade="all, delete")

class Critique(Base):
    __tablename__ = "critique"

    critique_id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_quality_id = Column(Integer, ForeignKey("feedback_quality.feedback_quality_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)

    feedback_quality = relationship("FeedbackQuality", back_populates="critiques")


class SetEvaluation(Base):
    __tablename__ = "set_evaluations"

    evaluation_id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    filter_criteria = Column(Text, nullable=False)

    artifact = relationship("Artifact", back_populates="set_evaluations")
    evaluation_qualities = relationship("EvaluationQuality", back_populates="evaluation", cascade="all, delete")

class EvaluationQuality(Base):
    __tablename__ = "evaluation_quality"

    evaluation_quality_id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("set_evaluations.evaluation_id", ondelete="CASCADE"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.quality_id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    percentage = Column(Integer, CheckConstraint("percentage >= 0 AND percentage <= 100"), nullable=False)

    evaluation = relationship("SetEvaluation", back_populates="evaluation_qualities")
    quality = relationship("Quality")
    critiques = relationship("EvaluationCritique", back_populates="evaluation_quality", cascade="all, delete")


class EvaluationCritique(Base):
    __tablename__ = "evaluation_critique"

    critique_id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_quality_id = Column(Integer, ForeignKey("evaluation_quality.evaluation_quality_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)

    evaluation_quality = relationship("EvaluationQuality", back_populates="critiques")