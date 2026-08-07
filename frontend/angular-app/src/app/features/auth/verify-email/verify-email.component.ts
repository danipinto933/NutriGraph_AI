import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="auth-container animate-fade-in">
      <div class="glass-panel auth-card">
        
        <ng-container *ngIf="status() === 'verifying'">
          <div class="spinner"></div>
          <h1 class="text-gradient">Verificando tu cuenta...</h1>
          <p class="subtitle">Estamos procesando tu token de autorización mágica.</p>
        </ng-container>

        <ng-container *ngIf="status() === 'success'">
          <div class="icon success-icon">✓</div>
          <h1 class="text-gradient">¡Cuenta Verificada!</h1>
          <p class="subtitle">Tu correo ha sido confirmado correctamente. Redirigiendo...</p>
        </ng-container>

        <ng-container *ngIf="status() === 'error'">
          <div class="icon error-icon">✕</div>
          <h1 class="text-gradient">Verificación Fallida</h1>
          <p class="subtitle">{{ errorMessage() }}</p>

          <button class="btn-primary w-full" routerLink="/login">
            Ir a Iniciar Sesión
          </button>
        </ng-container>

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
      background: radial-gradient(circle at top left, rgba(0,210,255,0.1), transparent 40%),
                  radial-gradient(circle at bottom right, rgba(16,185,129,0.1), transparent 40%);
    }
    .auth-card {
      width: 100%;
      max-width: 450px;
      padding: 2.5rem;
      text-align: center;
    }
    .subtitle {
      color: var(--text-secondary, #cbd5e1);
      margin-bottom: 2rem;
      font-size: 0.95rem;
    }
    .icon {
      font-size: 3.5rem;
      margin-bottom: 1rem;
      line-height: 1;
    }
    .success-icon {
      color: #10b981;
    }
    .error-icon {
      color: #ef4444;
    }
    .spinner {
      width: 48px;
      height: 48px;
      margin: 0 auto 1.5rem auto;
      border: 4px solid rgba(0, 210, 255, 0.1);
      border-left-color: #00d2ff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .w-full {
      width: 100%;
      margin-top: 1rem;
    }
  `]
})
export class VerifyEmailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authService = inject(AuthService);

  public status = signal<'verifying' | 'success' | 'error'>('verifying');
  public errorMessage = signal<string>('El enlace de verificación no es válido o ha expirado.');

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.status.set('error');
      this.errorMessage.set('Falta el token de verificación en la URL.');
      return;
    }

    this.authService.verifyEmail(token).subscribe({
      next: () => {
        this.status.set('success');
        setTimeout(() => {
          this.router.navigate(['/onboarding']);
        }, 1500);
      },
      error: (err) => {
        this.status.set('error');
        this.errorMessage.set(err.error?.detail || 'El enlace de activación ha caducado o es inválido.');
      }
    });
  }
}
