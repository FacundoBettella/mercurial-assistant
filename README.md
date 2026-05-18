# 🤖 Ticket Triage Autopilot

Sistema inteligente de triage automático para tickets de soporte al cliente en español rioplatense (Argentina/Uruguay). Utiliza OpenAI GPT-4o-mini para analizar, priorizar y sugerir respuestas iniciales, devolviendo siempre un JSON estructurado y registrando métricas de cada consulta.

## ¿Qué hace?

Convierte esto:

```
"Me cobraron dos veces este mes, necesito una solución urgente."
```

en esto:

```json
{
  "answer": "Lamentamos mucho el inconveniente con la facturación. Tu caso fue clasificado como crítico y será gestionado con máxima prioridad.",
  "confidence": 0.98,
  "actions": ["Encolar ticket como crítico", "Notificar a equipo de facturación"],
  "priority": "critical",
  "churn_risk": 0.9
}
```

## Características

- Clasificación automática de prioridad y riesgo de fuga
- Respuestas empáticas en español rioplatense (vos, podés, tenés)
- Registro de métricas: tokens, latencia, costo estimado por consulta
- Prompt engineering: few-shot y chain-of-thought
- Moderación de contenido adversarial (fallback seguro):
  - **ModerationService** detecta lenguaje riesgoso, intentos de prompt injection, amenazas o datos sensibles, y bloquea o anonimiza según reglas de negocio.
  - **LogRepository** registra todos los eventos de moderación en un archivo JSONL para trazabilidad y auditoría.
- Arquitectura Clean Architecture

## Estructura

```
src/
├── domain/           # Lógica de negocio pura (interfaces, servicios)
├── application/      # Casos de uso y orquestación
├── infrastructure/   # Adaptadores (OpenAI, persistencia, métricas)
├── core/             # Configuración y DI
├── api/              # Endpoints FastAPI
├── prompts/          # main_prompt.txt (instrucciones y ejemplos)
├── logs/             # moderation_events.jsonl (eventos de moderación, trazabilidad)
├── metrics/          # metrics.csv (registro de métricas de cada request)
```

## Variables de entorno

- `OPENAI_API_KEY` — API key de OpenAI
- `OPENAI_MODEL` — Modelo a usar (por defecto: gpt-4o-mini)
- `LOGS_DIR` — Carpeta para logs generales (por defecto: logs)
- `METRICS_DIR` — Carpeta para métricas (por defecto: metrics)

## Comandos principales

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor FastAPI
uvicorn src.main:app --reload
```

## Cómo ver métricas

Cada request registra métricas en `metrics/metrics.csv`:

- timestamp, prompt, modelo, tokens_prompt, tokens_completion, total_tokens, latency_ms, estimated_cost_usd

## Cómo ver logs de moderación

Todos los eventos de moderación (bloqueos, riesgos detectados, etc.) se registran en `logs/moderation_events.jsonl`. Cada línea es un JSON con el detalle del evento para trazabilidad y auditoría.

## Prompt principal

El prompt principal usado por el modelo está en `prompts/main_prompt.txt`. Allí se definen las instrucciones, el formato de salida y los ejemplos few-shot.

## Cómo probar la app

1. Levantá el servidor con `uvicorn src.main:app --reload`.
2. Accedé a la documentación interactiva en [http://localhost:8080/docs](http://localhost:8080/docs) para probar los endpoints y enviar consultas manualmente.

## Limitaciones

- El sistema no resuelve tickets, solo los clasifica y encola según urgencia.
- El costo es estimado según precios públicos de OpenAI.
- El modelo puede fallar ante entradas muy adversariales, pero existe fallback seguro.

## 🔒 Seguridad

El sistema aplica 3 capas de validación ANTES de enviar a OpenAI:

- **Datos sensibles:** Detecta tarjetas de crédito (Visa, MC, Amex), SSN, CUIT/CUIL argentinos
- **Prompt injection:** Detecta intentos de manipular el prompt (en español e inglés)
- **Lenguaje abusivo:** Keywords ofensivos en español e inglés

Si el ticket es bloqueado, devuelve una respuesta de fallback segura y NO consume tokens.
