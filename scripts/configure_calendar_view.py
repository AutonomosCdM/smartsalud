"""
Script para configurar la vista del calendario con horarios de trabajo.

Google Calendar no permite configurar horarios por API, pero podemos:
1. Crear eventos solo en horario laboral (8:00 - 17:00)
2. Dar instrucciones para configurar manualmente
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def show_calendar_configuration_instructions():
    """
    Mostrar instrucciones para configurar horarios de trabajo en Google Calendar.
    """
    print("=" * 70)
    print("CONFIGURACIÓN DE VISTA DE GOOGLE CALENDAR")
    print("=" * 70)
    print()
    print("📋 Para mostrar solo horario laboral (8:00 - 17:00):")
    print()
    print("1. Ve a Google Calendar: https://calendar.google.com")
    print()
    print("2. Haz clic en el ícono de ⚙️ (Configuración) arriba a la derecha")
    print()
    print("3. En el menú lateral, busca 'Ver opciones'")
    print()
    print("4. Configura:")
    print("   • Horario de trabajo: 08:00 - 17:00")
    print("   • Días laborales: Lunes a Viernes")
    print("   • Zona horaria: America/Santiago")
    print()
    print("5. También puedes ajustar la vista por defecto:")
    print("   • Vista semanal o diaria")
    print("   • Ocultar fines de semana si no trabajas esos días")
    print()
    print("=" * 70)
    print()
    print("💡 ALTERNATIVA: Usar vistas personalizadas")
    print()
    print("En la vista de calendario, puedes:")
    print("• Hacer zoom en el horario arrastrando las horas")
    print("• Hacer scroll para ver solo el rango que te interesa")
    print("• Usar la vista '4 días' para ver mejor los slots")
    print()
    print("=" * 70)
    print()


if __name__ == '__main__':
    show_calendar_configuration_instructions()
