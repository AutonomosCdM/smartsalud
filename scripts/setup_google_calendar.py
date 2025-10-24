"""
Script de autenticación OAuth2 para Google Calendar.

Genera token.json con permisos de escritura en Google Calendar.
Solo necesita ejecutarse una vez por cuenta.

Uso:
    python scripts/setup_google_calendar.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes necesarios para leer y escribir en Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Rutas de archivos
CREDENTIALS_FILE = project_root / 'credentials.json'
TOKEN_FILE = project_root / 'token.json'


def setup_google_calendar():
    """
    Configura autenticación OAuth2 para Google Calendar.

    Este script:
    1. Verifica que exista credentials.json
    2. Abre navegador para autorización
    3. Guarda token.json para uso futuro
    4. Verifica que el token funciona consultando calendarios
    """
    print("=" * 70)
    print("CONFIGURACIÓN DE GOOGLE CALENDAR - smartSalud V2")
    print("=" * 70)
    print()

    # Verificar que existe credentials.json
    if not CREDENTIALS_FILE.exists():
        print("❌ ERROR: No se encontró credentials.json")
        print()
        print("Por favor:")
        print("1. Ve a Google Cloud Console")
        print("2. Crea un proyecto (o usa uno existente)")
        print("3. Habilita Google Calendar API")
        print("4. Crea credenciales OAuth 2.0")
        print("5. Descarga el archivo JSON")
        print(f"6. Guárdalo como: {CREDENTIALS_FILE}")
        print()
        return False

    print(f"✅ Encontrado: {CREDENTIALS_FILE}")
    print()

    creds = None

    # Cargar token existente si existe
    if TOKEN_FILE.exists():
        print(f"⚠️  Ya existe {TOKEN_FILE}")
        print("🔄 Verificando validez del token...")
        print()
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Si no hay credenciales válidas, iniciar flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refrescando token expirado...")
            creds.refresh(Request())
        else:
            print("🌐 Iniciando flujo de autenticación OAuth2...")
            print()
            print("Se abrirá tu navegador para que autorices el acceso.")
            print("Por favor:")
            print("1. Inicia sesión con tu cuenta de Google (cesar@autonomos.de)")
            print("2. Autoriza el acceso a Google Calendar")
            print("3. Cierra el navegador cuando termine")
            print()

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Guardar credenciales para la próxima vez
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

        print(f"✅ Token guardado: {TOKEN_FILE}")
        print()

    # Verificar que funciona consultando calendarios
    print("🧪 Verificando acceso a Google Calendar...")
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Listar calendarios disponibles
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        if not calendars:
            print("⚠️  No se encontraron calendarios")
            return False

        print(f"✅ Acceso verificado! Encontrados {len(calendars)} calendario(s):")
        print()

        for calendar in calendars:
            cal_id = calendar['id']
            cal_name = calendar.get('summary', 'Sin nombre')
            is_primary = ' (PRIMARY)' if calendar.get('primary', False) else ''
            print(f"   📅 {cal_name}{is_primary}")
            print(f"      ID: {cal_id}")
            print()

        print("=" * 70)
        print("✅ CONFIGURACIÓN EXITOSA")
        print("=" * 70)
        print()
        print("Ahora puedes:")
        print("1. Ejecutar el servidor: PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload")
        print("2. El sistema usará automáticamente tu token.json")
        print("3. Las citas se sincronizarán con tu Google Calendar")
        print()

        return True

    except Exception as e:
        print(f"❌ ERROR al verificar acceso: {e}")
        return False


if __name__ == '__main__':
    success = setup_google_calendar()
    sys.exit(0 if success else 1)
