import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { UnidadEmergencia, TipoUnidadCatalogoItem } from '../models/unidad-emergencia.model';

@Injectable({ providedIn: 'root' })
export class UnidadEmergenciaService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  getUnidades(filtros?: { tipo?: string; estado?: string; activo?: string; search?: string }): Observable<UnidadEmergencia[]> {
    let params = new HttpParams();
    if (filtros?.tipo) params = params.set('tipo', filtros.tipo);
    if (filtros?.estado) params = params.set('estado', filtros.estado);
    if (filtros?.activo) params = params.set('activo', filtros.activo);
    if (filtros?.search) params = params.set('search', filtros.search);
    return this.http
      .get<UnidadEmergencia[]>(`${this.baseUrl}/unidades/`, { params })
      .pipe(catchError(this.handleError));
  }

  getTiposUnidad(): Observable<TipoUnidadCatalogoItem[]> {
    return this.http
      .get<TipoUnidadCatalogoItem[]>(`${this.baseUrl}/tipos-unidad/`)
      .pipe(catchError(this.handleError));
  }

  crearUnidad(nombre: string, tipoId: number): Observable<UnidadEmergencia> {
    return this.http
      .post<UnidadEmergencia>(`${this.baseUrl}/unidades/`, {
        unidademergencia: nombre,
        tipounidad_id: tipoId,
      })
      .pipe(catchError(this.handleError));
  }

  actualizarUnidad(id: number, nombre: string, tipoId: number): Observable<UnidadEmergencia> {
    return this.http
      .put<UnidadEmergencia>(`${this.baseUrl}/unidades/${id}/`, {
        unidademergencia: nombre,
        tipounidad_id: tipoId,
      })
      .pipe(catchError(this.handleError));
  }

  toggleActivo(id: number, activo: boolean): Observable<UnidadEmergencia> {
    return this.http
      .patch<UnidadEmergencia>(`${this.baseUrl}/unidades/${id}/activar/`, { activo })
      .pipe(catchError(this.handleError));
  }

  getEstadosUnidad(): Observable<{idestadounidad: number; estadounidad: string}[]> {
    return this.http
      .get<{idestadounidad: number; estadounidad: string}[]>(`${this.baseUrl}/estados-unidad/`)
      .pipe(catchError(this.handleError));
  }

  actualizarEstadoUnidad(id: number, estado: string): Observable<UnidadEmergencia> {
    return this.http
      .patch<UnidadEmergencia>(`${this.baseUrl}/unidades/${id}/estado/`, { estadounidad: estado })
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any): Observable<never> {
    console.error('UnidadEmergenciaService error:', error);
    const message =
      error?.error?.detail || error?.message || 'Error desconocido en el servidor';
    return throwError(() => new Error(message));
  }
}
