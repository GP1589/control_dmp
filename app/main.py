import os

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, HttpUrl

# Validar en runtime la existencia de la API Key
if "GEMINI_API_KEY" not in os.environ:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is missing. "
        "It MUST be injected in runtime."
    )

app = FastAPI(title="Web QA Gemini App")

# Inicializamos el cliente de google-genai
client = genai.Client()


class AskRequest(BaseModel):
    url: HttpUrl
    question: str


class AskResponse(BaseModel):
    response: str


@app.get("/health")
def health_check():
    """Endpoint para verificar que la API está arriba."""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Endpoint que descarga el contenido de una URL y usa Gemini
    para responder una pregunta sobre ella.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # 1. Descargar el contenido de la URL
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            )
        }
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as http_client:
            resp = await http_client.get(str(request.url))
            resp.raise_for_status()
            html_content = resp.text
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error fetching URL: {str(e)}"
        ) from e

    # 2. Extraer el texto limpio del HTML
    soup = BeautifulSoup(html_content, "html.parser")
    # Remover scripts y estilos
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    text = soup.get_text(separator="\n")
    # Limpiar lineas vacias
    lines = (line.strip() for line in text.splitlines())
    clean_text = "\n".join(
        chunk for line in lines for chunk in line.split("  ") if chunk
    )

    # Limitar el texto a unos caracteres razonables por precaución
    max_chars = 40000
    if len(clean_text) > max_chars:
        clean_text = clean_text[:max_chars] + "\n[Text truncated...]"

    prompt = (
        f"Context ({request.url}):\n\n"
        f"{clean_text}\n\n"
        f"Question: {request.question}"
    )

    # 3. Consultar a Gemini
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an expert AI assistant. Answer the question based "
                    "STRICTLY on the provided context. "
                    "CRITICAL: You MUST respond in the same language as the user's "
                    "Question. If the Question is in English, respond in English. "
                    "If it is in Spanish, respond in Spanish. "
                    "Your answer should be concise, but MUST be a complete sentence "
                    "that includes enough context to be fully understood on its own."
                )
            )
        )
        return AskResponse(response=response.text or "")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error communicating with Google AI API: {str(e)}"
        ) from e
