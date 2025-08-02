from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(description="The question to be answered")


class QABase(QuestionRequest):
    answer: str = Field(description="The answer to the question")


class QAAnalytics(QABase):
    thought: str = Field(description="The thought process of the model")
    topic: str = Field(description="The topic of the question")