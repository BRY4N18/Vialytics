import { Component, signal, inject } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './shared/components/header/header';
import { LoginModalComponent } from './shared/components/login-modal/login-modal';
import { AuthService } from './core/services/auth.service';
import { ToastService } from './core/services/toast.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, HeaderComponent, LoginModalComponent],
  templateUrl: './app.html',
})
export class App {
  protected readonly title = signal('frontend');
  protected readonly authService = inject(AuthService);
  protected readonly toastService = inject(ToastService);
}
