import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { DespachoPendiente, NotificacionDespacho } from '../models/despacho-pendiente.model';

@Injectable({ providedIn: 'root' })
export class DespachoService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  getDespachosPorUnidad(unidadId: number, soloPendientes: boolean = false): Observable<DespachoPendiente[]> {
    let params = new HttpParams();
    if (soloPendientes) {
      params = params.set('pendientes', 'true');
    }
    return this.http
      .get<DespachoPendiente[]>(`${this.baseUrl}/despachos/unidad/${unidadId}/`, { params })
      .pipe(catchError(this.handleError));
  }

  getNotificaciones(): Observable<NotificacionDespacho[]> {
    return this.http
      .get<NotificacionDespacho[]>(`${this.baseUrl}/notificaciones/`)
      .pipe(catchError(this.handleError));
  }

  aceptarNotificacion(notificacionId: number, unidadIds: number[]): Observable<any> {
    return this.http
      .post(`${this.baseUrl}/notificaciones/${notificacionId}/aceptar/`, {
        unidad_ids: unidadIds
      })
      .pipe(catchError(this.handleError));
  }

  marcarLlegada(despachoId: number): Observable<{ mensaje: string }> {
    return this.http
      .patch<{ mensaje: string }>(`${this.baseUrl}/despachos/${despachoId}/llegada/`, {})
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any): Observable<never> {
    console.error('DespachoService error:', error);
    const message =
      error?.error?.detail || error?.error?.error || error?.message || 'Error desconocido en el servidor';
    return throwError(() => new Error(message));
  }
}
