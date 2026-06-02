import { Component, input, output, signal, effect, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AccidenteService } from '../../../../core/services/accidente.service';
import { AccidenteDetalle } from '../../../../core/models/accidente.model';
import { BadgeSeveridadComponent } from '../../../../shared/components/badge-severidad/badge-severidad';
import { AuthService } from '../../../../core/services/auth.service';

@Component({
  selector: 'app-panel-detalle',
  standalone: true,
  imports: [CommonModule, BadgeSeveridadComponent],
  templateUrl: './panel-detalle.html'
})
export class PanelDetalleComponent {
  accidenteId = input.required<string>();

  cerrar = output<void>();
  abrirDespacho = output<void>();
  abrirActualizarEstado = output<void>();

  private readonly accidenteService = inject(AccidenteService);
  readonly authService = inject(AuthService);

  readonly detalle = signal<AccidenteDetalle | null>(null);
  readonly cargando = signal(false);
  readonly error = signal<string | null>(null);

  constructor() {
    // Re-fetch details when accidentId input changes
    effect(() => {
      const id = this.accidenteId();
      if (id) {
        this.cargarDetalle(id);
      }
    });
  }

  cargarDetalle(id: string): void {
    this.cargando.set(true);
    this.error.set(null);

    this.accidenteService.getAccidenteDetalle(id).subscribe({
      next: (data) => {
        this.detalle.set(data);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err.message || 'Error al obtener el detalle del accidente');
        this.cargando.set(false);
      }
    });
  }

  onCerrar(): void {
    this.cerrar.emit();
  }

  onDespachar(): void {
    this.abrirDespacho.emit();
  }

  onActualizarEstado(): void {
    this.abrirActualizarEstado.emit();
  }

  readonly estadoLabels: Record<string, string> = {
    ACTIVO: 'Reportado',
    EN_ATENCION: 'En Atención',
    EN_TRASLADO: 'En Traslado',
    CONTROLADO: 'Despejado',
    ARCHIVADO: 'Archivado'
  };

  getEstadoLabel(estado: string): string {
    return this.estadoLabels[estado] || estado;
  }

  getEstadoClass(estado: string): string {
    const map: Record<string, string> = {
      ACTIVO: 'activo',
      EN_ATENCION: 'en-atencion',
      EN_TRASLADO: 'en-atencion',
      CONTROLADO: 'controlado',
      ARCHIVADO: 'archivado'
    };
    return map[estado] || '';
  }

  formatFecha(isoString?: string): string {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      return date.toLocaleString('es-EC', {
        dateStyle: 'medium',
        timeStyle: 'short'
      });
    } catch {
      return isoString;
    }
  }
}
