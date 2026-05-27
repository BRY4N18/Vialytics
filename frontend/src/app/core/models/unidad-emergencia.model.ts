export type TipoUnidad = 'AMBULANCIA' | 'POLICIA' | 'GRUA' | 'BOMBEROS';

export type EstadoUnidad =
  | 'EN_BASE'
  | 'EN_CAMINO'
  | 'EN_ESCENA'
  | 'EN_TRASLADO'
  | 'REGRESO'
  | 'DISPONIBLE';

export interface UnidadEmergencia {
  idunidademergencia: number;
  unidademergencia: string;
  tipounidademergencia: TipoUnidad;
  estadounidad: EstadoUnidad;
  activo: boolean;
}
