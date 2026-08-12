import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="auth-container animate-fade-in">
      <div class="glass-panel auth-card">
        
        <!-- Registration Form View -->
        <ng-container *ngIf="!isRegistered()">
          <h1 class="text-gradient">Crear Cuenta</h1>
          <p class="subtitle">Únete a NutriGraph AI y descubre tu dieta ideal.</p>
          
          <div *ngIf="authService.error()" class="error-alert">
            {{ authService.error() }}
          </div>
          
          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
            <div class="form-group">
              <label for="first_name">Nombre Completo</label>
              <input 
                type="text" 
                id="first_name" 
                class="input-glass" 
                formControlName="first_name" 
                placeholder="Juan Pérez"
              >
              <div *ngIf="registerForm.get('first_name')?.touched && registerForm.get('first_name')?.invalid" class="validation-error">
                <small *ngIf="registerForm.get('first_name')?.errors?.['required']">El nombre es obligatorio.</small>
                <small *ngIf="registerForm.get('first_name')?.errors?.['minlength']">Mínimo 2 caracteres.</small>
                <small *ngIf="registerForm.get('first_name')?.errors?.['pattern']">No puede contener números ni símbolos.</small>
              </div>
            </div>

            <div class="form-group">
              <label for="email">Email</label>
              <input 
                type="email" 
                id="email" 
                class="input-glass" 
                formControlName="email" 
                placeholder="tu@email.com"
                autocomplete="email"
              >
              <div *ngIf="registerForm.get('email')?.touched && registerForm.get('email')?.invalid" class="validation-error">
                <small *ngIf="registerForm.get('email')?.errors?.['required']">El email es obligatorio.</small>
                <small *ngIf="registerForm.get('email')?.errors?.['email']">Formato de email inválido.</small>
              </div>
            </div>
            
            <div class="form-group">
              <label for="password">Contraseña</label>
              <input 
                type="password" 
                id="password" 
                class="input-glass" 
                formControlName="password" 
                placeholder="••••••••"
                autocomplete="new-password"
              >
              <div *ngIf="registerForm.get('password')?.touched && registerForm.get('password')?.invalid" class="validation-error">
                <small *ngIf="registerForm.get('password')?.errors?.['required']">La contraseña es obligatoria.</small>
                <small *ngIf="registerForm.get('password')?.errors?.['minlength']">Mínimo 8 caracteres.</small>
                <small *ngIf="registerForm.get('password')?.errors?.['maxlength']">Máximo 24 caracteres.</small>
                <small *ngIf="registerForm.get('password')?.errors?.['pattern']">Debe contener al menos una mayúscula y un número.</small>
              </div>
            </div>
            
            <button 
              type="submit" 
              class="btn-primary w-full" 
              [disabled]="registerForm.invalid || authService.isLoading()"
            >
              {{ authService.isLoading() ? 'Registrando...' : 'Registrarse' }}
            </button>
          </form>
          
          <p class="footer-text">
            ¿Ya tienes cuenta? <a routerLink="/login">Inicia sesión</a>
          </p>
        </ng-container>

        <!-- Verification Pending View -->
        <ng-container *ngIf="isRegistered()">
          <div class="email-icon">✉️</div>
          <h1 class="text-gradient">¡Verifica tu Correo!</h1>
          <p class="subtitle">
            Hemos enviado un enlace de doble autorización a <strong class="highlight-email">{{ maskedRegisteredEmail() }}</strong>.
          </p>
          
          <p class="info-text">
            Por favor, revisa tu bandeja de entrada (incluido la carpeta de spam) y haz clic en el enlace para activar tu cuenta y acceder a NutriGraph AI.
          </p>

          <div *ngIf="resendSuccess()" class="success-alert">
            {{ resendSuccess() }}
          </div>
          
          <div *ngIf="authService.error()" class="error-alert">
            {{ authService.error() }}
          </div>

          <button 
            type="button" 
            class="btn-secondary w-full" 
            (click)="onResend()" 
            [disabled]="authService.isLoading()"
          >
            {{ authService.isLoading() ? 'Enviando...' : 'Reenviar correo de verificación' }}
          </button>

          <p class="footer-text">
            <a routerLink="/login">Volver a iniciar sesión</a>
          </p>
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
      color: var(--text-secondary);
      margin-bottom: 1.5rem;
      font-size: 0.95rem;
      line-height: 1.5;
    }
    .info-text {
      color: var(--text-secondary);
      font-size: 0.85rem;
      margin-bottom: 1.5rem;
      line-height: 1.4;
    }
    .highlight-email {
      color: #00d2ff;
    }
    .email-icon {
      font-size: 3.5rem;
      margin-bottom: 1rem;
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
    .success-alert {
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;
      padding: 0.75rem;
      border-radius: var(--border-radius-sm, 8px);
      margin-bottom: 1.5rem;
      border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
      padding: 0.75rem 1.5rem;
      border-radius: var(--border-radius-sm, 8px);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .btn-secondary:hover:not(:disabled) {
      background: rgba(255, 255, 255, 0.1);
      border-color: #00d2ff;
    }
    .footer-text {
      margin-top: 2rem;
      font-size: 0.9rem;
      color: var(--text-secondary);
    }
    .validation-error {
      color: var(--error, #ef4444);
      font-size: 0.8rem;
      margin-top: 0.25rem;
      display: flex;
      flex-direction: column;
    }
  `]
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  public authService = inject(AuthService);
  private router = inject(Router);

  public isRegistered = signal<boolean>(false);
  public registeredEmail = signal<string>('');
  public resendSuccess = signal<string | null>(null);

  public maskedRegisteredEmail = computed(() => {
    const email = this.registeredEmail();
    if (!email || !email.includes('@')) return email;
    const [name, domain] = email.split('@');
    if (name.length <= 2) return `${name[0]}*@${domain}`;
    return `${name[0]}${'*'.repeat(name.length - 2)}${name[name.length - 1]}@${domain}`;
  });

  registerForm = this.fb.group({
    first_name: ['', [Validators.required, Validators.minLength(2), Validators.pattern('^[a-zA-ZñÑáéíóúÁÉÍÓÚ\\s]+$')]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(24), Validators.pattern('^(?=.*[A-Z])(?=.*[0-9]).*$')]]
  });

  onSubmit(): void {
    if (this.registerForm.valid) {
      const payload = { ...this.registerForm.value };
      const email = payload.email || '';
      // Limpiar la contraseña en texto plano del formulario inmediatamente tras la lectura
      this.registerForm.get('password')?.reset('');
      this.authService.register(payload).subscribe({
        next: () => {
          this.registeredEmail.set(email);
          this.isRegistered.set(true);
        }
      });
    }
  }

  onResend(): void {
    const email = this.registeredEmail();
    if (email) {
      this.resendSuccess.set(null);
      this.authService.resendVerification(email).subscribe({
        next: (res) => {
          this.resendSuccess.set(res.message || 'Correo reenviado correctamente');
        }
      });
    }
  }
}

