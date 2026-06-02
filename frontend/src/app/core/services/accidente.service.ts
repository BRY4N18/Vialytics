import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, catchError, throwError, map } from 'rxjs';
import {
  AccidenteMapa,
  AccidenteDetalle,
  RegistroAccidentePayload,
  ActualizarEstadoPayload,
  DespachoPayload,
  ExpedienteAccidente,
  Severidad,
  TipoReportado,
  TipoEstadoIncidente,
  Pais,
  Estado,
  Condado,
  Ciudad,
  Calle,
  Clima,
  ElementoFisico,
  PeriodoDia,
} from '../models/accidente.model';

@Injectable({ providedIn: 'root' })
export class AccidenteService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  registrarAccidente(payload: RegistroAccidentePayload): Observable<AccidenteMapa> {
    return this.http
      .post<AccidenteMapa>(`${this.baseUrl}/accidentes/`, payload)
      .pipe(catchError(this.handleError));
  }

  actualizarAccidente(id: string, payload: RegistroAccidentePayload): Observable<AccidenteMapa> {
    return this.http
      .put<AccidenteMapa>(`${this.baseUrl}/accidentes/${id}/`, payload)
      .pipe(catchError(this.handleError));
  }

  getAccidentesPaginados(filtros: { 
    page: number; 
    page_size: number; 
    search?: string; 
    severidad?: number; 
    estado?: string; 
    solo_activos?: boolean; 
    ciudad_id?: number;
    fecha_desde?: string;
    fecha_hasta?: string;
    min_heridos?: number;
    max_heridos?: number;
    min_fallecidos?: number;
    max_fallecidos?: number;
    matricula?: string;
  }): Observable<{ total_records: number; page: number; page_size: number; results: AccidenteMapa[] }> {
    let params = new HttpParams()
      .set('page', filtros.page.toString())
      .set('page_size', filtros.page_size.toString());

    if (filtros.search) {
      params = params.set('search', filtros.search);
    }
    if (filtros.severidad !== undefined && filtros.severidad !== null) {
      params = params.set('severidad', filtros.severidad.toString());
    }
    if (filtros.estado) {
      params = params.set('estado', filtros.estado);
    }
    if (filtros.solo_activos !== undefined) {
      params = params.set('solo_activos', filtros.solo_activos.toString());
    }
    if (filtros.ciudad_id !== undefined && filtros.ciudad_id !== null) {
      params = params.set('ciudad_id', filtros.ciudad_id.toString());
    }
    if (filtros.fecha_desde) {
      params = params.set('fecha_desde', filtros.fecha_desde);
    }
    if (filtros.fecha_hasta) {
      params = params.set('fecha_hasta', filtros.fecha_hasta);
    }
    if (filtros.min_heridos !== undefined && filtros.min_heridos !== null) {
      params = params.set('min_heridos', filtros.min_heridos.toString());
    }
    if (filtros.max_heridos !== undefined && filtros.max_heridos !== null) {
      params = params.set('max_heridos', filtros.max_heridos.toString());
    }
    if (filtros.min_fallecidos !== undefined && filtros.min_fallecidos !== null) {
      params = params.set('min_fallecidos', filtros.min_fallecidos.toString());
    }
    if (filtros.max_fallecidos !== undefined && filtros.max_fallecidos !== null) {
      params = params.set('max_fallecidos', filtros.max_fallecidos.toString());
    }
    if (filtros.matricula) {
      params = params.set('matricula', filtros.matricula);
    }

    return this.http
      .get<{ total_records: number; page: number; page_size: number; results: AccidenteMapa[] }>(`${this.baseUrl}/accidentes/buscar/`, { params })
      .pipe(catchError(this.handleError));
  }

  getAccidentesMapa(filtros?: { 
    severidad?: number; 
    estado?: string; 
    solo_activos?: boolean; 
    solo_ultima_semana?: boolean;
    fecha_inicio?: string;
    fecha_fin?: string;
    public?: boolean;
    idpais?: string;
    idestado?: string;
    idcondado?: string;
    idciudad?: string;
    idcalle?: string;
  }): Observable<AccidenteMapa[]> {
    let params = new HttpParams();
    if (filtros?.severidad) {
      params = params.set('severidad', filtros.severidad.toString());
    }
    if (filtros?.estado) {
      params = params.set('estado', filtros.estado);
    }
    if (filtros?.solo_activos !== undefined) {
      params = params.set('solo_activos', filtros.solo_activos.toString());
    }
    if (filtros?.solo_ultima_semana !== undefined) {
      params = params.set('solo_ultima_semana', filtros.solo_ultima_semana.toString());
    }
    if (filtros?.fecha_inicio) {
      params = params.set('fecha_inicio', filtros.fecha_inicio);
    }
    if (filtros?.fecha_fin) {
      params = params.set('fecha_fin', filtros.fecha_fin);
    }
    if (filtros?.public !== undefined) {
      params = params.set('public', filtros.public.toString());
    }
    if (filtros?.idpais) {
      params = params.set('idpais', filtros.idpais);
    }
    if (filtros?.idestado) {
      params = params.set('idestado', filtros.idestado);
    }
    if (filtros?.idcondado) {
      params = params.set('idcondado', filtros.idcondado);
    }
    if (filtros?.idciudad) {
      params = params.set('idciudad', filtros.idciudad);
    }
    if (filtros?.idcalle) {
      params = params.set('idcalle', filtros.idcalle);
    }
    return this.http
      .get<AccidenteMapa[]>(`${this.baseUrl}/accidentes/mapa/`, { params })
      .pipe(catchError(this.handleError));
  }

  getMapaPublico(filtros?: {
    severidad?: number;
    horas?: number;
    fecha_inicio?: string;
    fecha_fin?: string;
    idpais?: string;
    idestado?: string;
    idcondado?: string;
    idciudad?: string;
    idcalle?: string;
  }): Observable<AccidenteMapa[]> {
    let params = new HttpParams();
    if (filtros?.severidad) {
      params = params.set('severidad', filtros.severidad.toString());
    }
    if (filtros?.horas) {
      params = params.set('horas', filtros.horas.toString());
    }
    if (filtros?.fecha_inicio) {
      params = params.set('fecha_inicio', filtros.fecha_inicio);
    }
    if (filtros?.fecha_fin) {
      params = params.set('fecha_fin', filtros.fecha_fin);
    }
    if (filtros?.idpais) {
      params = params.set('idpais', filtros.idpais);
    }
    if (filtros?.idestado) {
      params = params.set('idestado', filtros.idestado);
    }
    if (filtros?.idcondado) {
      params = params.set('idcondado', filtros.idcondado);
    }
    if (filtros?.idciudad) {
      params = params.set('idciudad', filtros.idciudad);
    }
    if (filtros?.idcalle) {
      params = params.set('idcalle', filtros.idcalle);
    }
    return this.http
      .get<AccidenteMapa[]>(`${this.baseUrl}/public/mapa/`, { params })
      .pipe(catchError(this.handleError));
  }

  getAccidenteDetalle(id: string): Observable<AccidenteDetalle> {
    return this.http
      .get<AccidenteDetalle>(`${this.baseUrl}/accidentes/${id}/`)
      .pipe(catchError(this.handleError));
  }

  getExpediente(id: string): Observable<ExpedienteAccidente> {
    return this.http
      .get<ExpedienteAccidente>(`${this.baseUrl}/accidentes/${id}/expediente/`)
      .pipe(catchError(this.handleError));
  }

  actualizarEstado(id: string, payload: ActualizarEstadoPayload): Observable<AccidenteMapa> {
    return this.http
      .patch<AccidenteMapa>(`${this.baseUrl}/accidentes/${id}/estado/`, payload)
      .pipe(catchError(this.handleError));
  }

  despacharUnidades(id: string, payload: DespachoPayload): Observable<any> {
    return this.http
      .post<any>(`${this.baseUrl}/accidentes/${id}/despachos/`, payload)
      .pipe(catchError(this.handleError));
  }

  getTiposReportado(): Observable<TipoReportado[]> {
    return this.http
      .get<TipoReportado[]>(`${this.baseUrl}/tipos-reportado/`)
      .pipe(catchError(this.handleError));
  }

  getSeveridades(): Observable<Severidad[]> {
    return this.http
      .get<Severidad[]>(`${this.baseUrl}/severidades/`)
      .pipe(catchError(this.handleError));
  }

  getTiposEstado(): Observable<TipoEstadoIncidente[]> {
    return this.http
      .get<TipoEstadoIncidente[]>(`${this.baseUrl}/tipos-estado/`)
      .pipe(catchError(this.handleError));
  }

  // --- NEW CATALOG SERVICES ---
  getPaises(): Observable<Pais[]> {
    return this.http
      .get<Pais[]>(`${this.baseUrl}/paises/`)
      .pipe(
        map(arr => arr.filter(item => item.pais !== 'Ubicación Registrada')),
        catchError(this.handleError)
      );
  }

  getEstados(pais?: string): Observable<Estado[]> {
    let params = new HttpParams();
    if (pais) {
      params = params.set('pais', pais);
    }
    return this.http
      .get<Estado[]>(`${this.baseUrl}/estados/`, { params })
      .pipe(
        map(arr => arr.filter(item => item.estado !== 'Ubicación Registrada')),
        catchError(this.handleError)
      );
  }

  getCondados(estado?: string): Observable<Condado[]> {
    let params = new HttpParams();
    if (estado) {
      params = params.set('estado', estado);
    }
    return this.http
      .get<Condado[]>(`${this.baseUrl}/condados/`, { params })
      .pipe(
        map(arr => arr.filter(item => item.condado !== 'Ubicación Registrada')),
        catchError(this.handleError)
      );
  }

  getCiudades(condado?: string): Observable<Ciudad[]> {
    let params = new HttpParams();
    if (condado) {
      params = params.set('condado', condado);
    }
    return this.http
      .get<Ciudad[]>(`${this.baseUrl}/ciudades/`, { params })
      .pipe(
        map(arr => arr.filter(item => item.ciudad !== 'Ubicación Registrada')),
        catchError(this.handleError)
      );
  }

  getCalles(ciudad?: string): Observable<Calle[]> {
    let params = new HttpParams();
    if (ciudad) {
      params = params.set('ciudad', ciudad);
    }
    return this.http
      .get<Calle[]>(`${this.baseUrl}/calles/`, { params })
      .pipe(
        map(arr => arr.filter(item => item.calle !== 'Ubicación Registrada')),
        catchError(this.handleError)
      );
  }

  getClimas(): Observable<Clima[]> {
    return this.http
      .get<Clima[]>(`${this.baseUrl}/climas/`)
      .pipe(catchError(this.handleError));
  }

  getElementosFisicos(): Observable<ElementoFisico[]> {
    return this.http
      .get<ElementoFisico[]>(`${this.baseUrl}/elementos-fisicos/`)
      .pipe(catchError(this.handleError));
  }

  getPeriodosDias(): Observable<PeriodoDia[]> {
    return this.http
      .get<PeriodoDia[]>(`${this.baseUrl}/periodos-dias/`)
      .pipe(catchError(this.handleError));
  }

  getDashboardStats(): Observable<any> {
    return this.http
      .get<any>(`${this.baseUrl}/accidentes/dashboard/`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any): Observable<never> {
    console.error('AccidenteService error:', error);
    const message =
      error?.error?.detail || error?.message || 'Error desconocido en el servidor';
    return throwError(() => new Error(message));
  }
}
