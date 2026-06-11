# Control - App de IA/ML en Contenedor (UNI 2026)

Esta es una API de Asistente de IA Multilingüe implementada con **FastAPI** y el modelo `gemini-2.5-flash` a través del SDK `google-genai`. La aplicación está empaquetada en un contenedor Docker optimizado para producción usando `uv`. 
Cumple con el caso de uso de **QA sobre una página web**.

## Requisitos Previos
- Docker instalado en la máquina.
- API KEY de Google AI Studio.

## 1. Cómo construir la imagen

Ejecuta el siguiente comando en la raíz del proyecto para construir la imagen de Docker de forma rápida:

```bash
docker build -t uni-gemini-app .
```

## 2. Cómo correrla (pasando la API Key)

El contenedor requiere la inyección de la variable de entorno `GEMINI_API_KEY` durante el tiempo de ejecución. El puerto interno de la API es el `8000`.

```bash
docker run --rm -p 8000:8000 -e GEMINI_API_KEY="TU_API_KEY_AQUÍ" uni-gemini-app
```

## 3. Ejemplo exacto de entrada y respuesta

Una vez que el contenedor esté corriendo, la API descargará el contenido de la URL enviada al endpoint `/ask` y responderá a la pregunta de forma multilingüe basada en ese contexto.

### Ejemplo en Español
```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"url": "https://es.wikipedia.org/wiki/J%C3%BApiter_(planeta)", "question": "¿Es el planeta más grande del sistema solar?"}'
```

**Respuesta Esperada:**
```json
{
    "response": "Sí, Júpiter es el planeta más grande del sistema solar y el quinto en orden de lejanía al Sol."
}
```

### Ejemplo en Inglés
```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"url": "https://en.wikipedia.org/wiki/Docker_(software)", "question": "What is Docker used for?"}'
```

**Respuesta Esperada:**
```json
{
    "response": "Docker is a set of products that uses operating system-level virtualization to deliver software in packages called containers, automating the deployment of applications within lightweight containers to run consistently across different computing environments."
}
```
