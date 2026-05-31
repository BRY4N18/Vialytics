import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-layout-analitico',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './layout-analitico.html'
})
export class LayoutAnaliticoComponent {
  readonly authService = inject(AuthService);
}
