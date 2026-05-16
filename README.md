# 🎫 Ticket Triage Autopilot

Sistema inteligente de triage automático para tickets de soporte al cliente en español (Argentina/Uruguay). Utiliza OpenAI GPT-4o-mini para categorizar, priorizar y sugerir respuestas iniciales en tickets de soporte, optimizado para equipos hispanohablantes.

## 🎯 ¿Qué Hace?

Convierte esto:

```
"Me cobraron dos veces el mes pasado. Quiero el reembolso YA."
```

En esto:

```json
{
  "categoria": "facturacion",
  "subcategoria": "cargo_duplicado",
  "prioridad": "critica",
  "respuesta_inicial": "Tenés toda la razón en estar enojado. Este fue un error nuestro...",
  "confianza": 0.95,
  "tiempo_resolucion_estimado_minutos": 5,
  "equipo_asignado": "equipo_facturacion",
  "sla_minutos": 30,
  "sentimiento_cliente": "enojado",
  "riesgo_fuga": 0.85,
  "acciones": ["procesar_reembolso", "enviar_confirmacion", "monitorear_cuenta"]
}
```

## ✨ Características

- ✅ **Categorización automática**: issue_tecnico, facturacion, cuenta, cancelacion, consulta_funcionalidad, otro
- ✅ **Priorización inteligente**: baja → media → alta → crítica
- ✅ **Respuestas empáticas** en español rioplatense (vos, podés, etc.)
- ✅ **Detección de riesgo de fuga**: 0.0 - 1.0 (cliente satisfecho → cliente furioso)
- ✅ **Routing automático**: asigna al equipo correcto (soporte_tier1, equipo_tecnico, escalacion_ejecutiva)
- ✅ **Seguridad por patrones**: detecta tarjetas de crédito, SSN, CUIT/CUIL, prompt injection, lenguaje abusivo
- ✅ **Métricas detalladas**: tokens, latencia, costo por ticket
- ✅ **Few-shot learning**: 5 ejemplos anotados guían el comportamiento del modelo

## 🏗️ Arquitectura (Clean Architecture + DDD)

```
src/
├── domain/                      # Lógica de negocio pura (sin dependencias)
│   ├── entities/                # Value objects (Ticket, TriageResult, TriageMetrics)
│   └── interfaces/              # Abstracciones (ILLMService, ISafetyChecker, IMetricsRepository)
├── application/                 # Casos de uso (orquestación)
│   ├── triage_ticket_use_case.py        # Flujo: safety → LLM → metrics
│   └── get_metrics_summary_use_case.py  # Consulta de estadísticas
├── infrastructure/              # Implementaciones concretas
│   ├── llm/                     # Adaptador OpenAI
│   ├── safety/                  # Checker basado en regex
│   ├── repositories/            # Persistencia JSON
│   └── prompts/                 # Carga de prompts/ejemplos
├── core/                        # Configuración + Dependency Injection
│   ├── config.py                # Settings (pydantic-settings)
│   └── dependencies.py          # Factory functions (@lru_cache)
└── api/                         # Puntos de entrada
    └── cli.py                   # CLI con argparse
```

### Principios Aplicados

| Principio | Implementación |
|-----------|----------------|
| **SRP** | Cada clase tiene 1 responsabilidad (OpenAILLMService solo habla con OpenAI) |
| **DIP** | Use cases dependen de interfaces (ABC), no de implementaciones |
| **OCP** | Extendible sin modificar código existente (nuevo LLM provider → implementar ILLMService) |
| **Repository Pattern** | Abstracción de persistencia (JSON hoy, PostgreSQL mañana sin cambiar use cases) |
| **Dependency Injection** | Todas las dependencias inyectadas vía factory functions |

## 🚀 Setup

### 1. Requisitos

- Python 3.10+
- OpenAI API Key

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env` en la raíz:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=500
PROMPTS_DIR=prompts
METRICS_FILE=metrics/metrics.json
LOG_LEVEL=INFO
```

### 4. Ejecutar tests

```bash
pytest tests/ -v
```

## 📖 Uso

### Modo CLI (salida con emojis y formato legible)

```bash
python -m src.api.cli "No puedo acceder a mi cuenta, me dice error 403"
```

Salida:

```
📂 Categoría: cuenta (autenticacion)
🚨 Prioridad: alta
👥 Equipo: soporte_tier1
⏱️ SLA: 30 minutos

😊 Respuesta inicial:
Entendemos lo frustrante que es esto. Vamos a resetear tu contraseña...

⚠️ Riesgo de fuga: 0.6
✅ Confianza: 0.92

📋 Acciones:
  • enviar_link_reset_password
  • monitorear_seguimiento

📊 Métricas:
  • Tokens: 100 (entrada) + 50 (salida) = 150 total
  • Latencia: 250 ms
  • Costo: $0.0001
```

### Modo JSON (para integración con sistemas)

```bash
python -m src.api.cli "Me cobraron dos veces" --json
```

Salida:

```json
{
  "ticket_id": "auto-generated-uuid",
  "categoria": "facturacion",
  "subcategoria": "cargo_duplicado",
  "prioridad": "critica",
  ...
}
```

### Ver resumen de métricas

```bash
python -m src.api.cli --resumen
```

Salida:

```
📊 RESUMEN DE MÉTRICAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Total de tickets procesados: 42
⏱️  Latencia promedio: 245 ms
💰 Costo total: $0.0052
🔒 Tickets bloqueados (seguridad): 3
```

## 🔒 Seguridad

El sistema aplica 3 capas de validación ANTES de enviar a OpenAI:

1. **Datos sensibles**: Tarjetas de crédito (Visa, MC, Amex), SSN, CUIT/CUIL argentinos
2. **Prompt injection**: Detecta intentos de manipular el prompt (en español e inglés)
3. **Lenguaje abusivo**: Keywords ofensivos en español e inglés

Si el ticket es bloqueado, devuelve una respuesta de fallback segura y NO consume tokens.

## 💰 Costos

Modelo: **gpt-4o-mini**

- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

**Ejemplo real:**

- Ticket: "No puedo acceder a mi cuenta" (10 palabras)
- Tokens entrada: ~100 (system prompt + few-shot + mensaje)
- Tokens salida: ~50 (JSON estructurado)
- Costo por ticket: **$0.0001** (0.01 centavos de dólar)

**Proyección:**

- 1,000 tickets/día = **$0.10/día** = **$3/mes**
- 10,000 tickets/día = **$1/día** = **$30/mes**

## 📊 Métricas Recopiladas

Cada triage guarda en `metrics/metrics.json`:

```json
{
  "ticket_id": "T123",
  "timestamp": "2025-01-15T10:30:00",
  "tokens_prompt": 100,
  "tokens_completion": 50,
  "tokens_total": 150,
  "latencia_ms": 245,
  "costo_usd": 0.0001
}
```

## 🧪 Tests

```bash
# Correr todos los tests
pytest tests/ -v

# Solo tests de dominio
pytest tests/unit/domain/ -v

# Solo tests de infrastructure
pytest tests/unit/infrastructure/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

Tests incluidos:

- ✅ Domain: validaciones de entidades (Ticket, TriageResult)
- ✅ Infrastructure: PatternSafetyChecker (detección de CC, SSN, injection, abuse)
- ✅ Application: TriageTicketUseCase (flujo completo con mocks)

## 🌍 Contexto Regional

El sistema está optimizado para **español rioplatense** (Argentina/Uruguay):

- Usa "vos" en lugar de "tú"
- Verbos conjugados correctamente: "podés", "tenés", "querés"
- Tono directo pero cordial, evita formalidad excesiva
- Detecta CUIT/CUIL (identificadores argentinos)

## 🔧 Troubleshooting

### Error: "OpenAI API key not found"

→ Verificá que `.env` esté en la raíz y contenga `OPENAI_API_KEY=sk-...`

### Error: "FileNotFoundError: prompts/system_prompt.txt"

→ Asegurate que la carpeta `prompts/` existe con `system_prompt.txt` y `few_shot_examples.json`

## 📄 Licencia

MIT

---

*Ticket Triage Autopilot: Automatización inteligente de soporte al cliente en español* 🚀
