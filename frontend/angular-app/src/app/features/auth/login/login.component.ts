import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-container animate-fade-in">
      <div class="glass-panel auth-card">
        <h1 class="text-gradient">Bienvenido a NutriGraph AI</h1>
        <p class="subtitle">Inicia sesión para continuar tu viaje nutricional.</p>
        
        <div *ngIf="authService.error()" class="error-alert">
          {{ authService.error() }}
        </div>
        
        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              class="input-glass" 
              formControlName="email" 
              placeholder="tu@email.com"
            >
          </div>
          
          <div class="form-group">
            <label for="password">Contraseña</label>
            <input 
              type="password" 
              id="password" 
              class="input-glass" 
              formControlName="password" 
              placeholder="••••••••"
            >
          </div>
          
          <button 
            type="submit" 
            class="btn-primary w-full" 
            [disabled]="loginForm.invalid || authService.isLoading()"
          >
            {{ authService.isLoading() ? 'Cargando...' : 'Entrar' }}
          </button>
        </form>
        
        <p class="footer-text">
          ¿No tienes cuenta? <a routerLink="/register">Regístrate aquí</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .auth-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 1rem;
      background: radial-gradient(circle at top right, rgba(0,210,255,0.1), transparent 40%),
                  radial-gradient(circle at bottom left, rgba(58,123,213,0.1), transparent 40%);
    }
    .auth-card {
      width: 100%;
      max-width: 400px;
      padding: 2.5rem;
      text-align: center;
    }
    .subtitle {
      color: var(--text-secondary);
      margin-bottom: 2rem;
      font-size: 0.9rem;
    }
    .form-group {
      text-align: left;
      margin-bottom: 1.5rem;
    }
    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      color: var(--text-secondary);
    }
    .w-full {
      width: 100%;
      margin-top: 1rem;
    }
    .error-alert {
      background: rgba(239, 68, 68, 0.1);
      color: var(--error);
      padding: 0.75rem;
      border-radius: var(--border-radius-sm);
      margin-bottom: 1.5rem;
      border: 1px solid rgba(239, 68, 68, 0.2);
    }
    .footer-text {
      margin-top: 2rem;
      font-size: 0.9rem;
      color: var(--text-secondary);
    }
  `]
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  public authService = inject(AuthService);
  private router = inject(Router);

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required]
  });

  constructor() {}

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.authService.login(this.loginForm.value).subscribe({
        next: () => this.router.navigate(['/chat'])
      });
    }
  }
}
