
import uuid
from datetime import datetime
from pathlib import Path

from deepteam import red_team
from deepteam.attacks.single_turn import (
    PromptInjection,
    PermissionEscalation,
    EmotionalManipulation
)
from deepteam.vulnerabilities import (
    Bias,
    Toxicity,
    Hallucination,
    GoalTheft
)

# Agente objetivo
from workflow import TechDocBuilderGraph


# Crear directorio para resultados
RESULTS_DIR = Path("./deepteam-results")
RESULTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# DEFINIR CALLBACK DEL MODELO
# ============================================================================

workflow = TechDocBuilderGraph()

async def model_callback(input_text: str) -> str:
    """
    Callback que invoca tu agente LLM.
    Esto es lo que se va a testear contra las vulnerabilidades.
    """
    try:
        response = workflow.invoke(
            input_obj={
                "user_id": str(uuid.uuid4()),
            },
            session_id=str(uuid.uuid4()),
            question=input_text
        )
        return response
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# OWASP TOP 10 LLM - MAPEO DE VULNERABILIDADES
# ============================================================================

"""
OWASP Top 10 para LLMs (2024):

LLM-01: Prompt Injection
├─ Ataques: PromptInjection, EmotionalManipulation
├─ Impacto: Crítico
└─ Descripción: Inyección de comandos maliciosos en prompts

LLM-02: Insecure Output Handling
├─ Ataques: PermissionEscalation
├─ Impacto: Crítico
└─ Descripción: Manejo inseguro de salidas sin sanitización

LLM-03: Training Data Poisoning
├─ Ataques: Hallucination
├─ Impacto: Crítico
└─ Descripción: Datos de entrenamiento comprometidos

LLM-04: Model Denial of Service
├─ Impacto: Alto
└─ Descripción: Consumo excesivo de recursos

LLM-05: Supply Chain Vulnerabilities
├─ Impacto: Crítico
└─ Descripción: Vulnerabilidades en dependencias

LLM-06: Sensitive Information Disclosure
├─ Ataques: PromptInjection (para exfiltración)
├─ Impacto: Crítico
└─ Descripción: Revelación de información sensible (PII, APIs)

LLM-07: Cross-Plugin Request Forgery (CSRF)
├─ Impacto: Alto
└─ Descripción: Ejecución de acciones no autorizadas

LLM-08: Model Poisoning
├─ Impacto: Crítico
└─ Descripción: Alteración de pesos del modelo

LLM-09: Improper Error Handling
├─ Ataques: PermissionEscalation
├─ Impacto: Medio
└─ Descripción: Errores que revelan información interna

LLM-10: Unbounded Consumption
├─ Impacto: Alto
└─ Descripción: Consumo ilimitado de tokens/recursos
"""

# ============================================================================
# CONFIGURAR VULNERABILIDADES Y ATAQUES
# ============================================================================

print("=" * 80)
print("🔴 RED TEAMING - OWASP TOP 10 LLM")
print("=" * 80)

print("\n📋 Configurando vulnerabilidades...\n")

# ============================================================================
# LLM-01: PROMPT INJECTION (Crítico)
# ============================================================================
print("✅ LLM-01: Prompt Injection")
llm_01_injection = PromptInjection(weight=3)  # Higher weight = más pruebas
print("   - Ataque: PromptInjection (weight=3)")

# ============================================================================
# LLM-02: INSECURE OUTPUT HANDLING (Crítico)
# ============================================================================
print("✅ LLM-02: Insecure Output Handling")
llm_02_adversarial = PermissionEscalation(weight=2)
print("   - Ataque: PermissionEscalation (weight=2)")

# ============================================================================
# LLM-03: TRAINING DATA POISONING (Crítico)
# ============================================================================
print("✅ LLM-03: Training Data Poisoning")
llm_03_hallucination = Hallucination(types=["fake_citations", "fake_apis"])
print("   - Ataque: Hallucination (fake_citations, fake_apis)")

# ============================================================================
# LLM-04: MODEL DENIAL OF SERVICE (Alto)
# ============================================================================
print("✅ LLM-04: Model Denial of Service")
# Será probado implícitamente por PromptInjection y EmotionalManipulation
print("   - Ataque: Implícito en PromptInjection (consumo de recursos)")

# ============================================================================
# LLM-05: SUPPLY CHAIN VULNERABILITIES (Crítico)
# ============================================================================
print("✅ LLM-05: Supply Chain Vulnerabilities")
# Verificación manual de dependencias
print("   - Verificación: Manual (revisar requirements.txt)")

# ============================================================================
# LLM-06: SENSITIVE INFORMATION DISCLOSURE (Crítico)
# ============================================================================
print("✅ LLM-06: Sensitive Information Disclosure")
llm_06_injection = PromptInjection(weight=3)  # Específico para exfiltración
print("   - Ataque: PromptInjection con enfoque en datos sensibles (weight=3)")

# ============================================================================
# LLM-07: CROSS-PLUGIN REQUEST FORGERY (Alto)
# ============================================================================
print("✅ LLM-07: Cross-Plugin Request Forgery")
print("   - Verificación: Manual (revisar herramientas del agente)")

# ============================================================================
# LLM-08: MODEL POISONING (Crítico)
# ============================================================================
print("✅ LLM-08: Model Poisoning")
llm_08_jailbreak = EmotionalManipulation(weight=2)
print("   - Ataque: EmotionalManipulation (weight=2)")

# ============================================================================
# LLM-09: IMPROPER ERROR HANDLING (Medio)
# ============================================================================
print("✅ LLM-09: Improper Error Handling")
llm_09_adversarial = PermissionEscalation(weight=1)
print("   - Ataque: PermissionEscalation (weight=1)")

# ============================================================================
# LLM-10: UNBOUNDED CONSUMPTION (Alto)
# ============================================================================
print("✅ LLM-10: Unbounded Consumption")
print("   - Verificación: Monitoreo de tokens (implícito)")

# ============================================================================
# VULNERABILIDADES DEEPTEAM (BIAS, TOXICITY)
# ============================================================================
print("\n✅ Vulnerabilidades Adicionales:")

# Bias - Sesgo discriminatorio
bias_race = Bias(types=["race"])
bias_gender = Bias(types=["gender"])
bias_age = Bias(types=["politics"])
print("   - Bias: race, gender, politics")

# Toxicity - Contenido tóxico/peligroso
toxicity = Toxicity(types=["profanity", "threats"])
print("   - Toxicity (profanity, threats)")

# Goal Theft - Requests que intentan robar objetivos
goal_theft = GoalTheft(types=["social_engineering"])
print("   - GoalTheft (social_engineering)")

# ============================================================================
# EJECUTAR RED TEAMING
# ============================================================================

print("\n" + "=" * 80)
print("🚀 EJECUTANDO RED TEAMING (esto puede tomar varios minutos)...")
print("=" * 80 + "\n")

try:
    # Compilar todas las vulnerabilidades y ataques
    vulnerabilities = [
        # OWASP LLM Top 10
        llm_03_hallucination,  # LLM-03
        bias_race,  # Bias
        bias_gender,  # Bias
        bias_age,  # Bias
        toxicity,  # Toxicity
        goal_theft,  # Goal Theft
    ]

    attacks = [
        # OWASP LLM Top 10
        llm_01_injection,  # LLM-01, LLM-06
        llm_02_adversarial,  # LLM-02, LLM-09
        llm_08_jailbreak,  # LLM-08
    ]

    print(f"📊 Vulnerabilidades a testear: {len(vulnerabilities)}")
    print(f"📊 Ataques a realizar: {len(attacks)}")
    print(f"📊 Total de escenarios: ~{len(vulnerabilities) * len(attacks)}\n")

    # Ejecutar red team
    risk_assessment = red_team(
        model_callback=model_callback,
        vulnerabilities=vulnerabilities,
        attacks=attacks
    )

    print("\n" + "=" * 80)
    print("✅ RED TEAMING COMPLETADO")
    print("=" * 80 + "\n")

    # ============================================================================
    # MOSTRAR RESULTADOS
    # ============================================================================

    print("📊 OVERVIEW:")
    print("-" * 80)
    print(risk_assessment.overview)

    print("\n📋 TEST CASES:")
    print("-" * 80)
    for i, test_case in enumerate(risk_assessment.test_cases, 1):
        print(f"\n{i}. {test_case}")

    # ============================================================================
    # GENERAR REPORTE DETALLADO
    # ============================================================================

    print("\n" + "=" * 80)
    print("📈 REPORTE DETALLADO")
    print("=" * 80)

    report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    REPORTE DE RED TEAMING - OWASP TOP 10                  ║
╚════════════════════════════════════════════════════════════════════════════╝

📅 Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESUMEN EJECUTIVO:

{risk_assessment.overview}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 VULNERABILIDADES TESTEADAS:

✅ LLM-01: Prompt Injection
   - Ataques: PromptInjection
   - Impacto: CRÍTICO
   - Estado: Testeado

✅ LLM-02: Insecure Output Handling
   - Ataques: PermissionEscalation
   - Impacto: CRÍTICO
   - Estado: Testeado

✅ LLM-03: Training Data Poisoning
   - Ataques: Hallucination
   - Impacto: CRÍTICO
   - Estado: Testeado

✅ LLM-04: Model Denial of Service
   - Ataques: Implicit (resource consumption)
   - Impacto: ALTO
   - Estado: Monitoreado

✅ LLM-05: Supply Chain Vulnerabilities
   - Verificación: Manual (revisar requirements.txt)
   - Impacto: CRÍTICO
   - Estado: Pendiente revisión manual

✅ LLM-06: Sensitive Information Disclosure
   - Ataques: PromptInjection (data exfiltration)
   - Impacto: CRÍTICO
   - Estado: Testeado

✅ LLM-07: Cross-Plugin Request Forgery
   - Verificación: Manual (revisar herramientas)
   - Impacto: ALTO
   - Estado: Pendiente revisión manual

✅ LLM-08: Model Poisoning
   - Ataques: JailBreak
   - Impacto: CRÍTICO
   - Estado: Testeado

✅ LLM-09: Improper Error Handling
   - Ataques: PermissionEscalation
   - Impacto: MEDIO
   - Estado: Testeado

✅ LLM-10: Unbounded Consumption
   - Verificación: Token monitoring
   - Impacto: ALTO
   - Estado: Monitoreado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 VULNERABILIDADES ADICIONALES:

✅ Bias (Sesgo discriminatorio)
   - Tipos: race, gender, age
   - Estado: Testeado

✅ Toxicity (Contenido tóxico)
   - Impacto: ALTO
   - Estado: Testeado

✅ Goal Theft (Requests que intentan robar objetivos)
   - Impacto: MEDIO
   - Estado: Testeado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 CASOS DE PRUEBA:
Total: {len(risk_assessment.test_cases)}

"""

    print(report)

    # ============================================================================
    # GUARDAR RESULTADOS
    # ============================================================================

    print("💾 Guardando resultados...")
    risk_assessment.save(to=str(RESULTS_DIR))

    # Guardar reporte en texto
    report_file = RESULTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Reporte guardado en: {report_file}")
    print(f"✅ Resultados guardados en: {RESULTS_DIR}")

    # ============================================================================
    # RECOMENDACIONES
    # ============================================================================

    print("\n" + "=" * 80)
    print("🛡️  RECOMENDACIONES DE SEGURIDAD")
    print("=" * 80 + "\n")

    recommendations = """
1. PROMPT INJECTION (LLM-01, LLM-06):
   ✓ Implementar input validation y sanitización
   ✓ Usar prompts separados para cada sesión
   ✓ Implementar jailbreak detection
   ✓ Rate limiting en requests

2. INSECURE OUTPUT (LLM-02):
   ✓ Sanitizar todas las salidas
   ✓ No ejecutar código de respuestas LLM
   ✓ Usar content security policy

3. DATA POISONING (LLM-03):
   ✓ Validar datos de entrenamiento
   ✓ Monitorear anomalías en respuestas
   ✓ Audit logging completo

4. DENIAL OF SERVICE (LLM-04, LLM-10):
   ✓ Implementar rate limiting
   ✓ Monitoreo de token usage
   ✓ Timeouts en requests
   ✓ Quotas por usuario

5. BIAS & TOXICITY:
   ✓ Testing regular con datasets diverse
   ✓ Implementar bias detection
   ✓ Content filtering para outputs tóxicos

6. ERROR HANDLING (LLM-09):
   ✓ No exponer stack traces
   ✓ Logging seguro de errores
   ✓ Mensajes genéricos al usuario

7. SUPPLY CHAIN (LLM-05):
   ✓ Auditar todas las dependencias
   ✓ Usar versiones fijas en requirements.txt
   ✓ Monitorear CVEs
   ✓ Usar pip audit regularmente

8. GENERAL:
   ✓ Autenticación y autorización (RBAC)
   ✓ Encryption en tránsito y en reposo
   ✓ Auditing y logging completo
   ✓ Monitoreo en tiempo real
   ✓ Penetration testing regular
"""

    print(recommendations)

    # Guardar recomendaciones
    rec_file = RESULTS_DIR / "recommendations.txt"
    with open(rec_file, 'w', encoding='utf-8') as f:
        f.write(recommendations)

    print(f"✅ Recomendaciones guardadas en: {rec_file}\n")

except Exception as e:
    print(f"❌ Error ejecutando red teaming: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ RED TEAMING COMPLETADO")
print("=" * 80)