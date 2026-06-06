import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { UnidadEmergencia } from '../models/unidad-emergencia.model';

@Injectable({ providedIn: 'root' })
export class UnidadEmergenciaService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  getUnidades(): Observable<UnidadEmergencia[]> {
    return this.http
      .get<UnidadEmergencia[]>(`${this.baseUrl}/unidades/`)
      .pipe(catchError(this.handleError));
  }

  crearUnidad(nombre: string, tipo: string): Observable<UnidadEmergencia> {
    return this.http
      .post<UnidadEmergencia>(`${this.baseUrl}/unidades/`, {
        unidademergencia: nombre,
        tipounidademergencia: tipo,
      })
      .pipe(catchError(this.handleError));
  }

  actualizarUnidad(id: number, nombre: string, tipo: string): Observable<UnidadEmergencia> {
    return this.http
      .put<UnidadEmergencia>(`${this.baseUrl}/unidades/${id}/`, {
        unidademergencia: nombre,
        tipounidademergencia: tipo,
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
      .patch<UnidadEmergencia>(`${this.baseUrl}/unidades/${id}/estado/`, { estado })
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any): Observable<never> {
    console.error('UnidadEmergenciaService error:', error);
    const message =
      error?.error?.detail || error?.message || 'Error desconocido en el servidor';
    return throwError(() => new Error(message));
  }
}
