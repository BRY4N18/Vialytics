import { Component, inject, signal, effect, OnDestroy } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './header.html'
})
export class HeaderComponent implements OnDestroy {
  readonly authService = inject(AuthService);

  readonly formattedTime = signal('00:00:00');
  readonly formattedDate = signal('');

  private timerId: ReturnType<typeof setInterval>;

  constructor() {
    this.updateClock();
    this.timerId = setInterval(() => this.updateClock(), 1000);
  }

  ngOnDestroy(): void {
    clearInterval(this.timerId);
  }

  private updateClock(): void {
    const now = new Date();
    this.formattedTime.set(now.toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    this.formattedDate.set(now.toLocaleDateString('es-EC', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }));
  }
}
