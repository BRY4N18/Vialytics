# SGA — Sistema de Gestión de Accidentes

Plataforma web para la gestión operativa y analítica del ciclo de vida completo de accidentes viales, con visualización geoespacial en tiempo real, despacho de emergencias y dashboard de KPIs.

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Frontend | Angular (standalone) | 21.x |
| UI | Tailwind CSS 3 + CSS plano, Leaflet 1.9.4 + MarkerCluster 1.5.3 (CDN) | — |
| Backend | Django + Django REST Framework | 6.x |
| Base de datos operacional | Apache Pinot (vía Kafka) | — |
| Mensajería | Kafka | — |
| Autenticación | JWT (djangorestframework-simplejwt) | — |
| Gráficos | Chart.js | 4.5.1 |
| Entorno | Python venv (backend) | 3.x |

---

## Estructura del Proyecto

```
/
├── frontend/                              # Angular 21 standalone SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.ts / app.html          # Root component
│   │   │   ├── app.routes.ts              # 14 rutas (públicas, protegidas, analista)
│   │   │   ├── app.config.ts              # Providers globales
│   │   │   ├── core/                      # Capa transversal
│   │   │   │   ├── guards/
│   │   │   │   │   ├── auth.guard.ts
│   │   │   │   │   └── analista.guard.ts
│   │   │   │   ├── interceptors/
│   │   │   │   │   ├── auth.interceptor.ts
│   │   │   │   │   └── error.interceptor.ts
│   │   │   │   ├── models/
│   │   │   │   │   ├── accidente.model.ts
│   │   │   │   │   ├── despacho.model.ts
│   │   │   │   │   ├── despacho-pendiente.model.ts
│   │   │   │   │   └── unidad-emergencia.model.ts
│   │   │   │   └── services/
│   │   │   │       ├── accidente.service.ts
│   │   │   │       ├── auth.service.ts
│   │   │   │       ├── despacho.service.ts
│   │   │   │       ├── mapa.service.ts
│   │   │   │       ├── toast.service.ts
│   │   │   │       └── unidad-emergencia.service.ts
│   │   │   ├── features/                  # Organizado por PKGs (espejo del backend)
│   │   │   │   ├── PKG1_Gestion_Accidentes/
│   │   │   │   │   ├── CU01_Registrar_Accidente/   # RegistroAccidenteComponent
│   │   │   │   │   ├── CU02_Visualizar_Mapa/       # Mapa, panel, despacho, estado
│   │   │   │   │   ├── CU03_Actualizar_Estado/     # (vacío)
│   │   │   │   │   ├── CU05_Archivar_Accidente/    # (vacío)
│   │   │   │   │   ├── CU06_Asignar_Severidad/     # (vacío)
│   │   │   │   │   └── CU20_Dashboard_KPIs/        # DashboardComponent
│   │   │   │   ├── PKG2_Respuesta_Emergencias/
│   │   │   │   │   ├── CU07_Recibir_Despacho/      # RecibirDespachoComponent
│   │   │   │   │   ├── CU08_Actualizar_Estado_Unidad/ # CambiarEstadoComponent
│   │   │   │   │   ├── CU09_Gestionar_Retiro_Vehicular/ # SolicitarRetiroComponent
│   │   │   │   │   └── CU22_Gestionar_Unidades_Emergencia/ # GestionarUnidadesComponent
│   │   │   │   ├── PKG3_Consulta_Analisis/
│   │   │   │   │   ├── CU10_Buscar_Accidentes/     # 2 vistas: operador + analista
│   │   │   │   │   ├── CU11_Generar_Informes/      # (vacío)
│   │   │   │   │   ├── CU12_Exportar_Datos/        # (vacío)
│   │   │   │   │   ├── CU13_Visualizar_Mapa_Calor/ # (vacío)
│   │   │   │   │   ├── CU14_Solicitar_Expediente/  # ExpedienteComponent
│   │   │   │   │   └── layout-analitico/           # LayoutAnaliticoComponent
│   │   │   │   ├── PKG4_Portal_Externo/
│   │   │   │   │   ├── CU15_Consultar_Mapa_Publico/ # MapaPublicoPageComponent
│   │   │   │   │   └── CU16_Consultar_Estadisticas/ # (vacío)
│   │   │   │   └── PKG5_Administracion/
│   │   │   │       ├── CU17_Gestionar_Usuarios/    # (vacío)
│   │   │   │       ├── CU18_Gestionar_Roles/       # (vacío)
│   │   │   │       ├── CU19_Auditar_Accesos/       # (vacío)
│   │   │   │       └── CU21_Iniciar_Sesion/        # (login en shared)
│   │   │   └── shared/
│   │   │       └── components/
│   │   │           ├── badge-severidad/ # BadgeSeveridadComponent
│   │   │           ├── header/          # HeaderComponent (navbar + login modal)
│   │   │           └── login-modal/     # LoginModalComponent
│   │   ├── assets/
│   │   └── types/                       # leaflet.d.ts (tipos MarkerCluster)
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
│   │   ├── PKG2_Respuesta_Emergencias/    # 4 CUs (despacho, unidades, retiro)
│   │   │   ├── CU07_Recibir_Despacho/
│   │   │   ├── CU08_Actualizar_Estado_Unidad/
│   │   │   ├── CU09_Gestionar_Retiro_Vehicular/
│   │   │   └── CU22_Gestionar_Unidades_Emergencia/
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
│   │   │   ├── catalogo_repositories.py   # Repositorios de catálogos
│   │   │   ├── repositories.py           # PinotRepository, KafkaRepository
│   │   │   ├── permissions.py             # Permisos personalizados
│   │   │   └── utils.py                   # Utilidades compartidas
│   │   ├── models/__init__.py             # Re-exporta desde shared/models
│   │   ├── migrations/                    # Migraciones Django
│   │   ├── management/commands/           # seed_auth_users
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
python manage.py seed_auth_users    # Crear 5 usuarios JWT
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
| `analista_sga` | Consumidor Analítico | `sga_secure_pwd_2026` |
| `despachador_sga` | Despachador | `sga_secure_pwd_2026` |
| `unidad_emergencia_sga` | Unidad de Emergencia | `sga_secure_pwd_2026` |

Endpoint de login: `POST /api/v1/auth/login/` con JSON `{ "usuario": "...", "password": "..." }`.

---

## Estado de Implementación por PKG

### PKG-1 — Gestión de Accidentes ✅ (6/7 CUs)

| CU | Nombre | Estado | Backend | Frontend |
|----|--------|--------|---------|----------|
| CU-01 | Registrar Accidente | ✅ | views, services, repos, serializers | RegistroAccidenteComponent |
| CU-02 | Visualizar Mapa Tiempo Real | ✅ | views, services, repos | MapaPageComponent, MapaComponent, PanelDetalleComponent |
| CU-03 | Actualizar Estado | ✅ | views, services, serializers | ActualizarEstadoComponent |
| CU-04 | Despachar Emergencias | ✅ | views, services, repos, serializers | DespachoComponent |
| CU-05 | Archivar Accidente | ⬜ Pendiente | — | — |
| CU-06 | Asignar Severidad | ✅ | services | — (integrado en registro) |
| CU-20 | Dashboard KPIs | ✅ | views, services, repos | DashboardComponent |

### PKG-2 — Respuesta a Emergencias ✅ (4/4 CUs)

| CU | Nombre | Estado | Backend | Frontend |
|----|--------|--------|---------|----------|
| CU-07 | Recibir Despacho | ✅ | views, services, repos, serializers | RecibirDespachoComponent |
| CU-08 | Actualizar Estado Unidad | ✅ | views, services, repos, serializers | CambiarEstadoComponent |
| CU-09 | Gestionar Retiro Vehicular | ✅ | views, services, repos, serializers | SolicitarRetiroComponent, GestionarRetirosComponent |
| CU-22 | Gestionar Unidades Emergencia | ✅ | views, services, repos, serializers | GestionarUnidadesComponent |

### PKG-3 — Consulta y Análisis ✅ (3/5 CUs)

| CU | Nombre | Estado | Backend | Frontend |
|----|--------|--------|---------|----------|
| CU-10 | Buscar Accidentes Históricos | ✅ | views, services, repos | ListaAccidentesComponent (operador), ListaAccidentesAnaliticoComponent (analista) |
| CU-11 | Generar Informes Estadísticos | ✅ | services, repos | — |
| CU-12 | Exportar Datos (CSV, PDF) | ⬜ Pendiente | — | — |
| CU-13 | Visualizar Mapa de Calor | ⬜ Pendiente | — | — |
| CU-14 | Solicitar Expediente Oficial | ✅ | views, services, repos | ExpedienteComponent |

### PKG-4 — Portal Externo ✅ (2/2 CUs)

| CU | Nombre | Estado | Backend | Frontend |
|----|--------|--------|---------|----------|
| CU-15 | Consultar Mapa Público | ✅ | views (reusa MapaService) | MapaPublicoPageComponent |
| CU-16 | Consultar Estadísticas Públicas | ✅ | views (reusa DashboardService) | — |

### PKG-5 — Administración del Sistema ✅ (1/4 CUs)

| CU | Nombre | Estado | Backend | Frontend |
|----|--------|--------|---------|----------|
| CU-17 | Gestionar Usuarios | ⬜ Pendiente | — | — |
| CU-18 | Gestionar Roles y Permisos | ⬜ Pendiente | — | — |
| CU-19 | Auditar Accesos | ⬜ Pendiente | — | — |
| CU-21 | Iniciar Sesión (JWT) | ✅ | views | LoginModalComponent (integrado en HeaderComponent) |

**Total: 16/22 CUs implementados** · 6 pendientes

---

## Convenciones y Decisiones de Arquitectura

### Frontend
- **Componentes standalone** (no NgModules). Lazy loading con `loadComponent`.
- **Signals** para estado reactivo (no RxJS BehaviorSubject para estado local).
- **Tailwind CSS 3** con PostCSS + Autoprefixer + CSS plano con variables CSS — paleta oscura táctica con colores desaturados.
- **Leaflet vía CDN** (no npm). Tipos declarados en `src/types/leaflet.d.ts`. MarkerCluster añadido vía CDN (`leaflet.markercluster` 1.5.3) con severidad por colores en iconos de cluster.
- **Marcadores SVG personalizados** — pines con gradiente cromático por severidad (sin números), animación de pulso para accidentes activos, efecto hover (escala + glow). Popups rediseñados con cabecera degradada, badge de severidad y estadísticas SVG inline.
- **Chart.js 4.5.1** para gráficos del dashboard (barras, dona, línea temporal).
- **Estilo Double-Bezel** en cards: `border-radius: 10px`, transiciones `cubic-bezier(0.16, 1, 0.3, 1)` 200ms.
- **Interceptor HTTP** para JWT (`auth.interceptor.ts`) y manejo de errores (`error.interceptor.ts`).
- **Guard de autenticación** (`auth.guard.ts`) y **guard de rol analítico** (`analista.guard.ts`).
- **Rutas públicas**: `/mapa`, `/mapa-publico` (AllowAny).
- **Rutas protegidas**: `/dashboard`, `/registro-accidente`, `/accidentes`, `/responder`, `/responder/cambiar-estado`, `/retiros/solicitar`, `/retiros/gestionar`, `/unidades`.
- **Rutas de analista**: `/analitico/accidentes`, `/analitico/expediente/:id` (auth + rol analista).

### Backend
- **DRF con JWTAuthentication + IsAuthenticated** por defecto. Vistas públicas (catálogos, mapa público, estadísticas) tienen `permission_classes = [AllowAny]`.
- **Organización por PKGs del SRS**: Cada paquete funcional (`PKG1` – `PKG5`) agrupa sus Casos de Uso como submódulos independientes. Cada CU contiene `views.py`, `services.py` y opcionalmente `serializers.py`.
- **Código compartido en `shared/`**: modelos, repositorios (Pinot, Kafka), catálogos (views, serializers, repositories), admin, permisos, utilidades. Todos los modelos usan `app_label = 'accidentes'` para mantener compatibilidad con migraciones.
- **Vistas DRF puras** (no ViewSets) para control fino.
- **Tests**: Vitest + jsdom (frontend), unittest (backend).
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

### 2. Comboboxes de ubicación no se llenan al editar
**Error**: Al editar un accidente, los comboboxes de país/estado/ciudad/calle no se seleccionan automáticamente.

**Causa**: El método `poblarCascadaConIds()` fallaba cuando los IDs numéricos no coincidían exactamente con los valores de los arrays de opciones, y no tenía fallback por nombre.

**Solución**: Agregar fallback por nombre de calle/ciudad, tolerar ID=0, validación con función `pid()`.

### 3. Estados duplicados en seed data
**Nota**: Los seed data de `tiposestadosincidentes` tienen 5 registros, pero IDs 2 y 3 tienen nombres distintos (`EN_ATENCION` vs `EN_TRASLADO`). El mapeo en el servicio trata ambos como `EN_ATENCION`. Si se agregan nuevos estados, actualizar TAMBIÉN el `estados_catalogo` en `accidente_service.py` y el array `estados[]` en `lista-accidentes.ts`.

### 4. `idusuario_id` hardcodeado
Al crear/actualizar accidentes y estados, `idusuario_id` se envía como `1`. No se usa el usuario autenticado del JWT. Pendiente de corregir.

### 5. Tipos de TypeScript para MarkerCluster no declarados
**Error**: `L.markerClusterGroup` da error de tipo en compilación (`Property 'markerClusterGroup' does not exist on type 'typeof L'`).

**Causa**: `leaflet.markercluster` no tiene tipos nativos. Solo se declararon tipos mínimos en `leaflet.d.ts`.

**Solución**: Ya declarado en `src/types/leaflet.d.ts`. Si se actualiza la librería, verificar que los tipos sigan siendo compatibles con la sintaxis `L.markerClusterGroup()`.

### 6. Dashboard lento por múltiples queries secuenciales a Pinot
**Error**: El dashboard tarda varios segundos en cargar porque ejecuta 7 queries secuenciales a Pinot.

**Causa**: Cada llamada a `PinotRepository.execute_query()` es una request HTTP síncrona. 6 queries con JOINs usan multi-stage engine, que es más lento.

**Solución implementada**: 
- Caché en memoria con Django `LocMemCache` (TTL 60s) — la primera carga puede tardar, las siguientes son instantáneas.
- KPIs combinados en una sola query (antes eran 2 separadas).
- Timeout reducido de 15s a 5s para fallar rápido si Pinot no responde.

---

## Flujo de Autenticación

1. Usuario ingresa credenciales en `LoginModalComponent` (integrado en `HeaderComponent`).
2. `AuthService.login()` envía POST a `/api/v1/auth/login/`.
3. Backend valida contra `django.contrib.auth.models.User` y devuelve JWT + refresh token.
4. Frontend guarda access token, refresh token, username y rol en `localStorage`.
5. `auth.interceptor.ts` adjunta `Authorization: Bearer <token>` a cada request HTTP.
6. Si el servidor responde 401, el interceptor intenta renovar el token via `POST /api/v1/auth/refresh/` con el refresh token guardado.
7. Si el refresh es exitoso, se re-intenta la request original con el nuevo token.
8. Si el refresh falla, se limpia la sesión y redirige a `/mapa` (público).
9. `auth.guard.ts` protege rutas redirigiendo a `/mapa` si no hay sesión.
10. `analista.guard.ts` restringe rutas analíticas solo al rol `Consumidor Analitico`.
11. `AuthService.restoreSession()` en el constructor restaura sesión desde `localStorage` al recargar la página.

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
| `GET /api/v1/unidades/` | CU-22 | Listar y crear unidades de emergencia |
| `GET /api/v1/unidades/<id>/` | CU-22 | Detalle de unidad |
| `PATCH /api/v1/unidades/<id>/estado/` | CU-08 | Actualizar estado de unidad |
| `PATCH /api/v1/unidades/<id>/activar/` | CU-22 | Activar/desactivar unidad |
| `GET /api/v1/despachos/unidad/<id>/` | CU-07 | Despachos asignados a una unidad |
| `PATCH /api/v1/despachos/<id>/llegada/` | CU-07 | Reportar llegada a emergencia |
| `GET /api/v1/notificaciones/` | CU-07 | Listar notificaciones de despacho |
| `POST /api/v1/notificaciones/<id>/aceptar/` | CU-07 | Aceptar despacho asignado |
| `GET /api/v1/retiros/` | CU-09 | Listar solicitudes de retiro vehicular |
| `POST /api/v1/retiros/solicitar/` | CU-09 | Solicitar retiro de vehículo |
| `PATCH /api/v1/retiros/<id>/aceptar/` | CU-09 | Aprobar solicitud de retiro |
| `PATCH /api/v1/retiros/<id>/finalizar/` | CU-09 | Finalizar retiro vehicular |

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
| `GET /api/v1/estados-unidad/` | Estados de unidad de emergencia |
| `GET /api/v1/tipos-unidad/` | Tipos de unidad de emergencia |

---

## Comandos Útiles

```bash
# Re-seedear usuarios JWT
python manage.py seed_auth_users

# Build frontend
cd frontend && npx ng build

# Tests de backend
python manage.py test accidentes

# Verificar sintaxis Python (en todos los .py del backend)
python -m py_compile manage.py
python -c "import py_compile; import os; [py_compile.compile(os.path.join(r, f)) for r, d, fs in os.walk('accidentes') for f in fs if f.endswith('.py') and r.count(os.sep) < 8]"
```
