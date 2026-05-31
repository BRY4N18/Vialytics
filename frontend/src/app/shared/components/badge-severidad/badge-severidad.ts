import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-badge-severidad',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './badge-severidad.html',
})
export class BadgeSeveridadComponent {
  severidad = input.required<number>();

  readonly config = computed(() => {
    const base = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase animate-badge-bounce';
    const s = this.severidad();
    switch (s) {
      case 1:
        return { label: 'Leve', twClass: `${base} bg-sev-leve/10 text-sev-leve`, icon: '🟢' };
      case 2:
        return { label: 'Moderado', twClass: `${base} bg-sev-moderada/10 text-sev-moderada`, icon: '🟡' };
      case 3:
        return { label: 'Grave', twClass: `${base} bg-sev-grave/10 text-sev-grave`, icon: '🔴' };
      case 4:
        return { label: 'Fatal', twClass: `${base} bg-sev-fatal/10 text-sev-fatal animate-fatal-pulse`, icon: '🟣' };
      default:
        return { label: 'Sin clasificar', twClass: `${base} bg-gray-100 text-text-muted`, icon: '⚪' };
    }
  });
}
