import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-badge-severidad',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './badge-severidad.html',
  styleUrl: './badge-severidad.css',
})
export class BadgeSeveridadComponent {
  severidad = input.required<number>();

  readonly config = computed(() => {
    const s = this.severidad();
    switch (s) {
      case 1:
        return { label: 'Leve', cssClass: 'badge-leve', icon: '🟢' };
      case 2:
        return { label: 'Moderado', cssClass: 'badge-moderado', icon: '🟡' };
      case 3:
        return { label: 'Grave', cssClass: 'badge-grave', icon: '🔴' };
      case 4:
        return { label: 'Fatal', cssClass: 'badge-fatal', icon: '🟣' };
      default:
        return { label: 'Sin clasificar', cssClass: 'badge-default', icon: '⚪' };
    }
  });
}
