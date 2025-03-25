from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey,
    Table, CheckConstraint
)
from sqlalchemy.orm import relationship
from mlte.backend.db.session import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)

    requirements = relationship("Requirement", back_populates="artifact", cascade="all, delete")


class Requirement(Base):
    __tablename__ = "requirements"

    requirement_id = Column(Integer, primary_key=True, autoincrement=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.artifact_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)

    artifact = relationship("Artifact", back_populates="requirements")
    feedbacks = relationship("Feedback", back_populates="requirement", cascade="all, delete")
    categories = relationship("RequirementCategory", back_populates="requirement", cascade="all, delete")
    evaluations = relationship("SetEvaluation", back_populates="requirement", cascade="all, delete")


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
    description = Column(Text, nullable=False)

    requirement = relationship("Requirement", back_populates="feedbacks")
    qualities = relationship("FeedbackQuality", back_populates="feedback", cascade="all, delete")


class Quality(Base):
    __tablename__ = "quality"

    quality_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)

    feedbacks = relationship("FeedbackQuality", back_populates="quality", cascade="all, delete")
    critiques = relationship("QualityCritique", back_populates="quality", cascade="all, delete")


class FeedbackQuality(Base):
    __tablename__ = "feedback_quality"

    feedback_id = Column(Integer, ForeignKey("feedback.feedback_id", ondelete="CASCADE"), primary_key=True)
    quality_id = Column(Integer, ForeignKey("quality.quality_id", ondelete="CASCADE"), primary_key=True)

    feedback = relationship("Feedback", back_populates="qualities")
    quality = relationship("Quality", back_populates="feedbacks")


class Critique(Base):
    __tablename__ = "critique"

    critique_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)

    qualities = relationship("QualityCritique", back_populates="critique", cascade="all, delete")


class QualityCritique(Base):
    __tablename__ = "quality_critique"

    quality_id = Column(Integer, ForeignKey("quality.quality_id", ondelete="CASCADE"), primary_key=True)
    critique_id = Column(Integer, ForeignKey("critique.critique_id", ondelete="CASCADE"), primary_key=True)

    quality = relationship("Quality", back_populates="critiques")
    critique = relationship("Critique", back_populates="qualities")


class SetEvaluation(Base):
    __tablename__ = "set_evaluations"

    evaluation_id = Column(Integer, primary_key=True, autoincrement=True)
    requirement_id = Column(Integer, ForeignKey("requirements.requirement_id", ondelete="CASCADE"), nullable=False)
    filter_criteria = Column(Text, nullable=False)

    requirement = relationship("Requirement", back_populates="evaluations")
    qualities = relationship("SetQuality", back_populates="evaluation", cascade="all, delete")


class SetQuality(Base):
    __tablename__ = "set_quality"

    set_quality_id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(Integer, ForeignKey("set_evaluations.evaluation_id", ondelete="CASCADE"), nullable=False)
    quality_id = Column(Integer, ForeignKey("quality.quality_id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)

    evaluation = relationship("SetEvaluation", back_populates="qualities")
    quality = relationship("Quality")
