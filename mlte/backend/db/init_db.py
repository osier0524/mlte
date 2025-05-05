from mlte.backend.db.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mlte.backend.db.models import (Base, Quality, Artifact, 
                                    Requirement, Category, RequirementCategory,
                                    Feedback, FeedbackQuality, Critique)

# Connect to the database
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    qualities = ["unambiguous", "feasible", "complete", "appropriate"]
    quality_objs = []
    for q in qualities:
        quality = Quality(name=q)
        db.add(quality)
        quality_objs.append(quality)

    artifact = Artifact(
        name="default.negotiation_card", 
        project_description="The model should perform well.",
        ml_task="Flower Classification",
        usage_context="A handheld flower identification device.",
        dataset_description="Iris flower dataset.",
    )
    db.add(artifact)

    artifact2 = Artifact(
        name="sign detection", 
        project_description="This project aims to develop a machine learning model for detecting and recognizing road signs in real-time for autonomous vehicles. The model will identify various road signs—such as speed limits, stop signs, and yield signs—under different environmental conditions.",
    )
    db.add(artifact2)

    db.commit()
    db.refresh(artifact)
    db.refresh(artifact2)

    requirements = [
        Requirement(artifact_id=artifact.artifact_id, card_index=0, content="The model should accurately classify iris flowers with at least 95% accuracy."),
        Requirement(artifact_id=artifact.artifact_id, card_index=1, content="The model should run on low-power devices with less than 1GB of RAM."),
        Requirement(artifact_id=artifact.artifact_id, card_index=2, content="The model should provide confidence scores for each classification."),
        Requirement(artifact_id=artifact.artifact_id, card_index=3, content="The model should be robust to variations in lighting and background."),
    ]

    for req in requirements:
        db.add(req)
    
    db.commit()

    categories = [
        Category(name="Accuracy"),
        Category(name="Robustness")
    ]

    for cat in categories:
        db.add(cat)
    
    db.commit()

    category_links = [
        RequirementCategory(requirement_id=requirements[0].requirement_id, category_id=categories[0].category_id),
        RequirementCategory(requirement_id=requirements[1].requirement_id, category_id=categories[0].category_id),
        RequirementCategory(requirement_id=requirements[2].requirement_id, category_id=categories[1].category_id),
        RequirementCategory(requirement_id=requirements[3].requirement_id, category_id=categories[1].category_id),
    ]

    for link in category_links:
        db.add(link)
    
    db.commit()
    
    # Feedback 1: Ambiguous accuracy requirement
    feedback1 = Feedback(requirement_id=requirements[0].requirement_id, level="warning")
    db.add(feedback1)
    db.commit()
    db.refresh(feedback1)
    
    # Connect feedback to unambiguous quality
    fq1 = FeedbackQuality(feedback_id=feedback1.feedback_id, quality_id=quality_objs[0].quality_id)
    db.add(fq1)
    db.commit()
    db.refresh(fq1)

    # Add critiques to this feedback-quality combination
    critiques1 = [
        Critique(
            feedback_quality_id=fq1.feedback_quality_id, 
            content="The requirement does not specify which dataset the 95% accuracy should be measured on."
        ),
        Critique(
            feedback_quality_id=fq1.feedback_quality_id, 
            content="The requirement does not specify which metric (precision, recall, F1) to use for measuring accuracy."
        )
    ]
    
    for critique in critiques1:
        db.add(critique)

    # Feedback 2: Incomplete efficiency requirement
    feedback2 = Feedback(requirement_id=requirements[1].requirement_id, level="error")
    db.add(feedback2)
    db.commit()
    db.refresh(feedback2)
    
    # Connect feedback to complete quality
    fq2 = FeedbackQuality(feedback_id=feedback2.feedback_id, quality_id=quality_objs[2].quality_id)
    db.add(fq2)
    db.commit()
    db.refresh(fq2)
    
    # Add critiques to this feedback-quality combination
    critiques2 = [
        Critique(
            feedback_quality_id=fq2.feedback_quality_id, 
            content="The requirement does not specify a maximum inference time."
        ),
        Critique(
            feedback_quality_id=fq2.feedback_quality_id, 
            content="The requirement does not specify power consumption limits."
        )
    ]
    
    for critique in critiques2:
        db.add(critique)

    db.commit()
    db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")