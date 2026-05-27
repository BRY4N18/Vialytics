**DOCUMENTO DE ESPECIFICACIÓN DE**

**REQUERIMIENTOS DE SOFTWARE**

**Sistema de Gestión de Accidentes**

**(SGA)**

| **Versión**       | 1.0                               |
| ----------------- | --------------------------------- |
| **Fecha**         | Mayo 2025                         |
| **Autor**         | Lombeida Escaleras Bryan Humberto |
| **Estado**        | Borrador                          |
| **Clasificación** | Confidencial                      |

# **1\. Introducción**

## **1.1 Propósito del Documento**

El presente documento constituye la Especificación de Requerimientos de Software (SRS) para el Sistema de Gestión de Accidentes (SGA), una aplicación web de gestión operativa y analítica de accidentes viales. Este documento describe en detalle los requerimientos funcionales y no funcionales que debe satisfacer el sistema, sirviendo como contrato técnico entre los stakeholders, el equipo de desarrollo y el equipo de aseguramiento de calidad.

La audiencia objetivo incluye: desarrolladores de software, arquitectos de soluciones, analistas de negocio, gestores de proyectos, equipos de operaciones de emergencia y entidades reguladoras con interés en la interoperabilidad del sistema.

## **1.2 Alcance del Sistema**

El SGA es una plataforma web centralizada diseñada para gestionar el ciclo de vida completo de los accidentes viales, desde su registro inicial hasta su archivo y análisis histórico. El sistema está orientado a organismos de gestión de tráfico, fuerzas de emergencia, autoridades reguladoras y consumidores analíticos.

El sistema contempla cinco grandes áreas funcionales:

- Gestión operativa de accidentes en tiempo real.
- Coordinación de respuesta a emergencias.
- Consulta, análisis estadístico y exportación de datos históricos.
- Portal público de transparencia ciudadana.
- Administración centralizada de usuarios, roles y auditoría.

## **1.3 Definiciones, Acrónimos y Abreviaturas**

| **Término / Acrónimo** | **Definición**                                                                      |
| ---------------------- | ----------------------------------------------------------------------------------- |
| **SGA**                | Sistema de Gestión de Accidentes.                                                   |
| **SRS**                | Software Requirements Specification (Especificación de Requerimientos de Software). |
| **CU**                 | Caso de Uso.                                                                        |
| **API**                | Application Programming Interface.                                                  |
| **RBAC**               | Role-Based Access Control (Control de Acceso Basado en Roles).                      |
| **PII**                | Personally Identifiable Information (Información Personal Identificable).           |
| **TLS**                | Transport Layer Security.                                                           |
| **GDPR**               | General Data Protection Regulation.                                                 |
| **CCPA**               | California Consumer Privacy Act.                                                    |
| **WCAG**               | Web Content Accessibility Guidelines.                                               |
| **NFR**                | Non-Functional Requirement (Requerimiento No Funcional).                            |
| **GPS**                | Global Positioning System.                                                          |
| **KPI**                | Key Performance Indicator.                                                          |

## **1.4 Referencias**

- IEEE Std 830-1998 - IEEE Recommended Practice for Software Requirements Specifications.
- ISO/IEC 25010:2011 - Systems and software Quality Requirements and Evaluation (SQuaRE).
- NIST SP 800-53 Rev. 5 - Security and Privacy Controls for Information Systems and Organizations.
- ISO/IEC 27001:2022 - Information Security Management Systems.
- WCAG 2.1 - Web Content Accessibility Guidelines.
- GDPR (Reglamento UE 2016/679) y CCPA (California Consumer Privacy Act).
- Diagrama de casos de uso SGA - Bryan Lombeida (2025).

## **1.5 Visión General del Documento**

El presente documento se organiza en las siguientes secciones: Sección 2 describe el sistema en términos generales; Sección 3 detalla los requerimientos funcionales agrupados en paquetes de casos de uso; Sección 4 especifica los requerimientos no funcionales por categoría; Sección 5 describe las interfaces del sistema; y Sección 6 establece las restricciones de diseño e implementación.

# **2\. Descripción General del Sistema**

## **2.1 Perspectiva del Producto**

El SGA es una aplicación web nueva, independiente, que opera como plataforma central para la gestión integral de accidentes viales. Se comunica con sistemas externos de despacho de emergencias (ambulancias, policía, grúas) mediante APIs REST/webhooks, y puede integrarse con sistemas de navegación y tráfico a través de sus endpoints de accidentes activos.

La plataforma expone tres portales diferenciados:

- Portal Operativo: para operadores y unidades respondientes, con acceso en tiempo real.
- Portal Analítico: para consumidores analíticos (aseguradoras, investigadores, instituciones).
- Portal Público: acceso sin autenticación para ciudadanos.

## **2.2 Funciones Principales del Sistema**

A continuación se enumeran las macrofunciones del SGA:

- Registro y gestión del ciclo de vida completo de accidentes viales.
- Visualización geoespacial en tiempo real de incidentes activos.
- Despacho automatizado y coordinación de servicios de emergencia.
- Asignación de severidad estandarizada con clasificación automática asistida.
- Gestión del retiro vehicular y cadena de custodia.
- Búsqueda, análisis estadístico y generación de informes sobre histórico de accidentes.
- Exportación de datos en formatos CSV y PDF.
- Visualización de mapas de calor de siniestralidad.
- Solicitud formal de expedientes oficiales de accidentes.
- Consulta pública de mapa de accidentes activos y estadísticas históricas agregadas.
- Administración centralizada de usuarios, roles y permisos (RBAC).
- Auditoría completa e inmutable de accesos y modificaciones.

## **2.3 Características de los Usuarios**

| **Perfil de Usuario**    | **Descripción / Rol**                                                | **Nivel de Acceso**                       |
| ------------------------ | -------------------------------------------------------------------- | ----------------------------------------- |
| **Operador**             | Gestiona accidentes en tiempo real desde el dashboard principal.     | Portal Operativo - Lectura/Escritura      |
| **Unidad Respondiente**  | Recibe despachos y actualiza estados desde la interfaz móvil/web.    | Portal Operativo - Escritura limitada     |
| **Consumidor Analítico** | Busca, analiza y exporta datos históricos de accidentes.             | Portal Analítico - Solo lectura           |
| **Ciudadano**            | Consulta el mapa público y estadísticas agregadas sin autenticación. | Portal Público - Solo lectura             |
| **Administrador**        | Gestiona usuarios, roles, permisos y auditoría del sistema.          | Consola de Administración - Control total |
| **Supervisor de Turno**  | Monitorea operaciones sin capacidad de edición.                      | Portal Operativo - Solo lectura           |

## **2.4 Restricciones Generales**

- El sistema deberá ser desarrollado como aplicación web (SPA o MPA) accesible desde navegadores modernos sin instalación de software adicional en el cliente.
- La interfaz debe ser completamente responsive para desktop, tablet y móvil.
- Toda la comunicación entre cliente y servidor debe estar cifrada con TLS 1.3.
- El sistema debe cumplir con las legislaciones de protección de datos aplicables (GDPR, CCPA y leyes locales).
- La arquitectura debe soportar despliegue en múltiples zonas de disponibilidad para garantizar el SLA de 99.9% uptime.

## **2.5 Suposiciones y Dependencias**

- Se asume disponibilidad de APIs de mapas geoespaciales (p.ej. Google Maps, OpenStreetMap) para la visualización cartográfica.
- Los sistemas externos de despacho de cada servicio de emergencia cuentan con endpoints API o mecanismos de notificación compatibles.
- Los datos meteorológicos se obtendrán de servicios externos configurados durante la implementación.
- El servicio de identidad puede integrarse con proveedores OAuth2/OIDC existentes de las organizaciones usuarias.
- Los usuarios disponen de dispositivos con navegador actualizado y conectividad a internet.

# **3\. Requerimientos Funcionales**

Los requerimientos funcionales están organizados en cinco paquetes que agrupan los casos de uso del sistema según el área funcional a la que pertenecen. Cada caso de uso incluye su propósito, descripción y las historias de usuario que lo detallan.

## **PKG 1 - Gestión de Accidentes**

Este paquete contiene los casos de uso centrales del sistema, orientados a la gestión del ciclo de vida de cada accidente vial desde su registro hasta su archivo definitivo.

### **CU-01 - Registrar Accidente**

| **CU-01** | | **Registrar Accidente** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 10 - Alta | **Nivel** | Operativo |
| **Propósito** | Permitir que un operador cree manualmente el registro de un accidente cuando la información llega por vía telefónica, por radio, garantizando que ningún evento quede sin documentar en el sistema. | | |
| **Descripción** | El operador accede al formulario de registro desde el dashboard principal. Ingresa la ubicación, número estimado de vehículos involucrados, presencia de heridos, causa aparente y fuente del reporte. | | |
| **Historias de Usuario** | | | |
| HU-01.1 Como operador deseo crear un accidente en el mapa en menos de 30 segundos seleccionando la ubicación y completando los datos básicos, para reaccionar con rapidez sin perder tiempo mientras gestiono varias situaciones simultáneamente. | | | |
| HU-01.2 Como operador deseo adjuntar una nota de texto al momento de crear el accidente con información adicional proporcionada por el llamante, para que los servicios de respuesta tengan contexto completo al llegar al lugar. | | | |
| HU-01.3 Como operador deseo que los campos de ubicación validen la entrada contra un catálogo estandarizado, para asegurar la consistencia, integridad y calidad de los datos desde su captura inicial. | | | |
| HU-01.4 Como operador deseo poder seleccionar la fuente del reporte, para estandarizar el origen de la información. | | | |

### **CU-02 - Visualizar Mapa de Accidentes en Tiempo Real**

| **CU-02** | | **Visualizar Mapa de Accidentes en Tiempo Real** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 10 - Alta | **Nivel** | Operativo |
| **Propósito** | Proporcionar a los operadores una vista geoespacial centralizada y actualizada de todos los accidentes activos en la red vial, con capacidad de filtrado y detalle por evento. | | |
| **Descripción** | El operador puede ver y filtrar por área geográfica, tipo de vía, rango horario, severidad y estado. Al hacer clic en un accidente se despliega un panel lateral con el detalle completo del expediente. | | |
| **Historias de Usuario** | | | |
| HU-02.1 Como operador deseo que el mapa distinga visualmente los accidentes por severidad con iconos de color, para priorizar mi atención en tiempo real sin tener que leer cada reporte individualmente. | | | |
| HU-02.2 Como operador deseo filtrar el mapa para mostrar únicamente los accidentes en autopistas durante las últimas dos horas, para preparar el reporte del turno sin recorrer toda la lista manualmente. | | | |
| HU-02.3 Como operador deseo que el panel lateral me muestre un indicador visual del tiempo transcurrido desde el reporte inicial, para monitorear qué accidentes críticos corren el riesgo de exceder los tiempos máximos de respuesta. | | | |
| HU-02.4 Como operador deseo ocultar temporalmente los incidentes en estado 'Despejado' del mapa principal, para reducir la carga visual y focalizar la coordinación en las emergencias activas. | | | |

### **CU-03 - Actualizar Estado de Accidente**

| **CU-03** | | **Actualizar Estado de Accidente** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 9 - Alta | **Nivel** | Operativo |
| **Propósito** | Permitir que operadores y unidades respondientes actualicen el estado de progreso de un accidente para que toda la red de usuarios cuente con información fidedigna y actualizada sobre la evolución del evento. | | |
| **Descripción** | El operador autorizado puede cambiar el estado del accidente. Los estados también pueden ser actualizados por las unidades respondientes desde su interfaz móvil (web). | | |
| **Historias de Usuario** | | | |
| HU-03.1 Como operador deseo cambiar el estado de un accidente a 'Despejado' con un clic desde el panel de detalle adjuntando una nota de cierre, para que los sistemas de navegación integrados dejen de desviar el tráfico. | | | |
| HU-03.2 Como operador deseo marcar que el vehículo accidentado fue retirado completamente, para que se actualice el estado del carril afectado sin necesidad de llamadas por radio. | | | |
| HU-03.3 Como operador deseo recibir una notificación cuando el estado de un accidente que yo originé cambie a 'Atendido', para confirmar que los servicios de emergencia llegaron al lugar. | | | |
| HU-03.4 Como operador deseo recibir el evento de cambio de estado en menos de 10 segundos desde que el operador lo actualiza, para estar enterado del flujo del accidente. | | | |

### **CU-04 - Despachar Servicios de Emergencia**

| **CU-04** | | **Despachar Servicios de Emergencia** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 10 - Alta | **Nivel** | Operativo |
| **Propósito** | Coordinar el envío de unidades de emergencia al lugar del accidente desde el SGA, garantizando que los recursos correctos lleguen en el menor tiempo posible con la información completa del evento. | | |
| **Descripción** | Desde el panel del accidente, el operador puede solicitar el despacho de uno o varios tipos de servicio con un clic. El sistema genera una notificación estructurada a los sistemas de despacho de cada servicio con: coordenadas exactas, severidad, número estimado de heridos, tipo de vehículos y condiciones de acceso. | | |
| **Historias de Usuario** | | | |
| HU-04.1 Como operador deseo despachar simultáneamente una ambulancia, una unidad policial y una grúa al lugar del accidente con una sola acción desde el panel, para reducir el tiempo total de respuesta eliminando llamadas telefónicas individuales. | | | |
| HU-04.2 Como operador deseo recibir la notificación de despacho con las coordenadas exactas, el número estimado de heridos y el tipo de impacto, para preparar el material médico adecuado antes de llegar al lugar. | | | |
| HU-04.3 Como operador deseo ver en el panel del accidente qué servicios fueron despachados, a qué hora confirmaron y a qué hora llegaron, para evaluar los tiempos de respuesta de cada turno. | | | |
| HU-04.4 Como operador deseo que la notificación de despacho incluya si hay mercancías peligrosas en los vehículos involucrados, para llegar al lugar con el equipo correcto de protección. | | | |

### **CU-05 - Archivar Accidente**

| **CU-05** | | **Archivar Accidente** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 8 - Media-Alta | **Nivel** | Operativo |
| **Propósito** | Finalizar formalmente el ciclo de vida de un accidente, consolidando toda la información recopilada, marcándolo como resuelto y almacenándolo en el histórico para consulta futura, análisis estadístico y cumplimiento normativo. | | |
| **Descripción** | El operador confirma el cierre del accidente una vez recibida la confirmación de que la vía está despejada y los servicios han concluido su actuación. El sistema consolida en el expediente: partes policiales, fotos, datos meteorológicos, unidades intervinientes y tiempo total de resolución. | | |
| **Historias de Usuario** | | | |
| HU-05.1 Como operador deseo cerrar un accidente desde el panel con un clic de confirmación añadiendo una nota final sobre las causas, para que el expediente quede completo sin rellenar un formulario extenso al final de un turno. | | | |
| HU-05.2 Como operador deseo que al cerrarse un accidente se calcule y persista automáticamente el tiempo total de resolución, para usarlo como variable objetivo en modelos predictivos sin calcular este dato manualmente. | | | |
| HU-05.3 Como operador deseo que al archivar accidentes con más de dos años de antigüedad el sistema aplique automáticamente la política de anonimización de datos personales, para cumplir con la legislación de protección de datos. | | | |
| HU-05.4 Como operador deseo generar al fin de cada turno un resumen automático de todos los accidentes, para incluirlo en el informe operativo sin procesar ni cruzar los datos manualmente. | | | |

### **CU-06 - Asignar Severidad**

| **CU-06** | | **Asignar Severidad** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 8 - Media-Alta | **Nivel** | Operativo |
| **Propósito** | Establecer el nivel de severidad y tipología de cada accidente de forma estandarizada, para guiar la prioridad de respuesta, los recursos a despachar y la visibilidad que tendrá el evento en los distintos portales del SGA. | | |
| **Descripción** | El operador puede revisar y sobrescribir la clasificación propuesta. Escala: Leve (sin heridos, sin cierre de carril) / Moderado (heridos leves, carril parcial) / Grave (heridos graves o múltiples vehículos) / Fatal (fallecidos confirmados). | | |
| **Historias de Usuario** | | | |
| HU-06.1 Como operador deseo que el sistema me proponga automáticamente una severidad basada en los datos disponibles pero que yo pueda modificarla si tengo información adicional del terreno, para mantener precisión sin perder velocidad de respuesta. | | | |
| HU-06.2 Como operador deseo que los accidentes clasificados como 'Fatal' activen automáticamente el protocolo de notificación a la autoridad de tránsito, para garantizar la respuesta institucional correcta. | | | |
| HU-06.3 Como operador deseo que el nivel de severidad quede registrado con historial de cambios auditable, para usarlo como referencia objetiva en la validación de reclamaciones. | | | |
| HU-06.4 Como operador deseo elevar la severidad a 'Grave' manualmente si recibo actualizaciones críticas por radio, para que el sistema escale la prioridad y despache recursos adicionales de inmediato. | | | |

## **PKG 2 - Respuesta a Emergencias**

Este paquete agrupa los casos de uso orientados a la coordinación de las unidades de campo y servicios de emergencia durante la atención de un accidente.

### **CU-07 - Recibir Despacho de Emergencias**

| **CU-07** | | **Recibir Despacho de Emergencias** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 10 - Alta | **Nivel** | Operativo |
| **Propósito** | Garantizar que las unidades de emergencia reciban la notificación de despacho de forma inmediata, clara y completa, con toda la información del accidente necesaria para preparar la respuesta antes de llegar al lugar. | | |
| **Descripción** | Cuando el operador activa un despacho, la unidad correspondiente recibe una notificación push en su dispositivo con: dirección exacta, coordenadas GPS, severidad, tipo de accidente, número estimado de afectados, tipo de vehículos involucrados y mercancías peligrosas si aplica. | | |
| **Historias de Usuario** | | | |
| HU-07.1 Como unidad de emergencia deseo recibir el despacho con el número de heridos estimado, para preparar el material médico específico durante el trayecto y llegar listo para actuar desde el primer segundo en escena. | | | |
| HU-07.2 Como operador deseo recibir confirmación de aceptación del despacho de cada unidad en menos de 60 segundos, para confirmar la cobertura del accidente y gestionar alternativas de inmediato si alguna unidad no responde. | | | |
| HU-07.3 Como unidad de emergencia deseo que la notificación incluya si hay mercancías peligrosas según el parte policial o la telemetría disponible, para activar el protocolo de materiales peligrosos desde la salida. | | | |
| HU-07.4 Como unidad de emergencia deseo recibir el tipo y características del vehículo accidentado, para asignar la grúa de capacidad adecuada. | | | |

### **CU-08 - Actualizar Estado de Unidad**

| **CU-08** | | **Actualizar Estado de Unidad** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 8 - Media-Alta | **Nivel** | Operativo |
| **Propósito** | Permitir que las unidades de campo actualicen su estado operativo en tiempo real para que haya completa visibilidad de los recursos disponibles. | | |
| **Descripción** | La unidad de emergencia puede cambiar el estado con un solo toque. Estados predefinidos: En base / En camino / En escena / En traslado / Regreso / Disponible. | | |
| **Historias de Usuario** | | | |
| HU-08.1 Como unidad de emergencia deseo marcar 'En escena' con un solo toque cuando llego al accidente, para que registre automáticamente mi tiempo de respuesta real sin comunicarlo por radio mientras atiendo víctimas. | | | |
| HU-08.2 Como unidad de emergencia deseo recibir la notificación de 'En traslado' cuando una ambulancia sale hacia mi centro, para confirmar la disponibilidad de camas y personal especializado antes de la llegada del paciente. | | | |
| HU-08.3 Como unidad de emergencia deseo actualizar mi estado a 'Disponible' una vez finalizado el retiro vehicular, para que me incluyan en el listado de unidades disponibles para nuevos despachos. | | | |

### **CU-09 - Gestionar Retiro Vehicular**

| **CU-09** | | **Gestionar Retiro Vehicular** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 7 - Media | **Nivel** | Operativo |
| **Propósito** | Coordinar la asignación del servicio de grúa y auxilio vial para los vehículos accidentados, garantizando el despeje oportuno de la vía y la correcta cadena de custodia del vehículo retirado. | | |
| **Descripción** | El operador asigna una grúa, el servicio de emergencia acepta el servicio. Al finalizar, el conductor sube fotos del vehículo retirado y un informe de auxilio. | | |
| **Historias de Usuario** | | | |
| HU-09.1 Como operador deseo recibir una notificación inmediata cuando uno de mis vehículos sea retirado por una grúa del SGA, para activar el proceso de seguro y contactar al usuario conductor de forma proactiva. | | | |
| HU-09.2 Como operador deseo que el sistema registre el tiempo entre el despacho de la grúa y el despeje del carril, para evaluar el desempeño de los proveedores de auxilio vial. | | | |
| HU-09.3 Como unidad de emergencia deseo recibir las solicitudes de servicio del SGA directamente, para asignar automáticamente la grúa más cercana disponible de capacidad adecuada. | | | |

## **PKG 3 - Consulta y Análisis**

Conjunto de casos de uso destinados a los consumidores analíticos que requieren acceder, explorar y exportar datos históricos del sistema para análisis estadístico, investigación y cumplimiento normativo.

### **CU-10 - Buscar Accidentes Históricos**

| **CU-10** | | **Buscar Accidentes Históricos** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 8 - Media-Alta | **Nivel** | Táctico |
| **Propósito** | Permitir que los consumidores analíticos localicen accidentes específicos del pasado mediante filtros multidimensionales, para obtener información necesaria en procesos de planificación de seguridad vial. | | |
| **Descripción** | El consumidor analítico busca accidentes mediante filtros: rango de fechas, ubicación, severidad, tipo de evento, condición climática, número de víctimas, número de parte policial y matrícula de vehículo. | | |
| **Historias de Usuario** | | | |
| HU-10.1 Como consumidor analítico deseo buscar un accidente por matrícula del vehículo asegurado y acceder a sus datos básicos en menos de un minuto, para iniciar la validación de la reclamación sin depender de la disponibilidad de la comisaría. | | | |
| HU-10.2 Como consumidor analítico deseo buscar todos los accidentes ocurridos en una intersección específica en los últimos tres años con sus datos de severidad, para documentar el historial de siniestralidad del punto. | | | |
| HU-10.3 Como consumidor analítico deseo acceder al expediente completo del accidente con parte, fotos, datos meteorológicos y telemetría, para evitar solicitar información a múltiples instituciones. | | | |
| HU-10.4 Como consumidor analítico deseo buscar accidentes filtrando simultáneamente por condición climática, franja horaria y tipo de vía en un rango de cinco años, para analizar correlaciones entre factores ambientales y siniestralidad. | | | |

### **CU-11 - Generar Informes Estadísticos**

| **CU-11** | | **Generar Informes Estadísticos** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 7 - Media | **Nivel** | Táctico |
| **Propósito** | Producir informes cuantitativos sobre la siniestralidad vial en un período y área determinados para satisfacer las necesidades de reporte de actores reguladores, sanitarios, aseguradoras y organismos de planificación. | | |
| **Descripción** | El consumidor analítico configura los informes con dimensiones de análisis (tiempo, geografía, tipo de vía, tipo de evento, perfil de víctimas) y métricas (número de accidentes, tasa por 100k habitantes, víctimas mortales, tiempo medio de resolución). | | |
| **Historias de Usuario** | | | |
| HU-11.1 Como consumidor analítico deseo generar mensualmente un informe automático de accidentalidad con desglose por tipo de usuario vial, para alimentar el sistema nacional de estadísticas sin trabajo manual. | | | |
| HU-11.2 Como consumidor analítico deseo generar informes de siniestralidad filtrados por calle y franja horaria, para ajustar los modelos de tarificación de pólizas de automóvil con datos objetivos del mercado. | | | |
| HU-11.3 Como consumidor analítico deseo generar un informe de calidad de datos mensual con el porcentaje de accidentes con coordenadas válidas y partes completos, para identificar fuentes con baja calidad. | | | |
| HU-11.4 Como consumidor analítico deseo generar un informe comparativo interanual de accidentes fatales con visualizaciones incluidas en PDF, para presentarlo ante el consejo de gobierno. | | | |

### **CU-12 - Exportar Datos (CSV, PDF)**

| **CU-12** | | **Exportar Datos (CSV, PDF)** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 7 - Media | **Nivel** | Táctico |
| **Propósito** | Permitir que los actores analíticos descarguen los datos del SGA en formatos estándar de la industria para su análisis en herramientas externas, maximizando la interoperabilidad del sistema. | | |
| **Descripción** | El consumidor analítico, después de aplicar sus filtros, puede exportar los datos en CSV y PDF. | | |
| **Historias de Usuario** | | | |
| HU-12.1 Como consumidor analítico deseo exportar los accidentes de los últimos cinco años en formato CSV y cargarlos con la capa de infraestructura vial, para identificar puntos críticos y priorizar inversiones de mejora vial. | | | |
| HU-12.2 Como consumidor analítico deseo descargar los datos de víctimas anonimizados con edad, sexo y tipo de lesión en CSV, para producir modelos de carga de enfermedad y publicar resultados en revista científica. | | | |
| HU-12.3 Como consumidor analítico deseo exportar el expediente completo de un accidente en PDF con todos sus documentos adjuntos, para adjuntarlo como prueba documental en un proceso judicial. | | | |
| HU-12.4 Como consumidor analítico deseo que los archivos CSV exportados incluyan metadatos claros y estructura relacional limpia, para integrarlos directamente en pipelines de ingesta o herramientas de inteligencia de datos. | | | |

### **CU-13 - Visualizar Mapa de Calor**

| **CU-13** | | **Visualizar Mapa de Calor** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 8 - Media-Alta | **Nivel** | Táctico |
| **Propósito** | Representar visualmente la concentración geográfica de siniestralidad mediante mapas de calor configurables, permitiendo identificar puntos negros, corredores peligrosos y patrones espaciales. | | |
| **Descripción** | El consumidor analítico genera mapas de calor interactivos basados en el histórico filtrado por período, tipo de evento, severidad, modo de transporte y condición climática. Usa escala de color de baja a alta densidad. Los puntos negros se destacan automáticamente. | | |
| **Historias de Usuario** | | | |
| HU-13.1 Como consumidor analítico deseo visualizar el mapa de calor de atropellos a peatones en mi municipio filtrado por franja horaria, para identificar los cruces más peligrosos y priorizar la instalación de semáforos. | | | |
| HU-13.2 Como consumidor analítico deseo ver el mapa de calor antes y después de una intervención vial, para evaluar si la medida implementada redujo la siniestralidad con datos objetivos. | | | |
| HU-13.3 Como consumidor analítico deseo comparar mapas de calor de dos períodos anuales consecutivos, para identificar tendencias de mejora o deterioro de la siniestralidad. | | | |
| HU-13.4 Como consumidor analítico deseo visualizar el mapa de calor para ajustar los itinerarios de mis vehículos evitando tramos con mayor historial de accidentes. | | | |

### **CU-14 - Solicitar Expediente Oficial**

| **CU-14** | | **Solicitar Expediente Oficial** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 6 - Media | **Nivel** | Táctico |
| **Propósito** | Proporcionar un proceso formal para que actores autorizados soliciten el expediente completo de un accidente cumpliendo los requisitos legales de cadena de custodia y protección de datos. | | |
| **Descripción** | El consumidor analítico solicita el expediente, indica el accidente y el motivo legal de la solicitud. Si requiere revisión, se crea un flujo de aprobación gestionado por el responsable de privacidad. | | |
| **Historias de Usuario** | | | |
| HU-14.1 Como consumidor analítico deseo solicitar el expediente de un accidente en línea adjuntando mi autorización profesional, para agilizar la preparación del caso. | | | |
| HU-14.2 Como consumidor analítico deseo poder solicitar de forma masiva los expedientes de mis siniestros del último mes, para integrarlos en mi sistema de gestión de reclamaciones sin intervención manual. | | | |
| HU-14.3 Como consumidor analítico deseo recibir el expediente con todos los archivos multimedia del accidente, para tener todos los elementos de análisis en un solo lugar desde el inicio de la investigación. | | | |

## **PKG 4 - Portal Externo (Ciudadano)**

Casos de uso que cubren el acceso público sin autenticación al sistema, orientados a la transparencia institucional y la información ciudadana sobre la siniestralidad vial.

### **CU-15 - Consultar Mapa Público de Accidentes**

| **CU-15** | | **Consultar Mapa Público de Accidentes** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 9 - Alta | **Nivel** | Operativo |
| **Propósito** | Proporcionar a los ciudadanos un acceso público y transparente a la información de accidentes activos en la red vial, con un nivel de detalle apropiado que no comprometa datos personales ni la privacidad de los involucrados. | | |
| **Descripción** | Los ciudadanos verán un mapa interactivo sin necesidad de registro. No se exponen datos personales, matrículas ni información policial sensible. | | |
| **Historias de Usuario** | | | |
| HU-15.1 Como ciudadano deseo consultar el mapa público del SGA para ver si hay accidentes en mi ruta habitual al trabajo, para decidir si tomo la autopista o una vía alternativa antes de salir. | | | |
| HU-15.2 Como ciudadano deseo que el mapa sea accesible para lectores de pantalla y que los accidentes en mi zona puedan consultarse, para planificar mis desplazamientos de forma autónoma. | | | |
| HU-15.3 Como ciudadano deseo poder consultar el mapa público disponible en inglés y español, para entender los accidentes en la zona que voy a visitar y ajustar mi itinerario. | | | |
| HU-15.4 Como ciudadano deseo visualizar un gráfico de barras interactivo con los accidentes mensuales del último año, para identificar visualmente los picos de siniestralidad. | | | |

### **CU-16 - Consultar Estadísticas Históricas Públicas**

| **CU-16** | | **Consultar Estadísticas Históricas Públicas** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 6 - Media | **Nivel** | Táctico |
| **Propósito** | Ofrecer a los ciudadanos un acceso simplificado a estadísticas agregadas de siniestralidad histórica sin requerir autenticación, fomentando la transparencia institucional y la cultura de seguridad vial. | | |
| **Descripción** | Los ciudadanos ven en el portal público una sección de estadísticas históricas simplificadas. Los datos son completamente agregados y no contienen información personal. | | |
| **Historias de Usuario** | | | |
| HU-16.1 Como ciudadano deseo consultar cuántos accidentes han ocurrido en mi ciudad en el último año y cómo se compara con el año anterior, para participar informado en debates del consejo municipal sobre seguridad vial. | | | |
| HU-16.2 Como ciudadano deseo acceder a las estadísticas históricas de siniestralidad por tipo de vía para mi trabajo de fin de grado sin necesidad de acreditar mi institución, para usar datos oficiales y citables. | | | |
| HU-16.3 Como ciudadano deseo consultar la evolución histórica de accidentes con peatones en mi ciudad para los últimos diez años disponibles, para publicar una nota comparativa con datos verificables de una fuente oficial pública. | | | |

## **PKG 5 - Administración del Sistema**

Casos de uso administrativos que garantizan la correcta operación, seguridad y auditabilidad del sistema. Son gestionados exclusivamente por administradores del sistema.

### **CU-17 - Gestionar Usuarios**

| **CU-17** | | **Gestionar Usuarios** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 10 - Alta | **Nivel** | Operativo |
| **Propósito** | Administrar de forma centralizada las identidades de todos los usuarios del SGA, sus datos de perfil, credenciales y organizaciones asignadas, garantizando que cada persona acceda al sistema con las herramientas correctas y con procesos de alta y baja controlados. | | |
| **Descripción** | El administrador puede crear, editar, suspender y eliminar usuarios. | | |
| **Historias de Usuario** | | | |
| HU-17.1 Como administrador deseo crear el perfil de un nuevo operador y asignarle credenciales de acceso desde la consola en menos de 5 minutos, para garantizar que el operador pueda iniciar su turno sin demoras el primer día. | | | |
| HU-17.2 Como administrador deseo obtener un informe completo de todos los usuarios activos con su organización, fecha de último acceso y nivel de permisos, para verificar el cumplimiento del principio de mínimo privilegio durante la revisión de seguridad. | | | |
| HU-17.3 Como administrador deseo bloquear inmediatamente la cuenta de un usuario comprometido desde la consola con un solo clic, para contener una brecha de seguridad en menos de 30 segundos. | | | |

### **CU-18 - Gestionar Roles y Permisos**

| **CU-18** | | **Gestionar Roles y Permisos** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 9 - Alta | **Nivel** | Operativo |
| **Propósito** | Definir y administrar el modelo de control de acceso basado en roles del SGA, asignando permisos granulares a cada perfil de usuario para garantizar que cada actor acceda únicamente a la información y funcionalidades correspondientes a su función. | | |
| **Descripción** | El administrador puede ver en tiempo real qué usuarios tienen asignado cada rol. Los cambios de permisos se aplican inmediatamente sin necesidad de que los usuarios cierren sesión. | | |
| **Historias de Usuario** | | | |
| HU-18.1 Como administrador deseo crear un rol personalizado 'Consultor de Siniestros' con acceso solo de lectura al módulo de búsqueda histórica filtrado por organización, para garantizar que las aseguradoras solo vean sus propios datos. | | | |
| HU-18.2 Como administrador deseo que los cambios en los permisos de un rol se apliquen de forma inmediata, para corregir un error de asignación con efecto inmediato ante una situación de riesgo de seguridad detectada. | | | |
| HU-18.3 Como administrador deseo obtener el listado completo de permisos asociados a cada rol, para verificar que el modelo de control de acceso cumple con los requisitos de la política de seguridad institucional. | | | |
| HU-18.4 Como administrador deseo definir un rol 'Supervisor de turno' con permisos para ver todos los accidentes activos pero sin capacidad de editarlos ni despachar servicios, para permitir monitoreo sin interferir en las operaciones. | | | |

### **CU-19 - Auditar Accesos**

| **CU-19** | | **Auditar Accesos** | |
| --- | | --- | | --- | --- |
| **Prioridad** | 9 - Alta | **Nivel** | Estratégico |
| **Propósito** | Mantener un registro inmutable y consultable de todos los accesos al SGA para cumplir con requisitos legales de auditoría, detectar comportamientos anómalos y facilitar la investigación de incidentes de seguridad. | | |
| **Descripción** | El administrador puede buscar logs por usuario, IP, resultado, fecha y módulo. Los logs se exportan en formato estándar para análisis externo y se pueden configurar alertas automáticas por patrones anómalos. El administrador puede comparar versiones de un registro con una vista de diferencias. | | |
| **Historias de Usuario** | | | |
| HU-19.1 Como administrador deseo consultar quién accedió a los datos de un accidente específico y en qué momento, para responder a una solicitud de información de un ciudadano que ejerce su derecho de acceso bajo la legislación de protección de datos. | | | |
| HU-19.2 Como administrador deseo obtener el log de auditoría de quién accedió al expediente de un accidente y qué acciones realizó, para verificar la cadena de custodia digital y garantizar la integridad. | | | |
| HU-19.3 Como administrador deseo ver el historial completo de cambios de estado de un accidente con el nombre del operador responsable de cada cambio, para entender la cronología de gestión al revisar un expediente cerrado. | | | |

# **4\. Requerimientos No Funcionales**

Los requerimientos no funcionales definen los atributos de calidad, restricciones operativas y estándares que debe cumplir el SGA con independencia de las funcionalidades específicas. Son de cumplimiento obligatorio para garantizar la viabilidad, seguridad y sostenibilidad del sistema en producción.

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>Categoría</strong></p></th><th><p><strong>Requerimientos</strong></p></th></tr><tr><td><p><strong>Rendimiento</strong></p></td><td><ul><li>Latencia de ingesta a visualización &lt; 5 segundos para el 95% de los incidentes.</li><li>Dashboard debe cargar en &lt; 3 segundos con hasta 500 incidentes activos.</li><li>API de consulta histórica: respuesta &lt; 2 s para consultas de un año.</li></ul></td></tr><tr><td><p><strong>Disponibilidad</strong></p></td><td><ul><li>99.9% de uptime para el portal web y APIs críticas (24/7/365).</li><li>Arquitectura activa-activa en múltiples zonas de disponibilidad.</li></ul></td></tr><tr><td><p><strong>Escalabilidad</strong></p></td><td><ul><li>Soporte para hasta 10,000 incidentes activos simultáneos.</li><li>Capacidad de ingerir 500 eventos/segundo en picos.</li><li>Autoescalado de componentes web y de procesamiento.</li></ul></td></tr><tr><td><p><strong>Seguridad</strong></p></td><td><ul><li>Cifrado en tránsito (TLS 1.3) y en reposo (AES-256).</li><li>Pruebas de penetración anuales y escaneo continuo de vulnerabilidades.</li><li>Cumplimiento con estándares NIST SP 800-53 o ISO 27001.</li><li>Enmascaramiento de PII según perfil y jurisdicción.</li></ul></td></tr><tr><td><p><strong>Privacidad</strong></p></td><td><ul><li>Conformidad con GDPR, CCPA y leyes locales de protección de datos.</li><li>Módulo de gestión de consentimientos y derecho al olvido.</li></ul></td></tr><tr><td><p><strong>Usabilidad</strong></p></td><td><ul><li>Interfaz adaptativa (responsive) para uso en desktop, tablet y móvil.</li><li>Cumplimiento WCAG 2.1 AA para accesibilidad.</li><li>Soporte multiidioma (inglés y español al menos).</li></ul></td></tr><tr><td><p><strong>Mantenibilidad</strong></p></td><td><ul><li>Arquitectura por capas para facilitar la evolución de módulos independientes.</li><li>Cobertura de pruebas unitarias &gt; 80% en servicios core.</li><li>Documentación técnica y de usuario actualizada.</li></ul></td></tr></tbody></table></div>

# **5\. Interfaces del Sistema**

## **5.1 Interfaces de Usuario**

El SGA proveerá las siguientes interfaces web:

- Dashboard Operativo: Visualización cartográfica en tiempo real, formularios de registro de accidentes, panel de detalle lateral y gestión de despachos.
- Portal Analítico: Motor de búsqueda con filtros avanzados, generador de informes, visor de mapas de calor y exportador de datos.
- Portal Público: Mapa interactivo sin autenticación, estadísticas agregadas y visualizaciones gráficas.
- Consola de Administración: Gestión de usuarios, roles, permisos y visualización de logs de auditoría.

Todos los portales deberán ser accesibles desde navegadores modernos (Chrome, Firefox, Edge, Safari) sin instalación adicional, y con diseño responsive compatible con dispositivos móviles y tablets.

## **5.2 Interfaces de API**

- API REST para integración con sistemas externos de despacho de emergencias (ambulancias, policía, grúas).
- Webhooks de notificación de eventos: cambio de estado, despacho confirmado, accidente archivado.
- API pública de accidentes activos (solo datos no personales) para integración con sistemas de navegación.
- API de exportación histórica para integración con plataformas de análisis externas.
- Endpoint de autenticación OAuth2/OIDC para integración con proveedores de identidad institucionales.

## **5.3 Interfaces de Hardware**

- El sistema debe ser accesible desde dispositivos de escritorio, tablets y smartphones con capacidades estándar de hardware.
- Las unidades respondientes accederán al sistema desde dispositivos móviles (smartphones/tablets) con conectividad 4G/5G o WiFi.
- Se recomienda el uso de dispositivos con GPS integrado para facilitar la actualización de estados de unidades en campo.

## **5.4 Interfaces de Comunicación**

- Comunicación cliente-servidor: HTTPS con TLS 1.3.
- Actualizaciones en tiempo real: WebSockets o Server-Sent Events (SSE) para el mapa operativo.
- Notificaciones push: integración con servicio de notificaciones push (FCM/APNs o similar) para dispositivos móviles de unidades respondientes.
- Integración con APIs de terceros: servicio de mapas geoespaciales, datos meteorológicos y servicios de identidad.

# **6\. Restricciones de Diseño e Implementación**

## **6.1 Restricciones de Arquitectura**

- El sistema debe implementarse como aplicación web (SPA o MPA) con arquitectura por capas que permita la evolución independiente de módulos.
- La arquitectura de backend debe ser stateless y soportar despliegue en contenedores (Docker/Kubernetes) para facilitar el autoescalado.
- Arquitectura activa-activa en múltiples zonas de disponibilidad para garantizar el SLA de 99.9% de uptime.
- Los datos en reposo deben almacenarse con cifrado AES-256. Los datos en tránsito deben protegerse con TLS 1.3.

## **6.2 Restricciones de Estándares**

- La implementación de seguridad debe alinearse con NIST SP 800-53 Rev. 5 o ISO/IEC 27001:2022.
- El tratamiento de datos personales debe cumplir con GDPR (Reglamento UE 2016/679), CCPA y las leyes locales de protección de datos aplicables.
- La accesibilidad de la interfaz debe cumplir con WCAG 2.1 nivel AA.
- Los formatos de exportación de datos deben seguir estándares abiertos (CSV RFC 4180, PDF/A).

## **6.3 Restricciones de Calidad**

- La cobertura de pruebas unitarias de los servicios core debe ser superior al 80%.
- Deben realizarse pruebas de penetración al menos una vez al año y escaneo continuo de vulnerabilidades.
- La documentación técnica (API, arquitectura, operaciones) y de usuario debe mantenerse actualizada con cada release.

## **6.4 Supuestos de Implementación**

- El equipo de desarrollo adoptará metodología ágil con sprints de dos semanas y entregas incrementales.
- La infraestructura de despliegue será en la nube (cloud-native), con proveedor a definir durante la fase de arquitectura.
- Se habilitará un entorno de staging idéntico al de producción para pruebas de carga y regresión.

# **7\. Control de Versiones del Documento**

| **Versión** | **Fecha** | **Cambios**                        | **Autor**                   |
| ----------- | --------- | ---------------------------------- | --------------------------- |
| 1.0         | Mayo 2025 | Versión inicial del documento SRS. | Lombeida Escaleras Bryan H. |

_- Fin del Documento -_
