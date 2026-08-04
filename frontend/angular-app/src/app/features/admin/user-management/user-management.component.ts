import { Component, OnInit, signal, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../../core/services/admin.service';
import { MetaService } from '../../../core/services/meta.service';
import { User } from '../../../core/services/auth.service';

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="user-management">
      <div class="header-actions">
        <h2>Gestión de Usuarios</h2>
        <div class="header-controls">
          <div class="search-bar">
            <input 
              type="text" 
              class="form-control search-input" 
              placeholder="Buscar por nombre o email..." 
              [ngModel]="searchTerm()"
              (ngModelChange)="searchTerm.set($event)"
            >
          </div>
          <button class="btn btn-primary" (click)="openCreateModal()">
            + Nuevo Usuario
          </button>
        </div>
      </div>

      <div class="error-msg" *ngIf="adminService.error()">
        {{ adminService.error() }}
      </div>

      <div class="table-container">
        <table class="premium-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Nombre</th>
              <th>Rol</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let user of filteredUsers()">
              <td>{{ user.email }}</td>
              <td>{{ user.first_name }}</td>
              <td>
                <span class="badge" [ngClass]="user.role === 'admin' ? 'badge-admin' : 'badge-user'">
                  {{ user.role || 'user' }}
                </span>
              </td>
              <td class="actions">
                <button class="btn btn-icon btn-edit" (click)="openEditModal(user)" title="Editar">
                  ✏️
                </button>
                <button class="btn btn-icon btn-delete" (click)="deleteUser(user.email)" title="Eliminar">
                  🗑️
                </button>
              </td>
            </tr>
            <tr *ngIf="filteredUsers().length === 0">
              <td colspan="4" class="text-center">No se encontraron usuarios.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Modal Crear/Editar -->
      <div class="modal-overlay" *ngIf="isModalOpen()">
        <div class="modal-content form-scrollable">
          <h3>{{ isEditing() ? 'Editar Usuario' : 'Crear Usuario' }}</h3>
          <form (ngSubmit)="submitForm()" #userForm="ngForm">
            <div class="form-group" *ngIf="!isEditing()">
              <label>Email</label>
              <input type="email" [(ngModel)]="formData.email" name="email" required class="form-control">
            </div>
            
            <div class="form-group" *ngIf="!isEditing()">
              <label>Contraseña</label>
              <input type="password" [(ngModel)]="formData.password" name="password" required class="form-control">
            </div>

            <div class="form-group">
              <label>Nombre</label>
              <input type="text" [(ngModel)]="formData.first_name" name="first_name" required class="form-control">
            </div>

            <div class="form-group">
              <label>Rol</label>
              <select [(ngModel)]="formData.role" name="role" class="form-control">
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            
            <div *ngIf="isEditing()">
              <h4 class="section-title">Biometría y Dieta</h4>
              <div class="form-group">
                <label>Sexo
                  <span class="error-text" *ngIf="sexCtrl.invalid && (sexCtrl.dirty || sexCtrl.touched)">
                    <span *ngIf="sexCtrl.errors?.['required']">Requerido</span>
                  </span>
                </label>
                <select [(ngModel)]="formData.sex" name="sex" #sexCtrl="ngModel" required class="form-control" [class.input-error]="sexCtrl.invalid && (sexCtrl.dirty || sexCtrl.touched)">
                  <option value="">No especificado</option>
                  <option value="m">Masculino</option>
                  <option value="f">Femenino</option>
                </select>
              </div>
              <div class="form-group">
                <label>Peso (kg)
                  <span class="error-text" *ngIf="weightCtrl.invalid && (weightCtrl.dirty || weightCtrl.touched)">
                    <span *ngIf="weightCtrl.errors?.['required']">Requerido</span>
                    <span *ngIf="weightCtrl.errors?.['min']">Mínimo 30</span>
                    <span *ngIf="weightCtrl.errors?.['max']">Máximo 300</span>
                  </span>
                </label>
                <input type="number" [(ngModel)]="formData.weight_kg" name="weight_kg" #weightCtrl="ngModel" required min="30" max="300" class="form-control" step="0.1" [class.input-error]="weightCtrl.invalid && (weightCtrl.dirty || weightCtrl.touched)">
              </div>
              <div class="form-group">
                <label>Altura (cm)
                  <span class="error-text" *ngIf="heightCtrl.invalid && (heightCtrl.dirty || heightCtrl.touched)">
                    <span *ngIf="heightCtrl.errors?.['required']">Requerido</span>
                    <span *ngIf="heightCtrl.errors?.['min']">Mínimo 100</span>
                    <span *ngIf="heightCtrl.errors?.['max']">Máximo 250</span>
                  </span>
                </label>
                <input type="number" [(ngModel)]="formData.height_cm" name="height_cm" #heightCtrl="ngModel" required min="100" max="250" class="form-control" step="0.1" [class.input-error]="heightCtrl.invalid && (heightCtrl.dirty || heightCtrl.touched)">
              </div>
              <div class="form-group">
                <label>Edad
                  <span class="error-text" *ngIf="ageCtrl.invalid && (ageCtrl.dirty || ageCtrl.touched)">
                    <span *ngIf="ageCtrl.errors?.['required']">Requerido</span>
                    <span *ngIf="ageCtrl.errors?.['min']">Mínimo 18</span>
                    <span *ngIf="ageCtrl.errors?.['max']">Máximo 110</span>
                  </span>
                </label>
                <input type="number" [(ngModel)]="formData.age_years" name="age_years" #ageCtrl="ngModel" required min="18" max="110" class="form-control" [class.input-error]="ageCtrl.invalid && (ageCtrl.dirty || ageCtrl.touched)">
              </div>
              <div class="form-group">
                <label>Factor de Actividad
                  <span class="error-text" *ngIf="activityCtrl.invalid && (activityCtrl.dirty || activityCtrl.touched)">
                    <span *ngIf="activityCtrl.errors?.['required']">Requerido</span>
                  </span>
                </label>
                <select [(ngModel)]="formData.activity_factor" name="activity_factor" #activityCtrl="ngModel" required class="form-control" [class.input-error]="activityCtrl.invalid && (activityCtrl.dirty || activityCtrl.touched)">
                  <option [ngValue]="null">No especificado</option>
                  <option [ngValue]="1.2">Sedentario (1.2)</option>
                  <option [ngValue]="1.375">Ligero (1.375)</option>
                  <option [ngValue]="1.55">Moderado (1.55)</option>
                  <option [ngValue]="1.725">Activo (1.725)</option>
                  <option [ngValue]="1.9">Muy activo (1.9)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Tipo de Dieta
                  <span class="error-text" *ngIf="dietCtrl.invalid && (dietCtrl.dirty || dietCtrl.touched)">
                    <span *ngIf="dietCtrl.errors?.['required']">Requerido</span>
                  </span>
                </label>
                <select [(ngModel)]="formData.diet_type" name="diet_type" #dietCtrl="ngModel" required class="form-control" [class.input-error]="dietCtrl.invalid && (dietCtrl.dirty || dietCtrl.touched)">
                  <option value="">No especificado</option>
                  <option *ngFor="let diet of availableDiets()" [value]="diet">{{ diet }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Intolerancias</label>
                <div class="tags-container" *ngIf="formData.intolerances?.length">
                  <span class="tag" *ngFor="let intol of formData.intolerances">
                    {{ intol }}
                    <button type="button" class="tag-remove" (click)="removeIntolerance(intol)">&times;</button>
                  </span>
                </div>
                <select class="form-control" (change)="addIntolerance($event)">
                  <option value="">Añadir intolerancia...</option>
                  <option *ngFor="let item of availableAllergens()" [value]="item" [disabled]="formData.intolerances.includes(item)">
                    {{ item }}
                  </option>
                </select>
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" (click)="closeModal()">Cancelar</button>
              <button type="submit" class="btn btn-primary" [disabled]="adminService.isLoading() || userForm.invalid">
                {{ isEditing() ? 'Guardar' : 'Crear' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .user-management {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .header-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .header-controls {
      display: flex;
      gap: 1rem;
      align-items: center;
    }

    .search-bar {
      position: relative;
    }

    .search-input {
      width: 280px;
      padding: 0.6rem 1rem;
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border-color, #333);
      border-radius: 20px;
      color: var(--text-color, #fff);
      font-family: inherit;
      transition: all 0.3s ease;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--primary-color, #bb86fc);
      background: rgba(255,255,255,0.08);
      box-shadow: 0 0 0 2px rgba(187, 134, 252, 0.2);
    }

    .header-actions h2 {
      margin: 0;
      color: var(--text-color, #ffffff);
    }

    .table-container {
      background: var(--surface-color, #1e1e1e);
      border-radius: 12px;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      box-shadow: 0 4px 6px rgba(0,0,0,0.3);
      width: 100%;
    }

    .premium-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .premium-table th, .premium-table td {
      padding: 1rem 1.5rem;
      border-bottom: 1px solid var(--border-color, #333);
    }

    .premium-table th {
      background: rgba(255,255,255,0.05);
      color: var(--text-muted, #b3b3b3);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 0.85rem;
      letter-spacing: 0.05em;
    }

    .premium-table tbody tr:hover {
      background: rgba(255,255,255,0.02);
    }

    .badge {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
    }

    .badge-admin {
      background: rgba(187, 134, 252, 0.2);
      color: #bb86fc;
    }

    .badge-user {
      background: rgba(3, 218, 198, 0.2);
      color: #03dac6;
    }

    .actions {
      display: flex;
      gap: 0.5rem;
    }

    .btn {
      padding: 0.5rem 1rem;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s ease;
    }

    .btn-primary {
      background: var(--primary-color, #bb86fc);
      color: #000;
    }

    .btn-primary:hover:not(:disabled) {
      background: #9965f4;
    }

    .btn-primary:disabled {
      background: rgba(187, 134, 252, 0.4);
      color: rgba(0, 0, 0, 0.5);
      cursor: not-allowed;
    }

    .btn-secondary {
      background: transparent;
      color: var(--text-color, #fff);
      border: 1px solid var(--border-color, #333);
    }

    .btn-secondary:hover {
      background: rgba(255,255,255,0.1);
    }

    .btn-icon {
      padding: 0.5rem;
      background: transparent;
      border-radius: 50%;
    }

    .btn-icon:hover {
      background: rgba(255,255,255,0.1);
    }

    .text-center {
      text-align: center;
      color: var(--text-muted, #b3b3b3);
    }

    .error-msg {
      background: rgba(207, 102, 121, 0.2);
      color: #cf6679;
      padding: 1rem;
      border-radius: 8px;
    }

    /* Modal Styles */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      backdrop-filter: blur(5px);
    }

    .modal-content {
      background: var(--surface-color, #1e1e1e);
      padding: 2rem;
      border-radius: 12px;
      width: 100%;
      max-width: 400px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      border: 1px solid var(--border-color, #333);
    }
    
    .form-scrollable {
      max-height: 90vh;
      overflow-y: auto;
    }
    
    .section-title {
      margin-top: 1.5rem;
      margin-bottom: 1rem;
      color: var(--primary-color, #bb86fc);
      border-bottom: 1px solid var(--border-color, #333);
      padding-bottom: 0.5rem;
    }

    .modal-content h3 {
      margin-top: 0;
      margin-bottom: 1.5rem;
      color: var(--primary-color, #bb86fc);
    }

    .form-group {
      margin-bottom: 1.25rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      color: var(--text-muted, #b3b3b3);
      font-size: 0.9rem;
    }

    .form-control {
      width: 100%;
      padding: 0.75rem;
      border-radius: 8px;
      border: 1px solid var(--border-color, #333);
      background: rgba(255,255,255,0.05);
      color: var(--text-color, #fff);
      font-family: inherit;
    }

    .form-control:focus {
      outline: none;
      border-color: var(--primary-color, #bb86fc);
      box-shadow: 0 0 0 2px rgba(187, 134, 252, 0.2);
    }

    .form-control.input-error {
      border-color: #cf6679;
    }
    .form-control.input-error:focus {
      box-shadow: 0 0 0 2px rgba(207, 102, 121, 0.2);
    }

    .error-text {
      color: #cf6679;
      font-size: 0.8rem;
      margin-left: 0.5rem;
    }

    select.form-control option {
      background-color: #1e1e1e;
      color: #fff;
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 1rem;
      margin-top: 2rem;
    }

    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
    }

    .tag {
      background: rgba(187, 134, 252, 0.2);
      color: #bb86fc;
      padding: 0.35rem 0.75rem;
      border-radius: 16px;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .tag-remove {
      background: transparent;
      border: none;
      color: #bb86fc;
      cursor: pointer;
      font-size: 1.2rem;
      line-height: 1;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .tag-remove:hover {
      color: #fff;
    }
  `]
})
export class UserManagementComponent implements OnInit {
  adminService = inject(AdminService);
  metaService = inject(MetaService);

  isModalOpen = signal(false);
  isEditing = signal(false);
  editingEmail = signal('');
  searchTerm = signal('');

  users = toSignal(this.adminService.users$, { initialValue: [] });
  availableDiets = toSignal(this.metaService.getDiets(), { initialValue: [] });
  availableAllergens = toSignal(this.metaService.getAllergens(), { initialValue: [] });

  filteredUsers = computed(() => {
    const term = this.searchTerm().toLowerCase().trim();
    const usersList = this.users() || [];
    if (!term) return usersList;

    return usersList.filter((user: User) =>
      user.email.toLowerCase().includes(term) ||
      user.first_name.toLowerCase().includes(term)
    );
  });

  formData: any = {
    email: '',
    password: '',
    first_name: '',
    role: 'user',
    sex: '',
    weight_kg: null,
    height_cm: null,
    age_years: null,
    activity_factor: null,
    diet_type: '',
    intolerances: []
  };

  constructor() { }

  ngOnInit() {
    this.adminService.fetchUsers().subscribe();
  }

  openCreateModal() {
    this.isEditing.set(false);
    this.formData = {
      email: '', password: '', first_name: '', role: 'user',
      sex: '', weight_kg: null, height_cm: null, age_years: null,
      activity_factor: null, diet_type: '', intolerances: []
    };
    this.isModalOpen.set(true);
  }

  openEditModal(user: User) {
    this.isEditing.set(true);
    this.editingEmail.set(user.email);
    this.formData = {
      email: user.email,
      password: '', // Ignored on update
      first_name: user.first_name,
      role: user.role || 'user',
      sex: user.sex || '',
      weight_kg: user.weight_kg || null,
      height_cm: user.height_cm || null,
      age_years: user.age_years || null,
      activity_factor: user.activity_factor || null,
      diet_type: user.diet_type || '',
      intolerances: user.intolerances ? [...user.intolerances] : []
    };
    this.isModalOpen.set(true);
  }

  closeModal() {
    this.isModalOpen.set(false);
  }

  submitForm() {
    if (this.isEditing()) {
      const updateData: any = {
        first_name: this.formData.first_name,
        role: this.formData.role,
        sex: this.formData.sex || null,
        weight_kg: this.formData.weight_kg || null,
        height_cm: this.formData.height_cm || null,
        age_years: this.formData.age_years || null,
        activity_factor: this.formData.activity_factor || null,
        diet_type: this.formData.diet_type || null,
        intolerances: this.formData.intolerances || []
      };
      this.adminService.updateUser(this.editingEmail(), updateData).subscribe({
        next: () => this.closeModal()
      });
    } else {
      const createData = {
        email: this.formData.email,
        password: this.formData.password,
        first_name: this.formData.first_name,
        role: this.formData.role
      };
      this.adminService.createUser(createData).subscribe({
        next: () => this.closeModal()
      });
    }
  }

  deleteUser(email: string) {
    if (confirm(`¿Estás seguro de que deseas eliminar al usuario ${email}?`)) {
      this.adminService.deleteUser(email).subscribe();
    }
  }

  addIntolerance(event: any) {
    const value = event.target.value;
    if (value && !this.formData.intolerances.includes(value)) {
      this.formData.intolerances.push(value);
    }
    // Reset select
    event.target.value = '';
  }

  removeIntolerance(intolerance: string) {
    this.formData.intolerances = this.formData.intolerances.filter((i: string) => i !== intolerance);
  }
}
