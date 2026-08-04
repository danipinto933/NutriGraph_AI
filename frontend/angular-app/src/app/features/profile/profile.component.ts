import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { MetaService } from '../../core/services/meta.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="dashboard-layout animate-fade-in">
      <!-- Sidebar -->
      <aside class="sidebar glass-panel">
        <div class="brand">
          <h2 class="text-gradient">NutriGraph AI</h2>
        </div>

        <nav class="nav-menu">
          <button class="nav-item" (click)="router.navigate(['/chat'])">Volver al chat</button>
          <button class="nav-item active">Perfil Médico</button>
          <button *ngIf="authService.isAdmin()" class="nav-item" style="color: var(--warning)" (click)="router.navigate(['/admin'])">Panel de Administrador</button>
          <button class="nav-item text-error" (click)="logout()">Cerrar Sesión</button>
        </nav>
      </aside>

      <!-- Main Profile Area -->
      <main class="chat-main" style="padding-left: 2rem; overflow-y: auto;">
        <div class="glass-panel profile-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <div>
              <h2 class="text-gradient" style="margin:0;">Tu Perfil Nutricional</h2>
              <p class="subtitle" style="margin-top:0.5rem; color: var(--text-secondary);">Actualiza tus métricas biométricas e intolerancias.</p>
            </div>
            
            <div *ngIf="authService.currentUser()?.bmi" class="metrics-badge">
              <div class="metric" [ngClass]="getBmiClass(authService.currentUser()?.bmi)"><span>IMC</span> {{ authService.currentUser()?.bmi | number:'1.1-1' }}</div>
              <div class="metric"><span>TMB</span> {{ authService.currentUser()?.bmr | number:'1.0-0' }} kcal</div>
            </div>
          </div>

          <div *ngIf="authService.error()" class="error-alert">
            {{ authService.error() }}
          </div>
          


          <form [formGroup]="profileForm" (ngSubmit)="onSubmit()">
            <div class="form-row">
              <div class="form-group">
                <label>Nombre
                  <span class="error-text" *ngIf="profileForm.get('first_name')?.invalid && (profileForm.get('first_name')?.dirty || profileForm.get('first_name')?.touched)">Requerido</span>
                </label>
                <input type="text" formControlName="first_name" class="input-glass" [class.input-error]="profileForm.get('first_name')?.invalid && (profileForm.get('first_name')?.dirty || profileForm.get('first_name')?.touched)">
              </div>
              <div class="form-group">
                <label>Email
                  <span class="error-text" *ngIf="profileForm.get('email')?.invalid && (profileForm.get('email')?.dirty || profileForm.get('email')?.touched)">
                    <ng-container *ngIf="profileForm.get('email')?.hasError('required')">Requerido</ng-container>
                    <ng-container *ngIf="profileForm.get('email')?.hasError('email')">Email inválido</ng-container>
                  </span>
                </label>
                <input type="email" formControlName="email" class="input-glass" [class.input-error]="profileForm.get('email')?.invalid && (profileForm.get('email')?.dirty || profileForm.get('email')?.touched)">
              </div>
            </div>

            <h3 style="margin-top: 1rem; margin-bottom: 1rem; border-bottom: 1px solid var(--border-light); padding-bottom: 0.5rem;">Datos Biométricos</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label>Sexo Biológico</label>
                <select formControlName="sex" class="input-glass">
                  <option value="m">Hombre (m)</option>
                  <option value="f">Mujer (f)</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Edad (años)
                  <span class="error-text" *ngIf="profileForm.get('age_years')?.invalid && (profileForm.get('age_years')?.dirty || profileForm.get('age_years')?.touched)">
                    <ng-container *ngIf="profileForm.get('age_years')?.hasError('required')">Requerido</ng-container>
                    <ng-container *ngIf="profileForm.get('age_years')?.hasError('min')">Mínimo 18</ng-container>
                    <ng-container *ngIf="profileForm.get('age_years')?.hasError('max')">Máximo 110</ng-container>
                  </span>
                </label>
                <input type="number" step="1" formControlName="age_years" class="input-glass" min="18" max="110" [class.input-error]="profileForm.get('age_years')?.invalid && (profileForm.get('age_years')?.dirty || profileForm.get('age_years')?.touched)">
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label>Peso (kg)
                  <span class="error-text" *ngIf="profileForm.get('weight_kg')?.invalid && (profileForm.get('weight_kg')?.dirty || profileForm.get('weight_kg')?.touched)">
                    <ng-container *ngIf="profileForm.get('weight_kg')?.hasError('required')">Requerido</ng-container>
                    <ng-container *ngIf="profileForm.get('weight_kg')?.hasError('min')">Mínimo 30kg</ng-container>
                    <ng-container *ngIf="profileForm.get('weight_kg')?.hasError('max')">Máximo 300kg</ng-container>
                  </span>
                </label>
                <input type="number" step="0.1" formControlName="weight_kg" class="input-glass" min="30" max="300" [class.input-error]="profileForm.get('weight_kg')?.invalid && (profileForm.get('weight_kg')?.dirty || profileForm.get('weight_kg')?.touched)">
              </div>
              
              <div class="form-group">
                <label>Altura (cm)
                  <span class="error-text" *ngIf="profileForm.get('height_cm')?.invalid && (profileForm.get('height_cm')?.dirty || profileForm.get('height_cm')?.touched)">
                    <ng-container *ngIf="profileForm.get('height_cm')?.hasError('required')">Requerido</ng-container>
                    <ng-container *ngIf="profileForm.get('height_cm')?.hasError('min')">Mínimo 100cm</ng-container>
                    <ng-container *ngIf="profileForm.get('height_cm')?.hasError('max')">Máximo 250cm</ng-container>
                  </span>
                </label>
                <input type="number" step="1" formControlName="height_cm" class="input-glass" min="100" max="250" [class.input-error]="profileForm.get('height_cm')?.invalid && (profileForm.get('height_cm')?.dirty || profileForm.get('height_cm')?.touched)">
              </div>
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
              <label>Tipo de Dieta</label>
              <select formControlName="diet_type" class="input-glass">
                <option value="">Selecciona...</option>
                <option *ngFor="let diet of availableDiets" [value]="diet">{{ diet }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Alergias o Intolerancias</label>
              <div class="checkbox-group" formArrayName="intolerances" *ngIf="availableIntolerances.length > 0">
                <div *ngFor="let item of availableIntolerances; let i = index" class="checkbox-item">
                  <input type="checkbox" [formControlName]="i" [id]="'intol-' + i">
                  <label [for]="'intol-' + i">{{ item.label }}</label>
                </div>
              </div>
            </div>
            
            <button type="submit" class="btn-primary" style="margin-top: 1rem;" [disabled]="profileForm.invalid || authService.isLoading()">
              {{ authService.isLoading() ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </form>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .dashboard-layout {
      display: flex;
      height: 100vh;
      overflow: hidden;
      background: radial-gradient(circle at center, rgba(15,17,21,1) 0%, rgba(10,12,15,1) 100%);
    }
    .sidebar {
      width: 280px;
      margin: 1rem;
      display: flex;
      flex-direction: column;
      border-radius: var(--border-radius-lg);
    }
    .brand {
      padding: 2rem;
      border-bottom: 1px solid var(--border-light);
    }
    .user-info {
      padding: 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      border-bottom: 1px solid var(--border-light);
    }
    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
    }
    .name { font-weight: 500; }
    .email { font-size: 0.8rem; color: var(--text-muted); }
    .nav-menu { padding: 1rem; display: flex; flex-direction: column; gap: 0.5rem; }
    .nav-item {
      padding: 1rem;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      text-align: left;
      border-radius: var(--border-radius-sm);
      cursor: pointer;
      font-weight: 500;
      transition: all var(--transition-fast);
    }
    .nav-item:hover { background: var(--bg-glass-hover); color: var(--text-primary); }
    .nav-item.active { background: rgba(0, 210, 255, 0.1); color: var(--accent-primary); }
    .text-error { color: var(--error); }
    .text-error:hover { background: rgba(239, 68, 68, 0.1); color: var(--error); }

    .chat-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 1rem 1rem 1rem 0;
    }
    .profile-card {
      width: 100%;
      max-width: 800px;
      padding: 2.5rem;
      margin: 0 auto;
    }
    .metrics-badge {
      display: flex;
      gap: 1rem;
    }
    .metric {
      background: rgba(0, 210, 255, 0.1);
      border: 1px solid rgba(0, 210, 255, 0.2);
      padding: 0.5rem 1rem;
      border-radius: var(--border-radius-sm);
      color: var(--accent-primary);
      font-weight: bold;
      display: flex;
      flex-direction: column;
      align-items: center;
      font-size: 1.1rem;
    }
    .metric span {
      font-size: 0.75rem;
      color: var(--text-secondary);
      font-weight: normal;
      text-transform: uppercase;
    }
    .metric-red { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2); color: var(--error); }
    .metric-green { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); color: var(--success); }
    .metric-yellow { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); color: var(--warning); }
    
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
    
    .error-alert {
      background: rgba(239, 68, 68, 0.1);
      color: var(--error);
      padding: 0.75rem;
      border-radius: var(--border-radius-sm);
      margin-bottom: 1.5rem;
      border: 1px solid rgba(239, 68, 68, 0.2);
    }

  `]
})
export class ProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  public authService = inject(AuthService);
  public metaService = inject(MetaService);
  public router = inject(Router);

  public successMessage: string | null = null;

  availableDiets: string[] = [];
  availableIntolerances: { id: string, label: string }[] = [];

  profileForm = this.fb.group({
    first_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    sex: ['', Validators.required],
    weight_kg: ['', [Validators.required, Validators.min(30), Validators.max(300)]],
    height_cm: ['', [Validators.required, Validators.min(100), Validators.max(250), Validators.pattern('^[0-9]+$')]],
    age_years: ['', [Validators.required, Validators.min(18), Validators.max(110), Validators.pattern('^[0-9]+$')]],
    activity_factor: ['1.2', Validators.required],
    diet_type: ['Mediterranea', Validators.required],
    intolerances: this.fb.array([])
  });

  ngOnInit() {
    this.metaService.getDiets().subscribe(diets => {
      this.availableDiets = diets;
    });

    this.metaService.getAllergens().subscribe(allergens => {
      this.availableIntolerances = allergens.map(a => ({ id: a, label: a }));
      
      const intolerancesFormArray = this.profileForm.get('intolerances') as FormArray;
      intolerancesFormArray.clear();
      
      this.availableIntolerances.forEach(() => {
        intolerancesFormArray.push(this.fb.control(false));
      });

      this.loadUserData();
    });
  }

  private loadUserData() {
    const user = this.authService.currentUser();
    if (user) {
      this.patchUserToForm(user);
    } else {
      this.authService.fetchCurrentUser().subscribe(u => {
        this.patchUserToForm(u);
      });
    }
  }

  private patchUserToForm(user: any) {
    this.profileForm.patchValue({
      first_name: user.first_name || '',
      email: user.email || '',
      sex: user.sex || '',
      weight_kg: user.weight_kg ? user.weight_kg.toString() : '',
      height_cm: user.height_cm ? user.height_cm.toString() : '',
      age_years: user.age_years ? user.age_years.toString() : '',
      activity_factor: user.activity_factor ? user.activity_factor.toString() : '1.2',
      diet_type: user.diet_type || ''
    });

    if (user.intolerances && this.availableIntolerances.length > 0) {
      const boolArray = this.availableIntolerances.map(i => user.intolerances!.includes(i.id));
      this.profileForm.controls.intolerances.setValue(boolArray);
    }
  }

  getBmiClass(bmi: number | undefined | null): string {
    if (!bmi) return '';
    if (bmi < 18.5) return 'metric-red';
    if (bmi < 25.0) return 'metric-green';
    if (bmi < 30.0) return 'metric-yellow';
    return 'metric-red';
  }

  onSubmit() {
    if (this.profileForm.valid) {
      const currentEmail = this.authService.currentUser()?.email;
      if (!currentEmail) {
        this.authService.error.set("Usuario no autenticado");
        return;
      }

      const formValue = this.profileForm.value as any;
      const selectedIntolerances = formValue.intolerances
        .map((checked: boolean, i: number) => checked ? this.availableIntolerances[i].id : null)
        .filter((v: string | null) => v !== null);

      const payload: any = {
        email: currentEmail, // always send original email to identify the user
        sex: formValue.sex,
        weight_kg: Number(formValue.weight_kg),
        height_cm: Number(formValue.height_cm),
        age_years: Number(formValue.age_years),
        activity_factor: Number(formValue.activity_factor),
        diet_type: formValue.diet_type,
        intolerances: selectedIntolerances,
        first_name: formValue.first_name
      };

      // If email has changed, we send it as new_email
      const newEmail = formValue.email;
      if (newEmail !== currentEmail) {
        payload.new_email = newEmail;
      }

      this.authService.updateProfile(payload).subscribe({
        next: () => {
          window.alert("¡Perfil actualizado con éxito!");

          if (newEmail !== currentEmail) {
            // Force re-login
            this.authService.logout();
          }
        }
      });
    }
  }

  logout() {
    this.authService.logout();
  }
}
