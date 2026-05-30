import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login-modal.html',
  styleUrl: './login-modal.css'
})
export class LoginModalComponent {
  readonly authService = inject(AuthService);

  readonly username = signal<string>('');
  readonly password = signal<string>('');
  readonly showPassword = signal<boolean>(false);

  readonly loading = signal<boolean>(false);
  readonly errorMsg = signal<string | null>(null);

  readonly demoUsers = [
    { label: 'Operador', name: 'Laura Mendoza', user: 'operador_sga', role: 'Operador', color: 'emerald' },
    { label: 'Administrador', name: 'Carlos Gomez', user: 'admin_sga', role: 'Administrador', color: 'blue' },
    { label: 'Consumidor Analítico', name: 'Patricia Vega', user: 'analista_sga', role: 'Consumidor Analítico', color: 'teal' },
    { label: 'Despachador', name: 'David Torres', user: 'despachador_sga', role: 'Despachador', color: 'violet' }
  ];

  readonly selectedDemo = signal<any | null>(null);

  selectDemo(user: any): void {
    this.selectedDemo.set(user);
    this.username.set(user.user);
    this.password.set('sga_secure_pwd_2026');
    this.errorMsg.set(null);
  }

  toggleShowPassword(): void {
    this.showPassword.update(prev => !prev);
  }

  onClose(): void {
    this.authService.showLoginModal.set(false);
  }

  async onLogin(): Promise<void> {
    const userVal = this.username().trim();
    const pwdVal = this.password().trim();

    if (!userVal || !pwdVal) {
      this.errorMsg.set('Por favor, complete todos los campos de acceso.');
      return;
    }

    this.loading.set(true);
    this.errorMsg.set(null);

    try {
      await this.authService.login(userVal, pwdVal);
      this.loading.set(false);
    } catch {
      this.errorMsg.set('Acceso denegado. Credenciales inválidas.');
      this.loading.set(false);
    }
  }
}
