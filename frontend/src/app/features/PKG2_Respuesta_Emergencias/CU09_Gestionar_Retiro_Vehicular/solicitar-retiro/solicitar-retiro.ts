import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { ToastService } from '../../../../core/services/toast.service';
import { UnidadEmergenciaService } from '../../../../core/services/unidad-emergencia.service';
import { UnidadEmergencia } from '../../../../core/models/unidad-emergencia.model';

@Component({
  selector: 'app-solicitar-retiro',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './solicitar-retiro.html'
})
export class SolicitarRetiroComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly unidadEmergenciaService = inject(UnidadEmergenciaService);
  private readonly toastService = inject(ToastService);
  private readonly baseUrl = 'http://localhost:8080/api/v1';

  readonly unidadesGrua = signal<UnidadEmergencia[]>([]);
  readonly cargando = signal(false);
  readonly enviando = signal(false);
  readonly error = signal<string | null>(null);

  readonly idaccidente = signal('');
  readonly idunidad = signal<number | null>(null);
  readonly descripcion = signal('');

  ngOnInit(): void {
    this.cargarUnidadesGrua();
  }

  cargarUnidadesGrua(): void {
    this.cargando.set(true);
    this.unidadEmergenciaService.getUnidades({ tipo: 'GRUA', activo: 'true' }).subscribe({
      next: (data) => {
        this.unidadesGrua.set(data);
        this.cargando.set(false);
      },
      error: () => this.cargando.set(false)
    });
  }

  onUnidadChange(value: string): void {
    this.idunidad.set(value ? parseInt(value, 10) : null);
  }

  solicitar(): void {
    const idAcc = this.idaccidente().trim();
    const idUnidad = this.idunidad();
    if (!idAcc || !idUnidad) return;

    this.enviando.set(true);
    this.error.set(null);

    this.http.post(`${this.baseUrl}/retiros/solicitar/`, {
      idaccidente: idAcc,
      idunidademergencia: idUnidad,
      descripcion: this.descripcion().trim()
    }).subscribe({
      next: () => {
        this.toastService.show('Retiro solicitado exitosamente');
        this.enviando.set(false);
        this.idaccidente.set('');
        this.idunidad.set(null);
        this.descripcion.set('');
      },
      error: (err) => {
        this.error.set(err.error?.error || err.message || 'Error al solicitar retiro');
        this.enviando.set(false);
      }
    });
  }
}