import { Component, inject } from '@angular/core';
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
    .validation-error {
      color: var(--error);
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

  registerForm = this.fb.group({
    first_name: ['', [Validators.required, Validators.minLength(2), Validators.pattern('^[a-zA-ZñÑáéíóúÁÉÍÓÚ\\s]+$')]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8), Validators.maxLength(24), Validators.pattern('^(?=.*[A-Z])(?=.*[0-9]).*$')]]
  });

  constructor() {}

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.authService.register(this.registerForm.value).subscribe({
        next: () => {
          // Auto login after register
          const credentials = {
            email: this.registerForm.value.email,
            password: this.registerForm.value.password
          };
          this.authService.login(credentials).subscribe({
            next: () => this.router.navigate(['/onboarding'])
          });
        }
      });
    }
  }
}
