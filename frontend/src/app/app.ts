import { Component, signal, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './shared/components/header/header';
import { LoginModalComponent } from './shared/components/login-modal/login-modal';
import { AuthService } from './core/services/auth.service';
import { ToastService } from './core/services/toast.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HeaderComponent, LoginModalComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
  protected readonly authService = inject(AuthService);
  protected readonly toastService = inject(ToastService);
}
