import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Retiro, SolicitarRetiroPayload, AceptarRetiroPayload, FinalizarRetiroPayload } from '../models/retiro.model';

@Injectable({
  providedIn: 'root'
})
export class RetiroService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  getRetiros(): Observable<Retiro[]> {
    return this.http.get<Retiro[]>(`${this.baseUrl}/retiros/`);
  }

  solicitarRetiro(payload: SolicitarRetiroPayload): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/retiros/solicitar/`, payload);
  }

  aceptarRetiro(retiroId: number, payload: AceptarRetiroPayload): Observable<any> {
    return this.http.patch<any>(`${this.baseUrl}/retiros/${retiroId}/aceptar/`, payload);
  }

  finalizarRetiro(retiroId: number, payload: FinalizarRetiroPayload): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/retiros/${retiroId}/finalizar/`, payload);
  }
}
