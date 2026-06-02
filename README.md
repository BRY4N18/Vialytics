# SGA — Sistema de Gestión de Accidentes

Plataforma web para la gestión operativa y analítica del ciclo de vida completo de accidentes viales, con visualización geoespacial en tiempo real, despacho de emergencias y dashboard de KPIs.

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Frontend | Angular (standalone) | 21.x |
| UI | CSS plano (sin Tailwind), Leaflet 1.9.4 + MarkerCluster 1.5.3 (CDN) | — |
| Backend | Django + Django REST Framework | 5.x |
| Base de datos operacional | Apache Pinot (vía Kafka) | — |
| Mensajería | Kafka | — |
| Autenticación | JWT (djangorestframework-simplejwt) | — |
| Entorno | Python venv (backend) | 3.x |

---

## Estructura del Proyecto

```
/
├── frontend/                          # Angular standalone SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/                  # Servicios, modelos, interceptors, guards
│   │   │   ├── features/              # Páginas por rol (operador/, admin/)
│   │   │   └── shared/                # Componentes reutilizables
│   │   ├── assets/
│   │   └── types/                     # Declaraciones .d.ts (Leaflet)
│   └── package.json
├── backend/                           # Django REST API
│   ├── accidentes/                    # App Django principal
│   │   ├── PKG1_Gestion_Accidentes/   # 7 CUs (registro, mapa, estado, despacho, severidad, kpi)
│   │   │   ├── CU01_Registrar_Accidente/
│   │   │   ├── CU02_Visualizar_Mapa/
│   │   │   ├── CU03_Actualizar_Estado/
│   │   │   ├── CU04_Despachar_Emergencias/
│   │   │   ├── CU05_Archivar_Accidente/   # (vacío)
│   │   │   ├── CU06_Asignar_Severidad/
│   │   │   └── CU20_Dashboard_KPIs/
│   │   ├── PKG2_Respuesta_Emergencias/    # 3 CUs (despacho, unidades)
│   │   │   ├── CU07_Recibir_Despacho/     # (vacío)
│   │   │   ├── CU08_Actualizar_Estado_Unidad/
│   │   │   └── CU09_Gestionar_Retiro_Vehicular/  # (vacío)
│   │   ├── PKG3_Consulta_Analisis/        # 5 CUs (búsqueda, informes, expediente)
│   │   │   ├── CU10_Buscar_Accidentes/
│   │   │   ├── CU11_Generar_Informes/
│   │   │   ├── CU12_Exportar_Datos/       # (vacío)
│   │   │   ├── CU13_Visualizar_Mapa_Calor/# (vacío)
│   │   │   └── CU14_Solicitar_Expediente/
│   │   ├── PKG4_Portal_Externo/           # 2 CUs (mapa público, estadísticas)
│   │   │   ├── CU15_Consultar_Mapa_Publico/
│   │   │   └── CU16_Consultar_Estadisticas/
│   │   ├── PKG5_Administracion/           # 4 CUs (usuarios, roles, auditoría, login)
│   │   │   ├── CU17_Gestionar_Usuarios/   # (vacío)
│   │   │   ├── CU18_Gestionar_Roles/      # (vacío)
│   │   │   ├── CU19_Auditar_Accesos/      # (vacío)
│   │   │   └── CU21_Iniciar_Sesion/
│   │   ├── shared/                        # Código compartido entre PKGs
│   │   │   ├── models/                    # Dimensiones, hecho, operativos, personas, vehículos
│   │   │   ├── admin.py                   # Registro admin para todos los modelos
│   │   │   ├── catalogo_views.py          # Endpoints de catálogos (CRUD list)
│   │   │   ├── catalogo_serializers.py    # Serializers de catálogos
│   │   │   ├── repositories.py           # PinotRepository, KafkaRepository
│   │   │   ├── kafka_producer.py          # Productor Kafka genérico
│   │   │   └── permissions.py             # Permisos personalizados
│   │   ├── models/__init__.py             # Re-exporta desde shared/models
│   │   ├── migrations/                    # Migraciones Django
│   │   ├── management/commands/           # seed_auth_users, seed_data
│   │   ├── urls.py                        # Enrutador principal de la app
│   │   └── apps.py                        # Config App (AccidentesConfig)
│   └── core/                              # settings.py, urls.py globales
├── database/                              # Scripts SQL, schemas
├── uml/                                   # Diagramas
├── docker-compose.yml                     # Infraestructura (Kafka, Pinot, ZK)
└── SGA(...).md                            # SRS — Especificación de Requerimientos
```

---

## Cómo ejecutar

### Backend

```bash
cd backend
# Activar venv (Windows)
.\venv\Scripts\Activate.ps1
# Activar venv (Linux/Mac)
source venv/bin/activate

python manage.py migrate
python manage.py seed_data          # Seed completo de datos en Kafka/Pinot
python manage.py seed_auth_users    # Crear 4 usuarios JWT
python manage.py runserver
```

El backend corre en `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
ng serve
```

El frontend corre en `http://localhost:4200`.

---

## Usuarios JWT (seed)

| Usuario | Rol | Contraseña |
|---------|-----|-----------|
| `operador_sga` | Operador | `sga_secure_pwd_2026` |
| `admin_sga` | Administrador | `sga_secure_pwd_2026` |
| `supervisor_sga` | Supervisor | `sga_secure_pwd_2026` |
| `despachador_sga` | Despachador | `sga_secure_pwd_2026` |

Endpoint de login: `POST /api/v1/auth/login/` con JSON `{ "usuario": "...", "password": "..." }`.

---

## Estado de Implementación por PKG

### PKG-1 — Gestión de Accidentes ✅ (6/7 CUs)

| CU | Nombre | Estado | Archivos |
|----|--------|--------|----------|
| CU-01 | Registrar Accidente | ✅ | views, services, serializers |
| CU-02 | Visualizar Mapa Tiempo Real | ✅ | views, services |
| CU-03 | Actualizar Estado | ✅ | views, services, serializers |
| CU-04 | Despachar Emergencias | ✅ | views, services, serializers |
| CU-05 | Archivar Accidente | ⬜ Pendiente | — |
| CU-06 | Asignar Severidad | ✅ | services |
| CU-20 | Dashboard KPIs | ✅ | views, services |

### PKG-2 — Respuesta a Emergencias ✅ (1/3 CUs)

| CU | Nombre | Estado | Archivos |
|----|--------|--------|----------|
| CU-07 | Recibir Despacho | ⬜ Pendiente | — |
| CU-08 | Actualizar Estado Unidad | ✅ | views, services, serializers |
| CU-09 | Gestionar Retiro Vehicular | ⬜ Pendiente | — |

### PKG-3 — Consulta y Análisis ✅ (3/5 CUs)

| CU | Nombre | Estado | Archivos |
|----|--------|--------|----------|
| CU-10 | Buscar Accidentes Históricos | ✅ | views, services |
| CU-11 | Generar Informes Estadísticos | ✅ | services |
| CU-12 | Exportar Datos (CSV, PDF) | ⬜ Pendiente | — |
| CU-13 | Visualizar Mapa de Calor | ⬜ Pendiente | — |
| CU-14 | Solicitar Expediente Oficial | ✅ | views, services |

### PKG-4 — Portal Externo ✅ (2/2 CUs)

| CU | Nombre | Estado | Archivos |
|----|--------|--------|----------|
| CU-15 | Consultar Mapa Público | ✅ | views (reusa MapaService de CU-02) |
| CU-16 | Consultar Estadísticas Públicas | ✅ | views (reusa DashboardService de CU-20) |

### PKG-5 — Administración del Sistema ✅ (1/4 CUs)

| CU | Nombre | Estado | Archivos |
|----|--------|--------|----------|
| CU-17 | Gestionar Usuarios | ⬜ Pendiente | — |
| CU-18 | Gestionar Roles y Permisos | ⬜ Pendiente | — |
| CU-19 | Auditar Accesos | ⬜ Pendiente | — |
| CU-21 | Iniciar Sesión (JWT) | ✅ | views |

**Total: 12/21 CUs implementados** · 9 pendientes

---

## Convenciones y Decisiones de Arquitectura

### Frontend
- **Componentes standalone** (no NgModules).
- **Signals** para estado reactivo (no RxJS BehaviorSubject para estado local).
- **CSS plano con variables CSS** — paleta oscura táctica con colores desaturados. No usar Tailwind ni librerías UI externas.
- **Leaflet vía CDN** (no npm). Tipos declarados en `src/types/leaflet.d.ts`. MarkerCluster añadido vía CDN (`leaflet.markercluster` 1.5.3) con severidad por colores en iconos de cluster.
- **Marcadores SVG personalizados** — pines con gradiente cromático por severidad (sin números), animación de pulso para accidentes activos, efecto hover (escala + glow). Popups rediseñados con cabecera degradada, badge de severidad y estadísticas SVG inline.
- **Estilo Double-Bezel** en cards: `border-radius: 10px`, transiciones `cubic-bezier(0.16, 1, 0.3, 1)` 200ms.
- **Interceptor HTTP** para JWT (`auth.interceptor.ts`) y manejo de errores (`error.interceptor.ts`).
- **Rutas públicas**: `/mapa` (AllowAny). **Rutas protegidas**: `/dashboard`, `/lista`, `/registro` (requieren auth. guard).

### Backend
- **DRF con JWTAuthentication + IsAuthenticated** por defecto. Vistas públicas (catálogos, mapa público, estadísticas) tienen `permission_classes = [AllowAny]`.
- **Organización por PKGs del SRS**: Cada paquete funcional (`PKG1` – `PKG5`) agrupa sus Casos de Uso como submódulos independientes. Cada CU contiene `views.py`, `services.py` y opcionalmente `serializers.py`.
- **Código compartido en `shared/`**: modelos, repositorios (Pinot, Kafka), catálogos, admin, permisos. Todos los modelos usan `app_label = 'accidentes'` para mantener compatibilidad con migraciones.
- **Vistas DRF puras** (no ViewSets) para control fino.
- **JWT sin refresh token** configurado; el frontend persiste el token en `localStorage`.
- **Base de datos**: Apache Pinot (OLAP) vía queries SQL directas. Kafka como bus de eventos para ingestion en tiempo real. No se usa PostgreSQL/MySQL como almacenamiento primario.

---

## Errores Conocidos y Cómo Evitarlos

### 1. Mismatch de valores de estado (frontend ↔ backend)
**Error**: El listado muestra `ACTIVO` en vez de `Reportado`, y los filtros no funcionan.

**Causa**: El backend seedea los estados como `ACTIVO`, `EN_ATENCION`, `CONTROLADO`, `ARCHIVADO`. El frontend debe usar EXACTAMENTE esos valores en el array `estados[]` de `lista-accidentes.ts`.

**Solución**: Mapa de estados en `lista-accidentes.ts:62`:
```typescript
readonly estados = [
  { value: 'ACTIVO', label: 'Reportado', ... },
  { value: 'EN_ATENCION', label: 'En Atención', ... },
  { value: 'CONTROLADO', label: 'Despejado', ... },
  { value: 'ARCHIVADO', label: 'Archivado', ... }
];
```

### 2. `idelementofisico_id` hardcodeado en registro
**Error**: Al registrar un accidente, el campo `idelementofisico_id` siempre se enviaba como `1`.

**Causa**: El método `buildPayload()` usaba `idelementofisico_id: 1` en vez de mapear los checkboxes.

**Solución**: `matchElementoFisicoId()` en `registro-accidente.ts:522` que busca en el catálogo `elementosFisicos` la combinación exacta de checkboxes seleccionados.

### 3. `idestadoclima_id` hardcodeado
**Error**: Similar al anterior, se enviaba `idestadoclima_id: 1`.

**Causa**: Frontend hardcodeaba 1, backend usaba `=` en vez de `LIKE` para matchear nombres bilingües (el catálogo puede tener "Soleado" o "Sunny").

**Solución**: Backend usa `LIKE '%{cond_escaped}%'` y frontend usa el valor seleccionado del dropdown de clima.

### 4. Comboboxes de ubicación no se llenan al editar
**Error**: Al editar un accidente, los comboboxes de país/estado/ciudad/calle no se seleccionan automáticamente.

**Causa**: El método `poblarCascadaConIds()` fallaba cuando los IDs numéricos no coincidían exactamente con los valores de los arrays de opciones, y no tenía fallback por nombre.

**Solución**: Agregar fallback por nombre de calle/ciudad, tolerar ID=0, validación con función `pid()`.

### 5. Estados duplicados en seed data
**Nota**: Los seed data de `tiposestadosincidentes` tienen 5 registros, pero IDs 2 y 3 tienen nombres distintos (`EN_ATENCION` vs `EN_TRASLADO`). El mapeo en el servicio trata ambos como `EN_ATENCION`. Si se agregan nuevos estados, actualizar TAMBIÉN el `estados_catalogo` en `accidente_service.py` y el array `estados[]` en `lista-accidentes.ts`.

### 6. `idusuario_id` hardcodeado
Al crear/actualizar accidentes y estados, `idusuario_id` se envía como `1`. No se usa el usuario autenticado del JWT. Pendiente de corregir.

### 7. Tipos de TypeScript para MarkerCluster no declarados
**Error**: `L.markerClusterGroup` da error de tipo en compilación (`Property 'markerClusterGroup' does not exist on type 'typeof L'`).

**Causa**: `leaflet.markercluster` no tiene tipos nativos. Solo se declararon tipos mínimos en `leaflet.d.ts`.

**Solución**: Ya declarado en `src/types/leaflet.d.ts`. Si se actualiza la librería, verificar que los tipos sigan siendo compatibles con la sintaxis `L.markerClusterGroup()`.

### 8. Dashboard lento por múltiples queries secuenciales a Pinot
**Error**: El dashboard tarda varios segundos en cargar porque ejecuta 7 queries secuenciales a Pinot.

**Causa**: Cada llamada a `PinotRepository.execute_query()` es una request HTTP síncrona. 6 queries con JOINs usan multi-stage engine, que es más lento.

**Solución implementada**: 
- Caché en memoria con Django `LocMemCache` (TTL 60s) — la primera carga puede tardar, las siguientes son instantáneas.
- KPIs combinados en una sola query (antes eran 2 separadas).
- Timeout reducido de 15s a 5s para fallar rápido si Pinot no responde.

---

## Flujo de Autenticación

1. Usuario ingresa credenciales en `LoginModalComponent`.
2. `AuthService.login()` envía POST a `/api/v1/auth/login/`.
3. Backend valida contra `django.contrib.auth.models.User` y devuelve JWT + refresh token.
4. Frontend guarda access token, refresh token y username en `localStorage`.
5. `auth.interceptor.ts` adjunta `Authorization: Bearer <token>` a cada request HTTP.
6. Si el servidor responde 401, el interceptor intenta renovar el token via `POST /auth/refresh/` con el refresh token guardado.
7. Si el refresh es exitoso, se re-intenta la request original con el nuevo token.
8. Si el refresh falla, se limpia la sesión y redirige a `/mapa`.
9. `auth.guard.ts` protege rutas redirigiendo a `/mapa` si no hay sesión.
10. `AuthService.restoreSession()` en el constructor restaura sesión desde `localStorage` al recargar la página.

---

## Flujo de Estado de Accidente

```
Reportado (ACTIVO) → En Atención (EN_ATENCION) → Despejado (CONTROLADO) → Archivado (ARCHIVADO)
```

- Cada transición crea un registro en `accidentestiposestadosincidentes_topic` (Kafka → Pinot).
- El estado actual se resuelve consultando el registro con `MAX(fechahoramodificado)` por accidente.
- El listado y detalle usan `estado_actual` resuelto en backend (nunca hardcodeado).

---

## API Endpoints

> Todos los endpoints están prefijados con `/api/v1/`. Ej: `/api/v1/public/mapa/`.

### Portal Público (PKG-4, AllowAny)

| Endpoint | CU | Descripción |
|----------|----|-------------|
| `GET /api/v1/public/mapa/` | CU-15 | Mapa de accidentes (sin datos sensibles) |
| `GET /api/v1/public/estadisticas/` | CU-16 | Dashboard de KPIs público |

### Autenticación (PKG-5)

| Endpoint | CU | Descripción |
|----------|----|-------------|
| `POST /api/v1/auth/login/` | CU-21 | Login JWT |
| `POST /api/v1/auth/refresh/` | CU-21 | Renovar JWT |
| `GET /api/v1/auth/verify/` | CU-21 | Verificar token vigente |

### Gestión de Accidentes (PKG-1, autenticado)

| Endpoint | CU | Descripción |
|----------|----|-------------|
| `GET /api/v1/accidentes/dashboard/` | CU-20 | KPIs y estadísticas |
| `POST /api/v1/accidentes/` | CU-01 | Registrar nuevo accidente |
| `PUT /api/v1/accidentes/<id>/` | CU-01 | Actualizar accidente |
| `GET /api/v1/accidentes/mapa/` | CU-02 | Mapa operativo (datos completos) |
| `PATCH /api/v1/accidentes/<id>/estado/` | CU-03 | Cambiar estado del accidente |
| `GET/POST /api/v1/accidentes/<id>/despachos/` | CU-04 | Despachar unidades de emergencia |
| `GET /api/v1/accidentes/<id>/` | CU-14 | Detalle completo del accidente |
| `GET /api/v1/accidentes/<id>/expediente/` | CU-14 | Expediente oficial |
| `GET /api/v1/accidentes/buscar/` | CU-10 | Búsqueda paginada con filtros |

### Respuesta a Emergencias (PKG-2, autenticado)

| Endpoint | CU | Descripción |
|----------|----|-------------|
| `GET /api/v1/unidades/` | CU-08 | Listar unidades de emergencia |
| `PATCH /api/v1/unidades/<id>/estado/` | CU-08 | Actualizar estado de unidad |

### Catálogos (AllowAny)

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/v1/tipos-reportado/` | Tipos de reporte |
| `GET /api/v1/severidades/` | Niveles de severidad |
| `GET /api/v1/tipos-estado/` | Estados del incidente |
| `GET /api/v1/paises/` | Países |
| `GET /api/v1/estados/` | Estados/provincias |
| `GET /api/v1/condados/` | Condados |
| `GET /api/v1/ciudades/` | Ciudades |
| `GET /api/v1/calles/` | Calles |
| `GET /api/v1/climas/` | Estados climáticos |
| `GET /api/v1/elementos-fisicos/` | Elementos físicos de la vía |
| `GET /api/v1/periodos-dias/` | Períodos del día |

---

## Comandos Útiles

```bash
# Re-seedear datos de prueba
python manage.py seed_data

# Re-seedear usuarios JWT
python manage.py seed_auth_users

# Build frontend
cd frontend && npx ng build

# Verificar sintaxis Python (en todos los .py del backend)
python -m py_compile manage.py
python -c "import py_compile; import os; [py_compile.compile(os.path.join(r, f)) for r, d, fs in os.walk('accidentes') for f in fs if f.endswith('.py') and r.count(os.sep) < 8]"
```
