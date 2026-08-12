from app.core.config import settings
from app.services.agent_tools import tools
from app.services.memory_service import get_session_history
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


def create_agent():
    # Setup LLM
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_API_BASE,
        temperature=0.3,
        streaming=True
    )
    
    # Define prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres NutriGraph AI, un asistente experto en nutrición. "
                   "REGLA ABSOLUTA DE TOOL CALLING: Para CUALQUIER consulta o recomendación sobre recetas, qué comer, cenas, desayunos o ingredientes, DEBES LLAMAR OBLIGATORIAMENTE a la herramienta 'buscar_recetas_avanzado'. ESTÁ TOTALMENTE PROHIBIDO responder con alimentos de tu propia memoria sin haber obtenido primero los datos de la herramienta. "
                   "RESTRICCIONES DIETÉTICAS ESTRICTAS: Revisa el contexto del usuario. Si la dieta del usuario es Vegana (o el usuario indica que es vegano), NUNCA propongas ingredientes de origen animal (pollo, pavo, ternera, huevo, carne, pescado, lácteos, miel). En la llamada a la herramienta 'buscar_recetas_avanzado', debes incluir `diet_type='Vegana'` si el usuario es o indica ser vegano. "
                   "Si la dieta es Vegetariana, no propongas carne ni pescado. Si tiene intolerancias, jamás sugieras alimentos que las contengan. "
                   "Para ver el detalle completo de ingredientes de una receta, primero busca su ID con buscar_recetas_avanzado y luego usa obtener_desglose_receta. "
                   "IMPORTANTE: NUNCA menciones detalles técnicos de la base de datos (como IDs, UUIDs, nodos u otros datos internos) en tus respuestas al usuario. Muestra solo información útil, apetitosa y amigable."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create Executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor

import time
import asyncio
from app.models.chat_repository import chat_repository

RECENT_LATENCIES: list[float] = []

def get_recent_latencies() -> list[float]:
    return RECENT_LATENCIES

async def stream_agent_response(user_id: str, session_id: str, user_input: str):
    start_time = time.perf_counter()
    agent_executor = create_agent()
    memory = get_session_history(session_id)
    chat_history = memory.messages
    
    # Obtain user profile details from Neo4j (diet, intolerances, name)
    user_profile = await chat_repository.get_user_profile(user_id)
    diet_type = user_profile.get("diet_type") or "No especificada"
    intolerances_list = user_profile.get("intolerances") or []
    intolerances_str = ", ".join(intolerances_list) if intolerances_list else "Ninguna"
    first_name = user_profile.get("first_name") or ""
    
    # If Redis is empty but we have a session_id, try loading from Neo4j
    if not chat_history:
        db_messages = await chat_repository.get_conversation_messages(session_id)
        for msg in db_messages:
            if msg["role"] == "user":
                memory.add_user_message(msg["content"])
            elif msg["role"] == "ai":
                memory.add_ai_message(msg["content"])
        chat_history = memory.messages

    context_header = f"[Contexto interno: Usuario={user_id} | Nombre={first_name} | Dieta={diet_type} | Intolerancias={intolerances_str}] "
    input_data = {
        "input": context_header + user_input,
        "chat_history": chat_history
    }
    
    # Save the user message to Neo4j (fire and forget)
    title = user_input[:30] if not chat_history else None
    asyncio.create_task(chat_repository.save_message(user_id, session_id, "user", user_input, title=title))
    
    # Add user message to Redis history
    memory.add_user_message(user_input)
    
    full_response = ""
    # We use astream_events to get fine-grained token streaming
    async for event in agent_executor.astream_events(input_data, version="v1"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                full_response += content
                yield content
    
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    RECENT_LATENCIES.append(elapsed_ms)
    if len(RECENT_LATENCIES) > 100:
        RECENT_LATENCIES.pop(0)

    # Save the complete AI response to history
    memory.add_ai_message(full_response)
    asyncio.create_task(chat_repository.save_message(user_id, session_id, "ai", full_response))


