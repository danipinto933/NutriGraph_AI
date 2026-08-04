import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { MetaService } from '../../core/services/meta.service';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="onboarding-container animate-fade-in">
      <div class="glass-panel onboarding-card">
        <h1 class="text-gradient">Perfil Biométrico</h1>
        <p class="subtitle">Calcularemos tu IMC y metabolismo basal.</p>
        
        <form [formGroup]="onboardingForm" (ngSubmit)="onSubmit()">
          
          <div class="form-row">
            <div class="form-group">
              <label>Sexo Biológico</label>
              <select formControlName="sex" class="input-glass">
                <option value="">Selecciona...</option>
                <option value="m">Hombre (m)</option>
                <option value="f">Mujer (f)</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Edad (años)
                <span class="error-text" *ngIf="onboardingForm.get('age_years')?.invalid && (onboardingForm.get('age_years')?.dirty || onboardingForm.get('age_years')?.touched)">
                  <ng-container *ngIf="onboardingForm.get('age_years')?.hasError('required')">Requerido</ng-container>
                  <ng-container *ngIf="onboardingForm.get('age_years')?.hasError('min')">Mínimo 18</ng-container>
                  <ng-container *ngIf="onboardingForm.get('age_years')?.hasError('max')">Máximo 110</ng-container>
                </span>
              </label>
              <input type="number" step="1" formControlName="age_years" class="input-glass" placeholder="Ej: 25" min="18" max="110" [class.input-error]="onboardingForm.get('age_years')?.invalid && (onboardingForm.get('age_years')?.dirty || onboardingForm.get('age_years')?.touched)">
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Peso (kg)
                <span class="error-text" *ngIf="onboardingForm.get('weight_kg')?.invalid && (onboardingForm.get('weight_kg')?.dirty || onboardingForm.get('weight_kg')?.touched)">
                  <ng-container *ngIf="onboardingForm.get('weight_kg')?.hasError('required')">Requerido</ng-container>
                  <ng-container *ngIf="onboardingForm.get('weight_kg')?.hasError('min')">Mínimo 30kg</ng-container>
                  <ng-container *ngIf="onboardingForm.get('weight_kg')?.hasError('max')">Máximo 300kg</ng-container>
                </span>
              </label>
              <input type="number" step="0.1" formControlName="weight_kg" class="input-glass" placeholder="Ej: 70.5" min="30" max="300" [class.input-error]="onboardingForm.get('weight_kg')?.invalid && (onboardingForm.get('weight_kg')?.dirty || onboardingForm.get('weight_kg')?.touched)">
            </div>
            
            <div class="form-group">
              <label>Altura (cm)
                <span class="error-text" *ngIf="onboardingForm.get('height_cm')?.invalid && (onboardingForm.get('height_cm')?.dirty || onboardingForm.get('height_cm')?.touched)">
                  <ng-container *ngIf="onboardingForm.get('height_cm')?.hasError('required')">Requerido</ng-container>
                  <ng-container *ngIf="onboardingForm.get('height_cm')?.hasError('min')">Mínimo 100cm</ng-container>
                  <ng-container *ngIf="onboardingForm.get('height_cm')?.hasError('max')">Máximo 250cm</ng-container>
                </span>
              </label>
              <input type="number" step="1" formControlName="height_cm" class="input-glass" placeholder="Ej: 175" min="100" max="250" [class.input-error]="onboardingForm.get('height_cm')?.invalid && (onboardingForm.get('height_cm')?.dirty || onboardingForm.get('height_cm')?.touched)">
            </div>
          </div>

          <div class="form-group">
            <label>Tipo de Dieta</label>
            <select formControlName="diet_type" class="input-glass">
              <option value="">Selecciona...</option>
              <option *ngFor="let diet of availableDiets" [value]="diet">{{ diet }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>Nivel de Actividad Física</label>
            <select formControlName="activity_factor" class="input-glass">
              <option value="1.2">Sedentario (Poco o ningún ejercicio)</option>
              <option value="1.375">Ligero (Ejercicio ligero 1-3 días a la semana)</option>
              <option value="1.55">Moderado (Ejercicio moderado 3-5 días a la semana)</option>
              <option value="1.725">Fuerte (Ejercicio fuerte 6-7 días a la semana)</option>
              <option value="1.9">Muy Fuerte (Entrenamiento muy duro)</option>
            </select>
          </div>

          <div class="form-group">
            <label>Alergias o Intolerancias (Opcional)</label>
            <div class="checkbox-group" formArrayName="intolerances" *ngIf="availableIntolerances.length > 0">
              <div *ngFor="let item of availableIntolerances; let i = index" class="checkbox-item">
                <input type="checkbox" [formControlName]="i" [id]="'intol-' + i">
                <label [for]="'intol-' + i">{{ item.label }}</label>
              </div>
            </div>
          </div>
          
          <button type="submit" class="btn-primary w-full" [disabled]="onboardingForm.invalid || authService.isLoading()">
            {{ authService.isLoading() ? 'Calculando...' : 'Guardar y Continuar' }}
          </button>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .onboarding-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 2rem 1rem;
      background: radial-gradient(circle at top left, rgba(0,210,255,0.1), transparent 40%),
                  radial-gradient(circle at bottom right, rgba(16,185,129,0.1), transparent 40%);
    }
    .onboarding-card {
      width: 100%;
      max-width: 550px;
      padding: 2.5rem;
    }
    .text-gradient {
      text-align: center;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      color: var(--text-secondary);
      margin-bottom: 2rem;
      font-size: 0.9rem;
      text-align: center;
    }
    .form-row {
      display: flex;
      gap: 1rem;
    }
    .form-row .form-group {
      flex: 1;
    }
    .form-group {
      margin-bottom: 1.5rem;
    }
    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      color: var(--text-secondary);
    }
    select.input-glass option {
      background-color: #111827; /* Fallback for var(--bg-dark) */
      color: #ffffff;
    }
    .checkbox-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.5rem;
      background: rgba(255,255,255,0.02);
      padding: 1rem;
      border-radius: var(--border-radius);
      border: 1px solid rgba(255,255,255,0.05);
    }
    .checkbox-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .checkbox-item label {
      margin: 0;
      cursor: pointer;
    }
    .w-full {
      width: 100%;
      margin-top: 1rem;
    }
  `]
})
export class OnboardingComponent {
  private fb = inject(FormBuilder);
  public authService = inject(AuthService);
  public metaService = inject(MetaService);
  private router = inject(Router);

  availableDiets: string[] = [];
  availableIntolerances: { id: string, label: string }[] = [];

  onboardingForm = this.fb.group({
    sex: ['', Validators.required],
    weight_kg: ['', [Validators.required, Validators.min(30), Validators.max(300)]],
    height_cm: ['', [Validators.required, Validators.min(100), Validators.max(250), Validators.pattern('^[0-9]+$')]],
    age_years: ['', [Validators.required, Validators.min(18), Validators.max(110), Validators.pattern('^[0-9]+$')]],
    activity_factor: ['1.2', Validators.required],
    diet_type: ['', Validators.required],
    intolerances: this.fb.array([])
  });

  ngOnInit() {
    this.metaService.getDiets().subscribe(diets => {
      this.availableDiets = diets;
    });
    
    this.metaService.getAllergens().subscribe(allergens => {
      this.availableIntolerances = allergens.map(a => ({ id: a, label: a }));
      const intolerancesFormArray = this.onboardingForm.get('intolerances') as FormArray;
      this.availableIntolerances.forEach(() => {
        intolerancesFormArray.push(this.fb.control(false));
      });
    });
  }

  onSubmit() {
    if (this.onboardingForm.valid) {
      const email = this.authService.currentUser()?.email;
      if (!email) {
        window.alert("Usuario no autenticado");
        return;
      }
      
      const formValue = this.onboardingForm.value as any;
      const selectedIntolerances = formValue.intolerances
        .map((checked: boolean, i: number) => checked ? this.availableIntolerances[i].id : null)
        .filter((v: string | null) => v !== null);

      const payload = {
        email: email,
        sex: formValue.sex,
        weight_kg: Number(formValue.weight_kg),
        height_cm: Number(formValue.height_cm),
        age_years: Number(formValue.age_years),
        activity_factor: Number(formValue.activity_factor),
        diet_type: formValue.diet_type,
        intolerances: selectedIntolerances
      };

      this.authService.submitOnboarding(payload).subscribe({
        next: () => {
          this.router.navigate(['/chat']);
        },
        error: () => {
          window.alert(this.authService.error() || "Error al guardar datos");
        }
      });
    }
  }
}
