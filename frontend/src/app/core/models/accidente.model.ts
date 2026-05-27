export interface Severidad {
  idseveridad: number;
  severidad: number;
  descripcion: string;
}

export interface TipoReportado {
  idtiporeportado: number;
  tiporeportado: string;
}

export interface TipoEstadoIncidente {
  idtipoestadoincidente: number;
  tipoestadoincidente: string;
}

export interface Despacho {
  iddespacho: number;
  unidad_nombre: string;
  tipo_unidad: string;
  fechahoradespacho: string;
  fechahoraconfirmacion?: string;
  fechahorallegada?: string;
}

export interface AccidenteMapa {
  idaccidente: string;
  latitudinicio: number;
  longitudinicio: number;
  severidad_nivel: number;
  estado_actual: string;
  numheridos: number;
  numfallecidos: number;
  fecha_actualizacion: string;
  descripcion: string;
  calle_nombre: string;
  ciudad_nombre: string;
}

export interface AccidenteDetalle extends AccidenteMapa {
  numvehiculos: number;
  numvictimas: number;
  horainicio: string;
  horafin?: string;
  codigopostal: string;
  severidad_descripcion: string;
  despachos: Despacho[];
  notas: NotaAccidente[];

  // IDs de ubicación (para pre-llenar el formulario de edición)
  idpais_id?: number | null;
  idestado_id?: number | null;
  idcondado_id?: number | null;
  idciudad_id?: number | null;
  idcalle_id?: number | null;
  idtiporeportado_id?: number | null;
  idseveridad_id?: number | null;
  idperiododia_id?: number | null;
  idreferenciaestacion_id?: number | null;

  // Clima
  condicion_clima?: string;
  temperatura_f?: number;
  humedad_porcentaje?: number;
  visibilidad_millas?: number;
  velocidad_viento_mph?: number;

  // Período del día
  amaneceranochecer?: string;
  crepusculocivil?: string;
  crepusculonautico?: string;
  crepusculoastronomico?: string;

  // Elementos físicos
  cerca_cruce?: boolean;
  cerca_semaforo?: boolean;
  cerca_parada?: boolean;
  cerca_estacion?: boolean;
  cerca_bache?: boolean;
  cerca_viatren?: boolean;

  // Estado del conductor
  estadosobriedad?: boolean;
  nivelatencion?: boolean;
  condicionfisica?: boolean;
  usoseguridad?: boolean;

  // Estación de referencia
  codigoaeropuerto?: string;
  zonahoraria?: string;
}

export interface NotaAccidente {
  idnotaaccidentes: number;
  nota: string;
  tipo: boolean;
  fecha_actualizacion: string;
}

// --- NEW CATALOG INTERFACES ---
export interface Pais {
  idpais: number;
  pais: string;
}

export interface Estado {
  idestado: number;
  estado: string;
  pais: string;
}

export interface Condado {
  idcondado: number;
  condado: string;
  estado: string;
}

export interface Ciudad {
  idciudad: number;
  ciudad: string;
  condado: string;
}

export interface Calle {
  idcalle: number;
  calle: string;
  ciudad: string;
}

export interface Clima {
  idestadoclima: number;
  condicionclima: string;
  direccionviento: string;
  temperaturaf: number;
  sensaciontermicaf: number;
  humedadporcentaje: number;
  presionpulgadas: number;
  visibilidadmillas: number;
  velocidadvientomph: number;
  precipitacionpulgadas: number;
}

export interface ElementoFisico {
  idelementofisico: number;
  cercacruce: boolean;
  cercasemaforo: boolean;
  cercaparada: boolean;
  cercaestacion: boolean;
  cercabache: boolean;
  cercaviatren: boolean;
}

export interface PeriodoDia {
  idperiododia: number;
  amaneceranochecer: string;
  crepusculocivil: string;
  crepusculonautico: string;
  crepusculoastronomico: string;
}

export interface RegistroAccidentePayload {
  latitudinicio: number;
  longitudinicio: number;
  numvehiculos: number;
  numheridos: number;
  numfallecidos: number;
  descripcion: string;
  idseveridad_id?: number;
  
  // Location catalogs
  idpais_id: number;
  idestado_id: number;
  idcondado_id: number;
  idciudad_id: number;
  idcalle_id: number;
  
  // Environmental catalogs
  idperiododia_id: number;
  idestadoclima_id: number;
  idelementofisico_id: number;
  idtiporeportado_id: number;
  
  nota_inicial?: string;
  codigopostal?: string;

  // New detailed climate and environmental fields
  condicion_clima?: string;
  temperatura_f?: number;
  humedad_porcentaje?: number;
  visibilidad_millas?: number;
  velocidad_viento_mph?: number;

  cerca_cruce?: boolean;
  cerca_semaforo?: boolean;
  cerca_parada?: boolean;
  cerca_estacion?: boolean;
  cerca_bache?: boolean;
  cerca_viatren?: boolean;

  estadosobriedad?: boolean;
  nivelatencion?: boolean;
  condicionfisica?: boolean;
  usoseguridad?: boolean;

  amaneceranochecer?: string;
  crepusculocivil?: string;
  crepusculonautico?: string;
  crepusculoastronomico?: string;

  codigoaeropuerto?: string;
  zonahoraria?: string;
}

export interface ActualizarEstadoPayload {
  idtipoestadoincidente_id: number;
  nota?: string;
}

export interface DespachoPayload {
  unidades_ids: number[];
}
