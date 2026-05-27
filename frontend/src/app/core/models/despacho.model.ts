export interface DespachoModel {
  iddespacho: number;
  accidente_id: string;
  unidad_nombre: string;
  tipo: string;
  fechahoradespacho: string;
  fechahorallegada?: string;
}
