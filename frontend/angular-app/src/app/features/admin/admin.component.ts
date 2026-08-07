import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { UserManagementComponent } from './user-management/user-management.component';
import { DietTypeManagementComponent } from './diet-type-management/diet-type-management.component';
import { AllergenManagementComponent } from './allergen-management/allergen-management.component';
import { IngredientManagementComponent } from './ingredient-management/ingredient-management.component';
import { RecipeManagementComponent } from './recipe-management/recipe-management.component';
import { AnalyticsComponent } from './analytics/analytics.component';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    UserManagementComponent,
    DietTypeManagementComponent,
    AllergenManagementComponent,
    IngredientManagementComponent,
    RecipeManagementComponent,
    AnalyticsComponent
  ],
  template: `
    <div class="admin-layout">
      <aside class="admin-sidebar">
        <div class="sidebar-header">
          <h2>Admin Panel</h2>
        </div>
        <nav class="sidebar-nav">
          <ul>
            <li [class.active]="currentTab === 'analisis'">
              <a href="javascript:void(0)" (click)="currentTab = 'analisis'">
                <i class="icon-analytics"></i> Análisis & BI
              </a>
            </li>
            <li [class.active]="currentTab === 'usuarios'">
              <a href="javascript:void(0)" (click)="currentTab = 'usuarios'">
                <i class="icon-users"></i> Usuarios
              </a>
            </li>
            <li [class.active]="currentTab === 'ingredientes'">
              <a href="javascript:void(0)" (click)="currentTab = 'ingredientes'">
                <i class="icon-ingredient"></i> Ingredientes
              </a>
            </li>
            <li [class.active]="currentTab === 'recetas'">
              <a href="javascript:void(0)" (click)="currentTab = 'recetas'">
                <i class="icon-recipe"></i> Recetas
              </a>
            </li>
            <li [class.active]="currentTab === 'dietas'">
              <a href="javascript:void(0)" (click)="currentTab = 'dietas'">
                <i class="icon-diet"></i> Tipos de Dieta
              </a>
            </li>
            <li [class.active]="currentTab === 'alergenos'">
              <a href="javascript:void(0)" (click)="currentTab = 'alergenos'">
                <i class="icon-allergen"></i> Alérgenos
              </a>
            </li>
            <li>
              <a routerLink="/profile">
                <i class="icon-back"></i> Volver al Perfil
              </a>
            </li>
          </ul>
        </nav>
      </aside>
      
      <main class="admin-content">
        <ng-container *ngIf="currentTab === 'analisis'">
          <app-analytics [(selectedCategory)]="selectedKpiCategory"></app-analytics>
        </ng-container>
        <ng-container *ngIf="currentTab === 'usuarios'">
          <app-user-management></app-user-management>
        </ng-container>
        <ng-container *ngIf="currentTab === 'ingredientes'">
          <app-ingredient-management></app-ingredient-management>
        </ng-container>
        <ng-container *ngIf="currentTab === 'recetas'">
          <app-recipe-management></app-recipe-management>
        </ng-container>
        <ng-container *ngIf="currentTab === 'dietas'">
          <app-diet-type-management></app-diet-type-management>
        </ng-container>
        <ng-container *ngIf="currentTab === 'alergenos'">
          <app-allergen-management></app-allergen-management>
        </ng-container>
      </main>
    </div>
  `,

  styles: [`
    .admin-layout {
      display: flex;
      min-height: 100vh;
      background-color: var(--background-color, #121212);
      color: var(--text-color, #ffffff);
    }
    
    .admin-sidebar {
      width: 250px;
      background-color: var(--surface-color, #1e1e1e);
      border-right: 1px solid var(--border-color, #333);
      display: flex;
      flex-direction: column;
    }
    
    .sidebar-header {
      padding: 2rem 1.5rem;
      border-bottom: 1px solid var(--border-color, #333);
    }
    
    .sidebar-header h2 {
      margin: 0;
      font-size: 1.5rem;
      background: linear-gradient(90deg, #bb86fc, #03dac6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .sidebar-nav ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    
    .sidebar-nav li {
      margin: 0.5rem 1rem;
    }
    
    .sidebar-nav a {
      display: block;
      padding: 0.75rem 1rem;
      color: var(--text-muted, #b3b3b3);
      text-decoration: none;
      border-radius: 8px;
      transition: background-color 0.3s ease, color 0.3s ease;
      font-weight: 500;
    }
    
    .sidebar-nav a:hover, .sidebar-nav li.active a {
      background-color: rgba(187, 134, 252, 0.1);
      color: var(--primary-color, #bb86fc);
    }
    
    .admin-content {
      flex: 1;
      padding: 2rem;
      overflow-y: auto;
      min-width: 0;
    }
    
    @media (max-width: 768px) {
      .admin-layout {
        flex-direction: column;
      }
      
      .admin-sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid var(--border-color, #333);
      }
      
      .sidebar-nav ul {
        display: flex;
        overflow-x: auto;
        padding: 0.5rem;
      }
      
      .sidebar-nav li {
        margin: 0 0.25rem;
        white-space: nowrap;
      }
      
      .admin-content {
        padding: 1rem;
      }
    }
  `]
})

export class AdminComponent {
  currentTab = 'analisis';
  selectedKpiCategory = 'all';
}


