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
          <div *ngIf="isUnverifiedError()" class="resend-box">
            <button type="button" class="btn-link" (click)="onResendVerification()">
              {{ resendMessage() || 'Reenviar correo de verificación' }}
            </button>
          </div>
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
      color: var(--error, #ef4444);
      padding: 0.75rem;
      border-radius: var(--border-radius-sm, 8px);
      margin-bottom: 1.5rem;
      border: 1px solid rgba(239, 68, 68, 0.2);
    }
    .resend-box {
      margin-top: 0.5rem;
      padding-top: 0.5rem;
      border-top: 1px dashed rgba(239, 68, 68, 0.3);
    }
    .btn-link {
      background: none;
      border: none;
      color: #00d2ff;
      text-decoration: underline;
      cursor: pointer;
      font-size: 0.85rem;
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

  public resendMessage = signal<string | null>(null);

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required]
  });

  isUnverifiedError(): boolean {
    const err = this.authService.error() || '';
    return err.toLowerCase().includes('verificar');
  }

  onResendVerification(): void {
    const email = this.loginForm.value.email;
    if (email) {
      this.authService.resendVerification(email).subscribe({
        next: (res: any) => {
          this.resendMessage.set(res?.message || 'Correo enviado');
        },
        error: (err) => {
          console.error('[LoginComponent] Error al reenviar correo:', err);
        }
      });
    }
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.resendMessage.set(null);
      this.authService.login(this.loginForm.value).subscribe({
        next: (res) => {
          if (res && res.access_token) {
            this.router.navigate(['/chat']);
          }
        },
        error: (err) => {
          console.error('[LoginComponent] Error en el intento de inicio de sesión:', err);
        }
      });
    }
  }
}
