export interface Retiro {
  idretiro: number;
  idaccidente: string;
  idunidademergencia: number;
  unidademergencia_nombre: string;
  estado: string;
  descripcion: string;
  nota_informe: string;
  urls_fotos: string[];
  fecha_solicitud: string;
  fecha_aceptacion: string | null;
  fecha_finalizacion: string | null;
}

export interface SolicitarRetiroPayload {
  idaccidente: string;
  idunidademergencia: number;
  descripcion: string;
}

export interface AceptarRetiroPayload {
  nota: string;
}

export interface FinalizarRetiroPayload {
  nota_informe: string;
  urls_fotos: string[];
}
