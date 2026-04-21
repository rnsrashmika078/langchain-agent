from typing import Optional
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import requests
from reasoning_agent import requestLLM
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from langchain_ollama import ChatOllama #test only

from tools import pdf_generate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LLMRequest(BaseModel):
    request: str
    stop: bool
class GeneratePDF(BaseModel):
    html_code: str
    file_name: str

class TestVision(BaseModel):
    image: str


@app.post("/request")
def request_llm_answer(data: LLMRequest):
    try:
        return StreamingResponse(requestLLM(data.request), media_type="text/plain")
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail=f"error while generate response: {str(e)}"
        )

@app.post("/generate_pdf")
def request_pdf_generate(data:GeneratePDF):
    try:
        print(f"data {data.file_name}")
        pdf_generate(data.html_code,data.file_name)
    except Exception as e:
       return HTTPException(
            status_code=500,
            detail=f"Error while generating PDF: {str(e)}"
        )
       
#   Test only route
@app.post("/vision")
def request_pdf_generate(data:TestVision):
    try:
        # print(data.image)
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma4:e2b",
                "messages": [
                    {
                        "role": "user",
                        "content": "Hi there",
                    }
                ]
            }
        )
        print(f"response {response.content}")

        return response.json()

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))