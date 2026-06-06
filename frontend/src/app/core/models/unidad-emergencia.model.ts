export type TipoUnidad = 'AMBULANCIA' | 'BOMBEROS' | 'TRANSITO' | 'GRUA';

export type EstadoUnidad =
  | 'En base'
  | 'En camino'
  | 'En escena'
  | 'En traslado'
  | 'Regreso'
  | 'Disponible';

export interface UnidadEmergencia {
  idunidademergencia: number;
  unidademergencia: string;
  tipounidademergencia: TipoUnidad;
  estadounidad: EstadoUnidad;
  activo: boolean;
}
