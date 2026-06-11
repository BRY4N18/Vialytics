import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ToastService } from '../../../../core/services/toast.service';
import { RetiroService } from '../../../../core/services/retiro.service';
import { Retiro } from '../../../../core/models/retiro.model';

@Component({
  selector: 'app-gestionar-retiros',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './gestionar-retiros.html'
})
export class GestionarRetirosComponent implements OnInit {
  private readonly retiroService = inject(RetiroService);
  private readonly toastService = inject(ToastService);

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
    this.retiroService.getRetiros().subscribe({
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
    this.retiroService.aceptarRetiro(retiroId, { nota: '' }).subscribe({
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
    this.retiroService.finalizarRetiro(retiroId, {
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