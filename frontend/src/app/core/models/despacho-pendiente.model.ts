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

export interface DespachoPendiente {
  iddespacho: number;
  idaccidente: string;
  idunidademergencia: number;
  unidad_nombre: string;
  tipo_unidad: string;
  fechahoradespacho: string;
  fechahoraconfirmacion: string | null;
  fechahorallegada: string | null;
  accidente: AccidenteInfo;
}

export interface DespachoConfirmacionPayload {
  nota?: string;
}
