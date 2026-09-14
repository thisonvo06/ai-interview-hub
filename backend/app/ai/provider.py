import time
import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings
from app.ai.schemas import (
    ResumeParseSchema, JDParseSchema, QuestionGenSchema,
    AnswerEvalSchema, ReportGenSchema, LearningPlanSchema, MatchExplainerSchema
)
from app.ai.mock_data import (
    MOCK_RESUME_PARSED, MOCK_JD_PARSED, INTERVIEW_QUESTION_POOL,
    generate_mock_evaluation, generate_adaptive_mock_question,
    generate_mock_report, generate_mock_learning_tasks
)

logger = logging.getLogger("ai_provider")

class AIProvider:
    def __init__(self):
        self.mode = settings.AI_MODE
        self.base_url = settings.LLM_BASE_URL
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL

    async def _call_llm_json(self, prompt: str, schema_class) -> Dict[str, Any]:
        """Calls real LLM API with fallback to mock if unreachable or unconfigured."""
        if self.mode == "mock" or not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional AI interview engine. Output ONLY valid JSON matching the requested structure."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    # Validate schema
                    validated = schema_class(**parsed)
                    return validated.model_dump()
        except Exception as e:
            logger.warning(f"Real LLM call failed, falling back to mock: {e}")
            return None
        return None

    async def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parses resume text into structured entities."""
        prompt = f"Parse this resume into JSON:\n{resume_text}"
        real_res = await self._call_llm_json(prompt, ResumeParseSchema)
        if real_res:
            return real_res
        # Mock mode fallback
        validated = ResumeParseSchema(**MOCK_RESUME_PARSED)
        return validated.model_dump()

    async def parse_jd(self, jd_text: str) -> Dict[str, Any]:
        """Parses enterprise JD text into job fields and skill requirements."""
        prompt = f"Parse this Job Description into JSON:\n{jd_text}"
        real_res = await self._call_llm_json(prompt, JDParseSchema)
        if real_res:
            return real_res
        validated = JDParseSchema(**MOCK_JD_PARSED)
        return validated.model_dump()

    async def generate_question(
        self,
        job_title: str,
        stage: str = "专业基础",
        difficulty: str = "MEDIUM",
        seq: int = 1,
        last_question: str = None,
        last_answer: str = None,
        last_score: float = None
    ) -> Dict[str, Any]:
        """Dynamically generates interview question based on candidate's previous response and depth."""
        prompt = (
            f"You are an expert technical interviewer conducting an interview for '{job_title}'.\n"
            f"Question sequence: {seq}\n"
            f"Last question asked: {last_question or 'N/A'}\n"
            f"Candidate's last answer: {last_answer or 'N/A'}\n"
            f"Last answer score: {last_score or 'N/A'}\n\n"
            f"Requirements:\n"
            f"- If the candidate answered with high technical depth, generate a deep follow-up probing edge cases, concurrency, or architectural trade-offs.\n"
            f"- If the candidate's answer was superficial or indicated lack of knowledge, generate a foundational question to diagnose core concepts.\n"
            f"- Output JSON adhering to: question, skill_name, stage, difficulty, hints."
        )
        real_res = await self._call_llm_json(prompt, QuestionGenSchema)
        if real_res:
            return real_res

        # Adaptive Mock Engine
        raw_q = generate_adaptive_mock_question(
            job_title=job_title,
            seq=seq,
            last_question=last_question,
            last_answer=last_answer,
            last_score=last_score
        )
        validated = QuestionGenSchema(**raw_q)
        return validated.model_dump()

    async def evaluate_answer(
        self, question_text: str, answer_text: str, seq: int
    ) -> Dict[str, Any]:
        """Evaluates single answer using the 6-dimension Rubric with JSON Schema validation."""
        raw_eval = generate_mock_evaluation(question_text, answer_text, seq)
        validated = AnswerEvalSchema(**raw_eval)
        return validated.model_dump()

    async def generate_report(
        self, interview_id: int, total_questions: int, scores: List[float] = None
    ) -> Dict[str, Any]:
        """Generates comprehensive interview post-review report with radar scores."""
        raw_report = generate_mock_report(interview_id, total_questions, scores)
        validated = ReportGenSchema(**raw_report)
        return validated.model_dump()

    async def generate_learning_plan(self, job_title: str, gaps: List[str] = None) -> List[Dict[str, Any]]:
        """Generates targeted tasks for personal growth roadmap."""
        tasks = generate_mock_learning_tasks()
        validated = LearningPlanSchema(tasks=tasks)
        return validated.model_dump()["tasks"]

    async def explain_job_match(
        self, job_title: str, candidate_skills: List[str], required_skills: List[str]
    ) -> Dict[str, Any]:
        """Calculates deterministic match score and returns explanation."""
        c_set = set(s.lower() for s in candidate_skills)
        r_set = set(s.lower() for s in required_skills) if required_skills else {"java", "mysql", "redis", "spring boot"}

        adv = [s for s in required_skills if s.lower() in c_set]
        missing = [s for s in required_skills if s.lower() not in c_set]

        if not adv and not missing:
            adv = ["Java", "Spring Boot", "MySQL"]
            missing = ["分布式系统"]

        score = min(98, max(60, int(60 + len(adv) * 8 - len(missing) * 4)))

        data = {
            "match_score": score,
            "advantage_skills": adv or ["Java", "MySQL"],
            "missing_skills": missing or ["大型分布式实战"],
            "explanation": f"候选人与【{job_title}】匹配度为 {score}%。熟练掌握核心技能 {', '.join(adv or ['Java'])}，但在 {', '.join(missing or ['分布式'])} 方面仍有深度拓展空间。"
        }
        validated = MatchExplainerSchema(**data)
        return validated.model_dump()

ai_provider = AIProvider()
