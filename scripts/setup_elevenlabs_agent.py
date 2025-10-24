#!/usr/bin/env python3
"""
Script para crear y configurar el agente conversacional de ElevenLabs
para el demo de cambio de citas médicas.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")

def create_appointment_agent():
    """Crea el agente conversacional para cambio de citas"""

    client = ElevenLabs(api_key=API_KEY)

    # Agent configuration
    agent_config = {
        "name": "Asistente Médico SmartSalud",
        "prompt": {
            "prompt": """Eres un asistente médico virtual amable y profesional del CESFAM SmartSalud.

Tu trabajo es ayudar a los pacientes a:
1. Consultar información sobre su cita médica actual
2. Cambiar la fecha/hora de su cita si lo necesitan
3. Confirmar o cancelar citas

IMPORTANTE:
- Habla en español chileno, de forma natural y amigable
- Sé breve y al grano (los pacientes son adultos mayores)
- Cuando el paciente quiera cambiar la hora, usa la función 'reschedule_appointment'
- Al terminar la conversación, usa 'end_conversation' para enviar la confirmación por WhatsApp

FLUJO:
1. Saluda y pregunta el RUT del paciente
2. Busca su cita con 'get_patient_appointment'
3. Informa la fecha/hora actual
4. Si quiere cambiar, ofrece opciones con 'get_available_slots'
5. Confirma el cambio con 'reschedule_appointment'
6. Despídete y cierra con 'end_conversation'

Tono: Amable pero eficiente. Como una recepcionista de consultorio."""
        },
        "language": "es",
        "voice": {
            "voice_id": "ErXwobaYiN019PkySvjV"  # Antoni - Spanish male voice
        },
        "model": {
            "model_id": "eleven_flash_v2_5"  # Ultra-low latency
        },
        "conversation_config": {
            "asr": {
                "model": "scribe_v1",  # 99 languages
                "language": "es"
            },
            "tts": {
                "model_id": "eleven_flash_v2_5",
                "voice_id": "ErXwobaYiN019PkySvjV"
            }
        },
        "custom_llm": {
            "url": "http://localhost:8001/api/elevenlabs/llm",
            "extra_body": {}
        },
        "custom_tools": [
            {
                "name": "get_patient_appointment",
                "description": "Busca la cita médica actual del paciente por su RUT",
                "url": "http://localhost:8001/api/elevenlabs/tools/get_appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rut": {
                            "type": "string",
                            "description": "RUT del paciente (ej: 12345678-9)"
                        }
                    },
                    "required": ["rut"]
                }
            },
            {
                "name": "get_available_slots",
                "description": "Obtiene horarios disponibles para reagendar la cita",
                "url": "http://localhost:8001/api/elevenlabs/tools/get_slots",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doctor_id": {
                            "type": "integer",
                            "description": "ID del doctor"
                        },
                        "date": {
                            "type": "string",
                            "description": "Fecha deseada (YYYY-MM-DD)"
                        }
                    },
                    "required": ["doctor_id"]
                }
            },
            {
                "name": "reschedule_appointment",
                "description": "Cambia la fecha/hora de la cita del paciente. ESTO ACTUALIZA EL CALENDARIO EN TIEMPO REAL.",
                "url": "http://localhost:8001/api/elevenlabs/tools/reschedule",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "appointment_id": {
                            "type": "integer",
                            "description": "ID de la cita a cambiar"
                        },
                        "new_datetime": {
                            "type": "string",
                            "description": "Nueva fecha y hora (YYYY-MM-DD HH:MM)"
                        }
                    },
                    "required": ["appointment_id", "new_datetime"]
                }
            },
            {
                "name": "end_conversation",
                "description": "Finaliza la conversación y envía confirmación por WhatsApp al paciente",
                "url": "http://localhost:8001/api/elevenlabs/tools/end_conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_rut": {
                            "type": "string",
                            "description": "RUT del paciente"
                        },
                        "summary": {
                            "type": "string",
                            "description": "Resumen de lo acordado en la conversación"
                        }
                    },
                    "required": ["patient_rut", "summary"]
                }
            }
        ]
    }

    print("🤖 Creando agente en ElevenLabs...")
    print(f"📝 Nombre: {agent_config['name']}")
    print(f"🗣️ Voz: {agent_config['voice']['voice_id']}")
    print(f"🌐 Idioma: {agent_config['language']}")
    print(f"🔧 Funciones: {len(agent_config['custom_tools'])}")

    # Note: The actual API call would be:
    # agent = client.conversational_ai.create_agent(**agent_config)

    # For now, we'll create it manually in the dashboard
    print("\n⚠️  Para crear el agente, ve a:")
    print("   https://elevenlabs.io/app/conversational-ai")
    print("\n📋 Copia esta configuración:")
    import json
    print(json.dumps(agent_config, indent=2, ensure_ascii=False))

    return agent_config

if __name__ == "__main__":
    config = create_appointment_agent()

    print("\n✅ Configuración del agente lista!")
    print("\n📝 Siguiente paso:")
    print("   1. Crea el agente en https://elevenlabs.io/app/conversational-ai")
    print("   2. Copia el AGENT_ID y agrégalo a .env como ELEVENLABS_AGENT_ID")
    print("   3. Ejecuta el backend: PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001")
