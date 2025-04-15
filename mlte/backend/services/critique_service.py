import time
import traceback
import openai
import json

import asyncio
from concurrent.futures import ThreadPoolExecutor

from typing import Any, Dict, List, Union
from sqlalchemy.orm import Session

from mlte.backend.services.config import OPENAI_API_KEY
import mlte.backend.dto.critique as crit_dto

from mlte.backend.db.models import (
    Artifact, Requirement, Category, 
    Feedback, Quality, Critique, SetEvaluation,
    RequirementCategory, FeedbackQuality, EvaluationQuality, EvaluationCritique)
from mlte.backend.services.llm.llm_service import LLMService
from mlte.backend.services.llm.openai_provider import OpenAIProvider
from mlte.backend.services.requirement_service import RequirementService

class CritiqueService:

    def __init__(self, db: Session, llm_service: LLMService, req_service: RequirementService):
        self.db = db
        self.llm_service = llm_service
        self.req_service = req_service
    
    """
    Service for individual requirement quality critique.
    """
    individual_qualities = ["Necessary", "Appropriate", "Unambiguous", "Complete", "Singular", 
                           "Feasible", "Verifiable", "Correct", "Conforming"]
    
    # individual_qualities = ["Unambiguous"]
    
    async def critique_requirement(self, artifact_id: int, req_id: int) -> crit_dto.CritiqueStats:
        print(f"Processing requirement {req_id} for artifact {artifact_id}")
        artifact = self.db.query(Artifact).filter_by(artifact_id=artifact_id).first()
        req = self.db.query(Requirement).filter_by(requirement_id=req_id).first()
        req_category = ", ".join(sorted([c.category.name for c in req.categories]))
        project_context = crit_dto.ProjectContext(
            project_description=artifact.project_description,
            ml_task=artifact.ml_task,
            usage_context=artifact.usage_context,
            target_audience=artifact.target_audience,
            dataset_description=artifact.dataset_description
        )
        print(f"Starting critique for requirement {req_id}")
        print(f"Requirement: {req.content}")
        print(f"Requirement category: {req_category}")
        print(f"Project context: {project_context}")

        tasks = []
        for quality in self.individual_qualities:
            task = asyncio.create_task(
                self._process_single_quality(
                    quality=quality, 
                    req=req.content, 
                    req_category=req_category,
                    project_context=project_context
                )
            )

            print(f"Started task for quality: {quality} at {time.strftime('%H:%M:%S', time.localtime())}")
            tasks.append(task)

        completed = 0
        warnings = []
        errors = []
        total = len(tasks)

        # delete old feedbacks
        self.req_service.delete_all_feedbacks_for_requirement(req_id)

        for task in asyncio.as_completed(tasks):
            try:

                result = await task

                end_time = time.time()

                print(f"Task completed at {time.strftime('%H:%M:%S', time.localtime())}")
                if result:
                    quality_name = result["quality"]
                    rating: crit_dto.Rating = result["rating"]
                    critiques = result["critiques"]
                    print(f"Quality: {quality_name}, Rating: {rating.rating}, Critiques: {critiques}")
                    if rating.rating == "low":
                        errors.append(quality_name)
                        level = "error"
                    elif rating.rating == "medium":
                        warnings.append(quality_name)
                        level = "warning"
                    else:
                        level = None

                    if level:
                        self.req_service.add_feedback_with_quality_and_critiques(
                            requirement_id=req_id,
                            level=level,
                            quality_name=quality_name,
                            critique_contents=critiques
                        )
                        print(f"Saved feedback for quality: {quality_name}")
                
                completed += 1
                print(f"Completed {completed}/{total} tasks.")
            except Exception as e:
                print(f"An error occurred: {e}")
                traceback.print_exc()
                completed += 1
                print(f"Completed {completed}/{total} tasks (including failures).")

        return crit_dto.CritiqueStats(warnings=warnings, errors=errors)
    
    async def _process_single_quality(self, quality: str, req: str, req_category: str, project_context: crit_dto.ProjectContext):
        try:
            result = await self._call_llm_for_critique(quality, req, req_category, project_context)
            return result
        except Exception as e:
            traceback.print_exc()
            print(f"Error processing quality {quality}: {e}")
            return None
    
    async def _call_llm_for_critique(self, quality, req, req_category, project_context):
        # Step 1: Rate the requirement based on the quality
        first_rating, prev_conversation = await self._call_llm_to_rate(req, req_category, project_context, quality)
        # Step 2: Introduce a challenger model to rate again

        # Step 3: Generate critiques based on the ratings
        critiques = await self._generate_critiques(first_rating.rating, prev_conversation)

        # construct the result
        result = {
            "quality": quality,
            "rating": first_rating,
            "critiques": critiques
        }
        return result

    async def _call_llm_to_rate(self, req: str, req_category: str, ctx: crit_dto.ProjectContext, quality: str) -> Union[crit_dto.Rating, str]:
        # call different function to construct the prompt according to the quality
        if quality == "Necessary":
            rating_prompt = self._construct_necessary_rating_prompt(req_category, ctx)
        elif quality == "Appropriate":
            rating_prompt = self._construct_appropriate_rating_prompt(req_category, ctx)
        elif quality == "Unambiguous":
            rating_prompt = self._construct_unambiguous_rating_prompt(req_category, ctx)
        elif quality == "Complete":
            rating_prompt = self._construct_complete_rating_prompt(req_category, ctx)
        elif quality == "Singular":
            rating_prompt = self._construct_singular_rating_prompt(req_category, ctx)
        elif quality == "Feasible":
            rating_prompt = self._construct_feasible_rating_prompt(req_category, ctx)
        elif quality == "Verifiable":
            rating_prompt = self._construct_verifiable_rating_prompt(req_category, ctx)
        elif quality == "Correct":
            rating_prompt = self._construct_correct_rating_prompt(req_category, ctx)
        elif quality == "Conforming":
            rating_prompt = self._construct_conforming_rating_prompt(req_category, ctx)
        else:
            return crit_dto.Rating(rating="", explanation=""), ""
        
        rating_result, prev_conversation = self._rate_req(req, rating_prompt)

        return crit_dto.Rating(rating=rating_result["eval_result"], explanation=rating_result["explanation"]), prev_conversation
        
    async def _call_challenger_model(self, req: str, ctx: str, quality: str) -> crit_dto.Rating:
        return Rating(rating="low", explanation="The requirement is unclear and ambiguous.")

    async def _generate_critiques(self, rating: str, prev_conversation: str) -> list[str]:
        
        context = f"The previous step is to assess whether the quality of the requirement is high, medium, or low. \
                The query and result of the first step are as follows: \
                Previous Conversation: {prev_conversation}. \
                Final Rating: {rating}. \
                Next, proceed to the next step and provide critiques based on the quality level and quality defination."

        criticize_medium_prompt = "The requirement is rated as medium quality. \
                First, evaluate how many problematic specific expressions are present in this requirement sentence. \
                If there are more than 2 problematic specific expressions, provide critiques for the 2 most severe ones. \
                If there are fewer than 2, provide a critique for each one. \
                Each crituque should be a short sentence or two. \
                Each critique should focus on only one specific part of the sentence. \
                Avoid high-level or summary judgments such as \"missing goals\" or \"unclear background\"\
                Don't criticize the same part of the requirement sentence more than once."

        criticize_low_prompt = "The requirement is rated as low quality. \
                First, evaluate how many problematic specific expressions are present in this requirement sentence. \
                If there are more than 5 problematic specific expressions, provide critiques for the 5 most severe ones. \
                If there are fewer than 5, provide a critique for each one. \
                Each crituque should be a short sentence or two. \
                Each critique should focus on only one specific part of the sentence. \
                Avoid high-level or summary judgments such as \"missing goals\" or \"unclear background\"\
                Don't criticize the same part of the requirement sentence more than once."

        output_format = " Output: \
                The output should be in plain json format, \
                with only the following field: critiques \
                Do not include any extra text or formatting. \
                Do not inclue ```json. \
                Property names should be enclosed in double quotes. \
                Example: \"critiques\": [\"Critique 1\", \"Critique 2\"] "
        
        system_promt = "You are an expert in analyzing requirement quality and providing critiques."
        
        critiques = []
        if rating == "medium":
            prompt = context + criticize_medium_prompt + output_format
            result = self._safe_perform_query_return_json(prompt, system_promt)
            critiques = result["critiques"]
        elif rating == "low":
            prompt = context + criticize_low_prompt + output_format
            result = self._safe_perform_query_return_json(prompt, system_promt)
            critiques = result["critiques"]
        else:
            return []
        return critiques

    def _rate_req(self, req, rating_prompt, model="gpt-4-turbo"):
        system_prompt = "You are an expert in analyzing requirement quality."
        req_prompt = f"The user has provided a requirement: {req}\n"
        prompt = req_prompt + rating_prompt
        # result = perform_query("", prompt, system_promt, model)
        result = self.llm_service.send_message(system_prompt, prompt)
        json_result = json.loads(result)
        context = "User Prompt: " + prompt + " System Response: " + result
        return json_result, context

    def _safe_perform_query_return_json(self, prompt: str, system_promt: str, max_retries=5):
        attempt = 0
        while attempt < max_retries:
            try:
                new_result = self.llm_service.send_message(system_promt, prompt)
                return json.loads(new_result)
            except json.JSONDecodeError:
                attempt += 1
        raise ValueError("Failed to get a valid JSON response after multiple attempts.")

    def _construct_necessary_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is necessary \
        Necessary means: \
        The requirement defines an essential capability, characteristic, constraint and/or quality factor. \
        If it is not included in the set of requirements, a deficiency in capability or characteristic will exist, \
        which cannot be fulfilled by implementing other requirements. The requirement is currently applicable \
        and has not been made obsolete by the passage of time. \
        Requirements with planned expiration dates or applicability dates are clearly identified. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_appropriate_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is appropriate \
        Appropriate means: \
        The specific intent and amount of detail of the requirement is appropriate to the level of the entity to which \
        it refers (level of abstraction appropriate to the level of entity). \
        This includes avoiding unnecessary constraints on the architecture or design \
        while allowing implementation independence to the extent possible. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_unambiguous_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is unambiguous \
        Unambiguous means: \
        The requirement is stated in such a way so that it can be interpreted in only one way. \
        The requirement is stated simply and is easy to understand. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        Here are detailed explanations for why ambiguous and why unambiguous. \
        Why unambiguous: \
        1. The requirement uses precise and well-defined terms. \
        2. It avoids subjective words (e.g., \"good,\" \"fast,\" \"efficient\") and instead uses measurable criteria. \
        3. The requirement does not depend on external context or implicit assumptions. \
        Why ambiguous: \
        1. It contains vague adjectives (e.g., \"The system shall work well\" - What does \"work well\" mean?). \
        2. It includes subjective descriptions (e.g., \"The interface should be user-friendly\" - Different users may have different interpretations of \"user-friendly\"). \
        3. It uses relative terms without a reference point (e.g., \"The model shall be better than before\" - What is \"before\"?). \
        4. There are implicit assumptions that are not explicitly stated (e.g., \"The data shall be secure\" \- Secure against what threats?). \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_complete_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is complete \
        Complete means: \
        The requirement sufficiently describes the necessary capability, characteristic, constraint or quality factor \
        to meet the entity need without needing other information to understand the requirement. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_singular_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is singular \
        Singular means: \
        The requirement states a single capability, characteristic, constraint or quality factor. \
        NOTE: Although a single requirement consists of a single function, quality or constraint, \
        it can have multiple conditions under which the requirement is to be met. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_feasible_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is feasible \
        Feasible means: \
        The requirement can be realized within system constraints (e.g., cost, schedule, technical) with acceptable risk. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_verifiable_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is verifiable \
        Verifiable means: \
        The requirement is structured and worded such that its realization can be proven (verified) to the customer’s satisfaction \
        at the level the requirements exists. Verifiability is enhanced when the requirement is measurable. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_correct_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is correct \
        Correct means: \
        The requirement is an accurate representation of the entity need from which it was transformed. "
        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output

    def _construct_conforming_rating_prompt(self, req_category: str, context: crit_dto.ProjectContext) -> str:
        intro = f"Your task is to evaluate the quality of a {req_category} requirement. \
        Evaluate whether the following requirement is conforming \
        Conforming means: \
        The individual items conform to an approved standard template and style for writing requirements, when applicable. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context))
        
        request = f" Request: \
        Based on the project context and the definition of the quality, \
        Evaluate the quality of this requirement, with three levels: high, medium, or low. \
        The result must be either high, medium, or low. \
        Explain your decision, why you think it is high, medium, or low. "

        output = f"Output: \
        The output should be in plain json format, \
        with only the following fields: eval_result, explanation. \
        Do not include any extra text or formatting! Do not inclue ```json."

        return intro + project_context + request + output
    

    """
    Service for set of requirements quality critique.
    """
    set_qualities = ["Complete", "Consistent", "Feasible", "Comprehensible", "Able to be validated"]
    # set_qualities = ["Complete"]

    async def critique_requirement_set(self, artifact_id: int, filter_criteria: str) -> crit_dto.SetCritiqueStats:

        artifact = self.db.query(Artifact).filter_by(artifact_id=artifact_id).first()
        if not artifact:
            raise ValueError(f"Artifact with ID {artifact_id} not found.")
        
        # Get project context
        project_context = crit_dto.ProjectContext(
            project_description=artifact.project_description,
            ml_task=artifact.ml_task,
            usage_context=artifact.usage_context,
            target_audience=artifact.target_audience,
            dataset_description=artifact.dataset_description
        )

        matching_requirements = []
        if filter_criteria == "All":
            # Get all requirements
            matching_requirements = self.db.query(Requirement).filter_by(artifact_id=artifact_id).all()
        else:
            category_names = filter_criteria.split(",")
            matching_requirements = self._get_requirements_by_categories(artifact_id, category_names)

        if not matching_requirements:
            return
        
        existing_evaluation = self.db.query(SetEvaluation).filter_by(
            artifact_id=artifact_id,
            filter_criteria=filter_criteria
        ).first()

        if existing_evaluation:
            self.db.query(EvaluationQuality).filter_by(
                evaluation_id=existing_evaluation.evaluation_id
            ).delete()
            self.db.commit()
            evaluation = existing_evaluation
        else:
            evaluation = SetEvaluation(
                artifact_id=artifact_id,
                filter_criteria=filter_criteria,
            )
            self.db.add(evaluation)
            self.db.commit()

        tasks = []
        for quality in self.set_qualities:
            task = asyncio.create_task(
                self._process_set_quality(
                    quality=quality, 
                    reqs=matching_requirements, 
                    filter_criteria=filter_criteria,
                    project_context=project_context,
                    evaluation_id=evaluation.evaluation_id
                )
            )

            tasks.append(task)

        completed = 0
        issues = []
        total = len(tasks)
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                if result:
                    quality_name = result["quality"]
                    summary = result["summary"]
                    critiques = result["critiques"]
                    print(f"Quality: {quality_name}, Summary: {summary}, Critiques: {critiques}")

                    if critiques:
                        issues.append(quality_name)
                
                completed += 1
            except Exception as e:
                traceback.print_exc()
                completed += 1
            
        return crit_dto.SetCritiqueStats(issues=issues)

    def _get_requirements_by_categories(self, artifact_id: int, category_names: list[str]) -> List[Requirement]:
        categories = self.db.query(Category).filter(
            Category.name.in_(category_names)
        ).all()

        category_ids = [c.category_id for c in categories]

        requirements = self.db.query(Requirement).filter(
            Requirement.artifact_id == artifact_id,
            Requirement.requirement_id.in_(
                self.db.query(RequirementCategory.requirement_id).filter(
                    RequirementCategory.category_id.in_(category_ids)
                ).distinct()
            )
        ).all()

        return requirements
    
    async def _process_set_quality(self, quality: str, reqs: List[Requirement], 
                             filter_criteria: str, project_context: crit_dto.ProjectContext, 
                             evaluation_id: int) -> Dict[str, Any]:
        try:
            result = await self._call_llm_for_set_critique(
                quality=quality,
                requirements=reqs,
                filter_criteria=filter_criteria,
                project_context=project_context
            )
            
            if result:
                self._store_set_quality_results(
                    evaluation_id=evaluation_id,
                    quality_name=result["quality"],
                    summary=result["summary"],
                    critiques=result["critiques"],
                    percentage=result["percentage"]
                )

            return result
        except Exception as e:
            traceback.print_exc()
            print(f"Error processing quality {quality}: {e}")
            return None
    
    async def _call_llm_for_set_critique(self, quality: str, requirements: List[Requirement], 
                                        filter_criteria: str, project_context: crit_dto.ProjectContext) -> Dict[str, Any]:

        requirements_content = "\n".join([
            f"Requirement {i+1}: {req.content}" for i, req in enumerate(requirements)
        ])

        if quality == "Complete":
            prompt = self._construct_set_complete_prompt(
                requirements_content = requirements_content,
                filter_criteria=filter_criteria,
                context = project_context
            )
        elif quality == "Consistent":
            prompt = self._construct_set_consistent_prompt(
                requirements_content = requirements_content,
                filter_criteria=filter_criteria,
                context = project_context
            )
        elif quality == "Feasible":
            prompt = self._construct_set_feasible_prompt(
                requirements_content = requirements_content,
                filter_criteria=filter_criteria,
                context = project_context
            )
        elif quality == "Comprehensible":
            prompt = self._construct_set_comprehensible_prompt(
                requirements_content = requirements_content,
                filter_criteria=filter_criteria,
                context = project_context
            )
        elif quality == "Able to be validated":
            prompt = self._construct_set_able_to_be_validated_prompt(
                requirements_content = requirements_content,
                filter_criteria=filter_criteria,
                context = project_context
            )
        else:
            return None
        
        system_prompt = "You are an expert in analyzing requirement sets and their quality."
        result = self._safe_perform_query_return_json(prompt, system_prompt)

        print(f"LLM response: {result}")

        all_problematic_ids = set()
        formatted_critiques = []

        for critique in result.get("critiques", []):
            if isinstance(critique, dict):
                req_ids = critique.get("requirement_ids", [])
                if len(req_ids) < 2:
                    continue

                issue = critique.get("issue", "")
                explanation = critique.get("explanation", "")

                all_problematic_ids.update(req_ids)

                formatted_critique = {
                    "set": [f"R{req_id}" for req_id in req_ids],
                    "critics": [f"{issue}. {explanation}"]
                }

                formatted_critiques.append(formatted_critique)
            else:
                continue
        
        total_reqs = len(requirements)
        problematic_reqs = len(all_problematic_ids)
        percentage = 100 if problematic_reqs == 0 else round(100 * (1 - (problematic_reqs / total_reqs)))

        return {
            "quality": quality,
            "summary": result.get("summary"),
            "critiques": formatted_critiques,
            "problematic_reqs": problematic_reqs,
            "percentage": percentage,
        }
    
    def _store_set_quality_results(self, evaluation_id: int, quality_name: str, 
                                   summary: str, critiques: List[str], percentage: int) -> None:
        
        quality = self.db.query(Quality).filter_by(name=quality_name).first()
        if not quality:
            quality = Quality(name=quality_name)
            self.db.add(quality)
            self.db.commit()

        evaluation_quality = EvaluationQuality(
            evaluation_id=evaluation_id,
            quality_id=quality.quality_id,
            summary=summary,
            percentage=percentage
        )
        self.db.add(evaluation_quality)
        self.db.flush()

        for critique_content in critiques:
            critique = EvaluationCritique(
                evaluation_quality_id=evaluation_quality.evaluation_quality_id,
                content=json.dumps(critique_content),
            )
            self.db.add(critique)

        self.db.commit()
    
    def _construct_set_complete_prompt(self, requirements_content: str, filter_criteria: str, context: crit_dto.ProjectContext) -> str:

        intro = f"Your task is to evaluate the quality of a set of requirements with categories: {filter_criteria}. \
        Evaluate whether the following set of requirements is complete as a set. \
        Complete as a set means: \
        The set of requirements stands alone such that it sufficiently describes \
        the necessary capabilities, characteristics, constraints or quality factors \
        to meet entity needs without needing further information. \
        In addition, the set does not contain any To Be Defined (TBD), To Be Specified (TBS), or To Be Resolved (TBR) clauses. \
        Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items, \
        determined by risks and dependencies. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context_parts = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context_parts))
        
        requirements = f"Requirements to evaluate: \n{requirements_content}"
        
        request = f" Request: \
        Based on the project context, the requirements set, and the definition of completeness, \
        evaluate whether the set of requirements is complete. \
        Provide a detailed summary explaining what aspects of completeness the set meets or fails to meet. \
        \
        Then identify issues that affect GROUPS of requirements (not individual requirements). \
        For each issue: \
        1. Each critique must target a unique combination of at least 2 requirements working together \
        2. Do not create multiple critiques for the exact same set of requirements \
        3. Different critiques can include overlapping requirements, but no two critiques should cover exactly the same requirements \
        4. Focus on how multiple requirements together create a completeness problem, not on individual requirement issues \
        5. Always include the requirement IDs involved in each critique"
        
        output = f"Output: \
        The output should be in plain JSON format with the following structure: \
        {{ \
            \"summary\": \"A detailed paragraph summarizing the completeness evaluation of the set\", \
            \"critiques\": [ \
                {{ \
                    \"issue\": \"Description of the issue\", \
                    \"requirement_ids\": [1, 3, 5], \
                    \"explanation\": \"Why these requirements together create a problem\" \
                }}, \
                ... \
            ] \
        }} \
        EIMPORTANT RULES: \
        - Each critique must include at least 2 requirement IDs \
        - No two critiques should have exactly the same set of requirement IDs \
        - Focus on group-level issues not individual requirement problems \
        - If no set-level issues are found, the critiques array can be empty \
        - Do not include any extra text or formatting! Do not inclue ```json."
            
        return intro + project_context + requirements + request + output

    def _construct_set_consistent_prompt(self, requirements_content: str, filter_criteria: str, context: crit_dto.ProjectContext) -> str:

        intro = f"Your task is to evaluate the quality of a set of requirements with categories: {filter_criteria}. \
        Evaluate whether the following set of requirements is consistent as a set. \
        Consistent as a set means: \
        The set of requirements contains individual requirements that are unique, \
        do not conflict with or overlap with other requirements in the set, \
        and the units and measurement systems are homogeneous. \
        The terminology used within the set of requirements is consistent, \
        i.e. the same term is used throughout the set to mean the same thing. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context_parts = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context_parts))
        
        requirements = f"Requirements to evaluate: \n{requirements_content}"
        
        request = f" Request: \
        Based on the project context, the requirements set, and the definition of completeness, \
        evaluate whether the set of requirements is consistent. \
        Provide a detailed summary explaining what aspects of completeness the set meets or fails to meet. \
        \
        Then identify issues that affect GROUPS of requirements (not individual requirements). \
        For each issue: \
        1. Each critique must target a unique combination of at least 2 requirements working together \
        2. Do not create multiple critiques for the exact same set of requirements \
        3. Different critiques can include overlapping requirements, but no two critiques should cover exactly the same requirements \
        4. Focus on how multiple requirements together create a completeness problem, not on individual requirement issues \
        5. Always include the requirement IDs involved in each critique"
        
        output = f"Output: \
        The output should be in plain JSON format with the following structure: \
        {{ \
            \"summary\": \"A detailed paragraph summarizing the completeness evaluation of the set\", \
            \"critiques\": [ \
                {{ \
                    \"issue\": \"Description of the issue\", \
                    \"requirement_ids\": [1, 3, 5], \
                    \"explanation\": \"Why these requirements together create a problem\" \
                }}, \
                ... \
            ] \
        }} \
        EIMPORTANT RULES: \
        - Each critique must include at least 2 requirement IDs \
        - No two critiques should have exactly the same set of requirement IDs \
        - Focus on group-level issues not individual requirement problems \
        - If no set-level issues are found, the critiques array can be empty \
        - Do not include any extra text or formatting! Do not inclue ```json."
            
        return intro + project_context + requirements + request + output

    def _construct_set_feasible_prompt(self, requirements_content: str, filter_criteria: str, context: crit_dto.ProjectContext) -> str:

        intro = f"Your task is to evaluate the quality of a set of requirements with categories: {filter_criteria}. \
        Evaluate whether the following set of requirements is feasible as a set. \
        Feasible as a set means: \
        The complete set of requirements can be realized within entity constraints \
        (e.g., cost, schedule, technical) with acceptable risk. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context_parts = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context_parts))
        
        requirements = f"Requirements to evaluate: \n{requirements_content}"
        
        request = f" Request: \
        Based on the project context, the requirements set, and the definition of completeness, \
        evaluate whether the set of requirements is feasible. \
        Provide a detailed summary explaining what aspects of completeness the set meets or fails to meet. \
        \
        Then identify issues that affect GROUPS of requirements (not individual requirements). \
        For each issue: \
        1. Each critique must target a unique combination of at least 2 requirements working together \
        2. Do not create multiple critiques for the exact same set of requirements \
        3. Different critiques can include overlapping requirements, but no two critiques should cover exactly the same requirements \
        4. Focus on how multiple requirements together create a completeness problem, not on individual requirement issues \
        5. Always include the requirement IDs involved in each critique"
        
        output = f"Output: \
        The output should be in plain JSON format with the following structure: \
        {{ \
            \"summary\": \"A detailed paragraph summarizing the completeness evaluation of the set\", \
            \"critiques\": [ \
                {{ \
                    \"issue\": \"Description of the issue\", \
                    \"requirement_ids\": [1, 3, 5], \
                    \"explanation\": \"Why these requirements together create a problem\" \
                }}, \
                ... \
            ] \
        }} \
        EIMPORTANT RULES: \
        - Each critique must include at least 2 requirement IDs \
        - No two critiques should have exactly the same set of requirement IDs \
        - Focus on group-level issues not individual requirement problems \
        - If no set-level issues are found, the critiques array can be empty \
        - Do not include any extra text or formatting! Do not inclue ```json."
            
        return intro + project_context + requirements + request + output

    def _construct_set_comprehensible_prompt(self, requirements_content: str, filter_criteria: str, context: crit_dto.ProjectContext) -> str:

        intro = f"Your task is to evaluate the quality of a set of requirements with categories: {filter_criteria}. \
        Evaluate whether the following set of requirements is comprehensible as a set. \
        Comprehensible as a set means: \
        The set of requirements is written such that it is clear as to what is expected by the entity and its relation to the system of which it is a part. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context_parts = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context_parts))
        
        requirements = f"Requirements to evaluate: \n{requirements_content}"
        
        request = f" Request: \
        Based on the project context, the requirements set, and the definition of completeness, \
        evaluate whether the set of requirements is comprehensible. \
        Provide a detailed summary explaining what aspects of completeness the set meets or fails to meet. \
        \
        Then identify issues that affect GROUPS of requirements (not individual requirements). \
        For each issue: \
        1. Each critique must target a unique combination of at least 2 requirements working together \
        2. Do not create multiple critiques for the exact same set of requirements \
        3. Different critiques can include overlapping requirements, but no two critiques should cover exactly the same requirements \
        4. Focus on how multiple requirements together create a completeness problem, not on individual requirement issues \
        5. Always include the requirement IDs involved in each critique"
        
        output = f"Output: \
        The output should be in plain JSON format with the following structure: \
        {{ \
            \"summary\": \"A detailed paragraph summarizing the completeness evaluation of the set\", \
            \"critiques\": [ \
                {{ \
                    \"issue\": \"Description of the issue\", \
                    \"requirement_ids\": [1, 3, 5], \
                    \"explanation\": \"Why these requirements together create a problem\" \
                }}, \
                ... \
            ] \
        }} \
        EIMPORTANT RULES: \
        - Each critique must include at least 2 requirement IDs \
        - No two critiques should have exactly the same set of requirement IDs \
        - Focus on group-level issues not individual requirement problems \
        - If no set-level issues are found, the critiques array can be empty \
        - Do not include any extra text or formatting! Do not inclue ```json."
            
        return intro + project_context + requirements + request + output

    def _construct_set_able_to_be_validated_prompt(self, requirements_content: str, filter_criteria: str, context: crit_dto.ProjectContext) -> str:

        intro = f"Your task is to evaluate the quality of a set of requirements with categories: {filter_criteria}. \
        Evaluate whether the following set of requirements is able to be validated as a set. \
        Able to be validated as a set means: \
        The set of requirements stands alone such that it sufficiently describes \
        the necessary capabilities, characteristics, constraints or quality factors \
        to meet entity needs without needing further information. \
        In addition, the set does not contain any To Be Defined (TBD), To Be Specified (TBS), or To Be Resolved (TBR) clauses. \
        Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items, \
        determined by risks and dependencies. "

        project_context = f"Project Context: \
        Project Description: {context.project_description}"
        context_parts = [
            f"ML Task: {context.ml_task}" if context.ml_task else "",
            f"Usage Context: {context.usage_context}" if context.usage_context else "",
            f"Target Audience: {context.target_audience}" if context.target_audience else "",
            f"Dataset Description: {context.dataset_description}" if context.dataset_description else ""
        ]
        project_context = project_context + ", ".join(filter(None, context_parts))
        
        requirements = f"Requirements to evaluate: \n{requirements_content}"
        
        request = f" Request: \
        Based on the project context, the requirements set, and the definition of completeness, \
        evaluate whether the set of requirements is able to be validated. \
        Provide a detailed summary explaining what aspects of completeness the set meets or fails to meet. \
        \
        Then identify issues that affect GROUPS of requirements (not individual requirements). \
        For each issue: \
        1. Each critique must target a unique combination of at least 2 requirements working together \
        2. Do not create multiple critiques for the exact same set of requirements \
        3. Different critiques can include overlapping requirements, but no two critiques should cover exactly the same requirements \
        4. Focus on how multiple requirements together create a completeness problem, not on individual requirement issues \
        5. Always include the requirement IDs involved in each critique"
        
        output = f"Output: \
        The output should be in plain JSON format with the following structure: \
        {{ \
            \"summary\": \"A detailed paragraph summarizing the completeness evaluation of the set\", \
            \"critiques\": [ \
                {{ \
                    \"issue\": \"Description of the issue\", \
                    \"requirement_ids\": [1, 3, 5], \
                    \"explanation\": \"Why these requirements together create a problem\" \
                }}, \
                ... \
            ] \
        }} \
        EIMPORTANT RULES: \
        - Each critique must include at least 2 requirement IDs \
        - No two critiques should have exactly the same set of requirement IDs \
        - Focus on group-level issues not individual requirement problems \
        - If no set-level issues are found, the critiques array can be empty \
        - Do not include any extra text or formatting! Do not inclue ```json."
            
        return intro + project_context + requirements + request + output
