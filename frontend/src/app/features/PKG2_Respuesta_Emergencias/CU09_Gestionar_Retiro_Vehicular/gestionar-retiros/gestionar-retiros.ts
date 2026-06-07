import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { RouterModule } from '@angular/router';
import { ToastService } from '../../../../core/services/toast.service';

interface Retiro {
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

@Component({
  selector: 'app-gestionar-retiros',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './gestionar-retiros.html'
})
export class GestionarRetirosComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly toastService = inject(ToastService);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  readonly retiros = signal<Retiro[]>([]);
  readonly cargando = signal(false);
  readonly aceptandoId = signal<number | null>(null);
  readonly finalizandoId = signal<number | null>(null);
  readonly error = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarRetiros();
  }

  cargarRetiros(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.http.get<Retiro[]>(`${this.baseUrl}/retiros/`).subscribe({
      next: (data) => {
        this.retiros.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error al cargar retiros');
        this.cargando.set(false);
      }
    });
  }

  aceptarRetiro(retiroId: number): void {
    this.aceptandoId.set(retiroId);
    this.http.patch(`${this.baseUrl}/retiros/${retiroId}/aceptar/`, { nota: '' }).subscribe({
      next: (res: any) => {
        this.toastService.show(res.mensaje || 'Retiro aceptado exitosamente');
        this.aceptandoId.set(null);
        this.cargarRetiros();
      },
      error: (err) => {
        this.toastService.show(err.error?.error || 'Error al aceptar retiro');
        this.aceptandoId.set(null);
      }
    });
  }

  finalizarRetiro(retiroId: number): void {
    this.finalizandoId.set(retiroId);
    this.http.post(`${this.baseUrl}/retiros/${retiroId}/finalizar/`, {
      nota_informe: 'Retiro completado',
      urls_fotos: []
    }).subscribe({
      next: (res: any) => {
        this.toastService.show(res.mensaje || 'Retiro finalizado exitosamente');
        this.finalizandoId.set(null);
        this.cargarRetiros();
      },
      error: (err) => {
        this.toastService.show(err.error?.error || 'Error al finalizar retiro');
        this.finalizandoId.set(null);
      }
    });
  }

  formatoFecha(iso: string | null): string {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleString('es-EC');
    } catch {
      return iso;
    }
  }
}