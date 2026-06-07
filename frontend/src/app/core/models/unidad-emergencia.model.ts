export type TipoUnidad = string;

export type EstadoUnidad =
  | 'En base'
  | 'En camino'
  | 'En escena'
  | 'En traslado'
  | 'Regreso'
  | 'Disponible';

export interface TipoUnidadCatalogoItem {
  idtipounidad: number;
  tipounidad: TipoUnidad;
}

export interface UnidadEmergencia {
  idunidademergencia: number;
  unidademergencia: string;
  tipounidademergencia: TipoUnidad;
  estadounidad: EstadoUnidad;
  activo: boolean;
}
