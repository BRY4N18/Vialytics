export interface AccidenteInfo {
  idaccidente: string;
  latitudinicio?: number;
  longitudinicio?: number;
  numheridos: number;
  numfallecidos: number;
  descripcion: string;
  severidad_nivel?: number;
  estado_actual: string;
  calle_nombre: string;
  ciudad_nombre: string;
}

export interface Vehiculo {
  tipovehiculo: string;
  modelovehiculo: string;
  mercanciapeligrosa: boolean;
}

export interface DespachoPendiente {
  iddespacho: number;
  idaccidente: string;
  idunidademergencia: number;
  unidad_nombre: string;
  tipo_unidad: string;
  fechahoradespacho: string;
  fechahorallegada: string | null;
  accidente: AccidenteInfo;
  vehiculos: Vehiculo[];
}

export interface NotificacionDespacho {
  idnotificaciondespacho: number;
  idaccidente: string;
  numheridos: number;
  numvehiculos: number;
  tipos_necesarios: string[];
  fecha_actualizacion: string;
  accidente: AccidenteInfo;
  vehiculos: Vehiculo[];
}
