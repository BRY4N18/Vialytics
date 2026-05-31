import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AccidenteService } from '../../../core/services/accidente.service';
import { firstValueFrom } from 'rxjs';

interface Expediente {
  accidente: any;
  evidencias: { fotos: any[] };
  clima: any;
  vehiculos: any[];
}

@Component({
  selector: 'app-expediente',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './expediente.html'
})
export class ExpedienteComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly accidenteService = inject(AccidenteService);

  readonly expediente = signal<Expediente | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  async ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.error.set('ID de accidente no proporcionado');
      this.loading.set(false);
      return;
    }

    try {
      const data = await firstValueFrom(
        this.accidenteService.getExpediente(id)
      );
      this.expediente.set(data);
    } catch (e) {
      this.error.set('Error al cargar el expediente');
    } finally {
      this.loading.set(false);
    }
  }
}
