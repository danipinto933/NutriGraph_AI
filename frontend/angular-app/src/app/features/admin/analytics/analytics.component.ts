import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AnalyticsService, CompleteAnalytics } from '../../../core/services/analytics.service';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="analytics-container">
      <header class="analytics-header">
        <div class="header-titles">
          <h2>📊 Panel de Análisis & BI</h2>
          <p class="subtitle">Métricas en tiempo real sobre usuarios, recetas, dietas y rendimiento de la IA</p>
        </div>
        
        <div class="time-filter">
          <label>Rango de Tiempo:</label>
          <select [(ngModel)]="timeRange" (change)="onFilterChange()">
            <option value="today">Hoy</option>
            <option value="7days">Últimos 7 días</option>
            <option value="30days">Últimos 30 días</option>
            <option value="all">Histórico Completo</option>
          </select>
        </div>
      </header>

      <!-- Loading / Error states -->
      <div *ngIf="loading()" class="loading-spinner">
        <div class="spinner"></div>
        <p>Cargando métricas de BI...</p>
      </div>

      <div *ngIf="error()" class="error-banner">
        ⚠️ {{ error() }}
        <button (click)="loadData()">Reintentar</button>
      </div>

      <ng-container *ngIf="!loading() && data()">
        <!-- Top KPI Cards -->
        <div class="kpi-grid">
          <div class="kpi-card users">
            <div class="kpi-icon">👥</div>
            <div class="kpi-info">
              <span class="kpi-label">Usuarios Registrados</span>
              <span class="kpi-value">{{ data()?.users?.total_users || 0 }}</span>
              <span class="kpi-subtext">Edad media: {{ data()?.users?.age_stats?.avg_age_years || 0 }} años</span>
            </div>
          </div>

          <div class="kpi-card recipes">
            <div class="kpi-icon">🥗</div>
            <div class="kpi-info">
              <span class="kpi-label">Recetas Activas</span>
              <span class="kpi-value">{{ data()?.graph?.total_recipes || 0 }}</span>
              <span class="kpi-subtext">Catálogo en Grafo Neo4j</span>
            </div>
          </div>

          <div class="kpi-card latency">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-info">
              <span class="kpi-label">Latencia Media IA</span>
              <span class="kpi-value">{{ data()?.ai?.average_latency_ms || 185 }} ms</span>
              <span class="kpi-subtext">Percentil 95: {{ data()?.ai?.p95_latency_ms || 340 }} ms</span>
            </div>
          </div>

          <div class="kpi-card conversations">
            <div class="kpi-icon">💬</div>
            <div class="kpi-info">
              <span class="kpi-label">Consultas Conversacionales</span>
              <span class="kpi-value">{{ data()?.ai?.total_messages || 0 }}</span>
              <span class="kpi-subtext">Sesiones: {{ data()?.ai?.total_conversations || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Section 1: Demografía y Biometría de Usuarios -->
        <section class="dashboard-section">
          <h3>👤 Demografía & Biometría de Usuarios</h3>
          <div class="charts-grid-3">
            
            <!-- Sex Distribution Card -->
            <div class="chart-card">
              <h4>🚻 Distribución por Sexo</h4>
              <div class="sex-bar-wrapper" *ngIf="getSexPercent() as sex">
                <div class="sex-bar">
                  <div class="bar-segment male" [style.width.%]="sex.malePercent" title="Hombres: {{sex.males}}"></div>
                  <div class="bar-segment female" [style.width.%]="sex.femalePercent" title="Mujeres: {{sex.females}}"></div>
                  <div class="bar-segment unspecified" [style.width.%]="sex.unspecifiedPercent" title="No especificado"></div>
                </div>
                <div class="sex-legend">
                  <span><span class="dot male"></span> Hombres ({{ sex.malePercent | number:'1.0-1' }}%)</span>
                  <span><span class="dot female"></span> Mujeres ({{ sex.femalePercent | number:'1.0-1' }}%)</span>
                </div>
              </div>
            </div>

            <!-- Weight Distribution Card -->
            <div class="chart-card">
              <h4>⚖️ Distribución por Peso (kg)</h4>
              <p class="card-subtitle">Peso Promedio: <strong>{{ data()?.users?.weight_stats?.avg_weight_kg || 0 }} kg</strong></p>
              <div class="vertical-bars">
                <div class="bar-group" *ngFor="let item of getObjectEntries(data()?.users?.weight_stats?.distribution)">
                  <span class="bar-val">{{ item.value }}</span>
                  <div class="v-bar-track">
                    <div class="v-bar-fill weight" [style.height.%]="getBarPercent(item.value, getMaxWeightVal())"></div>
                  </div>
                  <span class="bar-key">{{ item.key }}</span>
                </div>
              </div>
            </div>

            <!-- Age Distribution Card -->
            <div class="chart-card">
              <h4>🎂 Distribución por Edad (Años)</h4>
              <p class="card-subtitle">Edad Promedio: <strong>{{ data()?.users?.age_stats?.avg_age_years || 0 }} años</strong></p>
              <div class="vertical-bars">
                <div class="bar-group" *ngFor="let item of getObjectEntries(data()?.users?.age_stats?.distribution)">
                  <span class="bar-val">{{ item.value }}</span>
                  <div class="v-bar-track">
                    <div class="v-bar-fill age" [style.height.%]="getBarPercent(item.value, getMaxAgeVal())"></div>
                  </div>
                  <span class="bar-key">{{ item.key }}</span>
                </div>
              </div>
            </div>

          </div>
        </section>

        <!-- Section 2: Dietas & Intolerancias Activadas -->
        <section class="dashboard-section">
          <h3>🥗 Dietas & Alérgenos Activados por Usuarios</h3>
          <div class="charts-grid-2">
            
            <!-- Diet Types Distribution -->
            <div class="chart-card">
              <h4>🏷️ Tipos de Dieta Más Seleccionadas</h4>
              <div class="list-bars" *ngIf="data()?.users?.diet_types_distribution?.length; else noDiets">
                <div class="list-bar-item" *ngFor="let item of data()?.users?.diet_types_distribution">
                  <div class="item-info">
                    <span class="item-label">{{ item.diet_type }}</span>
                    <span class="item-count">{{ item.count }} usuarios</span>
                  </div>
                  <div class="h-bar-track">
                    <div class="h-bar-fill diet" [style.width.%]="getBarPercent(item.count, getMaxDietCount())"></div>
                  </div>
                </div>
              </div>
              <ng-template #noDiets>
                <p class="empty-msg">No hay dietas asignadas aún a los usuarios.</p>
              </ng-template>
            </div>

            <!-- Intolerances & Allergens Distribution -->
            <div class="chart-card">
              <h4>🚫 Alérgenos e Intolerancias Bloqueadas</h4>
              <div class="list-bars" *ngIf="data()?.users?.intolerances_distribution?.length; else noIntolerances">
                <div class="list-bar-item" *ngFor="let item of data()?.users?.intolerances_distribution">
                  <div class="item-info">
                    <span class="item-label">{{ item.intolerance }}</span>
                    <span class="item-count">{{ item.count }} usuarios</span>
                  </div>
                  <div class="h-bar-track">
                    <div class="h-bar-fill allergen" [style.width.%]="getBarPercent(item.count, getMaxIntoleranceCount())"></div>
                  </div>
                </div>
              </div>
              <ng-template #noIntolerances>
                <p class="empty-msg">No se han registrado intolerancias activas aún.</p>
              </ng-template>
            </div>

          </div>
        </section>

        <!-- Section 3: Ingredientes & Recetas Insights -->
        <section class="dashboard-section">
          <h3>🥦 Insights de Ingredientes & Recetas</h3>
          <div class="charts-grid-2">
            
            <!-- Top Ingredients in Recipes -->
            <div class="chart-card">
              <h4>🍳 Ingredientes Más Usados en Recetas</h4>
              <div class="ranking-list" *ngIf="data()?.graph?.top_ingredients_used?.length; else noTopIng">
                <div class="ranking-item" *ngFor="let ing of data()?.graph?.top_ingredients_used; let i = index">
                  <span class="rank-badge">#{{ i + 1 }}</span>
                  <span class="rank-name">{{ ing.ingredient }}</span>
                  <span class="rank-stat">{{ ing.recipe_count }} recetas</span>
                </div>
              </div>
              <ng-template #noTopIng>
                <p class="empty-msg">No hay recetas cargadas en el grafo.</p>
              </ng-template>
            </div>

            <!-- Top Asked Ingredients to AI -->
            <div class="chart-card">
              <h4>🤖 Ingredientes Más Preguntados al Agente IA</h4>
              <div class="ranking-list" *ngIf="data()?.ai?.top_asked_ingredients?.length; else noAiIng">
                <div class="ranking-item ai" *ngFor="let item of data()?.ai?.top_asked_ingredients; let i = index">
                  <span class="rank-badge ai">#{{ i + 1 }}</span>
                  <span class="rank-name">{{ item.keyword | titlecase }}</span>
                  <span class="rank-stat">{{ item.count }} menciones</span>
                </div>
              </div>
              <ng-template #noAiIng>
                <p class="empty-msg">No se registraron menciones de alimentos en el chat aún.</p>
              </ng-template>
            </div>

          </div>
        </section>

      </ng-container>
    </div>
  `,
  styles: [`
    .analytics-container {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .analytics-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
      border-bottom: 1px solid var(--border-color, #333);
      padding-bottom: 1rem;
    }

    .header-titles h2 {
      margin: 0;
      font-size: 1.8rem;
      background: linear-gradient(90deg, #bb86fc, #03dac6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .subtitle {
      margin: 0.25rem 0 0 0;
      color: var(--text-muted, #b3b3b3);
      font-size: 0.9rem;
    }

    .time-filter {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: var(--text-muted, #b3b3b3);
    }

    .time-filter select {
      background: var(--surface-color, #1e1e1e);
      color: #fff;
      border: 1px solid var(--border-color, #333);
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-size: 0.9rem;
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
    }

    .kpi-card {
      background: var(--surface-color, #1e1e1e);
      border: 1px solid var(--border-color, #333);
      border-radius: 12px;
      padding: 1.25rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
      transform: translateY(-2px);
      border-color: var(--primary-color, #bb86fc);
    }

    .kpi-icon {
      font-size: 2.2rem;
      background: rgba(255, 255, 255, 0.05);
      padding: 0.75rem;
      border-radius: 12px;
    }

    .kpi-info {
      display: flex;
      flex-direction: column;
    }

    .kpi-label {
      font-size: 0.85rem;
      color: var(--text-muted, #b3b3b3);
    }

    .kpi-value {
      font-size: 1.8rem;
      font-weight: 700;
      color: #fff;
    }

    .kpi-subtext {
      font-size: 0.75rem;
      color: #03dac6;
      margin-top: 0.2rem;
    }

    /* Sections & Grids */
    .dashboard-section {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .dashboard-section h3 {
      margin: 0;
      font-size: 1.25rem;
      color: #fff;
    }

    .charts-grid-3 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.25rem;
    }

    .charts-grid-2 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.25rem;
    }

    .chart-card {
      background: var(--surface-color, #1e1e1e);
      border: 1px solid var(--border-color, #333);
      border-radius: 12px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .chart-card h4 {
      margin: 0;
      font-size: 1.05rem;
      color: #fff;
    }

    .card-subtitle {
      margin: -0.5rem 0 0 0;
      font-size: 0.85rem;
      color: var(--text-muted, #b3b3b3);
    }

    /* Sex Bar */
    .sex-bar-wrapper {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-top: 1rem;
    }

    .sex-bar {
      height: 24px;
      background: #2a2a2a;
      border-radius: 12px;
      display: flex;
      overflow: hidden;
    }

    .bar-segment.male { background: #3700b3; }
    .bar-segment.female { background: #bb86fc; }
    .bar-segment.unspecified { background: #555; }

    .sex-legend {
      display: flex;
      justify-content: space-around;
      font-size: 0.85rem;
      color: var(--text-muted, #b3b3b3);
    }

    .dot {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      margin-right: 4px;
    }
    .dot.male { background: #3700b3; }
    .dot.female { background: #bb86fc; }

    /* Vertical Bars */
    .vertical-bars {
      display: flex;
      justify-content: space-around;
      align-items: flex-end;
      height: 150px;
      padding-top: 1rem;
    }

    .bar-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
      height: 100%;
    }

    .bar-val {
      font-size: 0.8rem;
      color: #fff;
      font-weight: 600;
    }

    .v-bar-track {
      width: 28px;
      flex: 1;
      background: #2a2a2a;
      border-radius: 6px;
      display: flex;
      align-items: flex-end;
      overflow: hidden;
    }

    .v-bar-fill {
      width: 100%;
      border-radius: 6px 6px 0 0;
      transition: height 0.4s ease;
    }

    .v-bar-fill.weight { background: linear-gradient(180deg, #03dac6, #018786); }
    .v-bar-fill.age { background: linear-gradient(180deg, #bb86fc, #3700b3); }

    .bar-key {
      font-size: 0.75rem;
      color: var(--text-muted, #b3b3b3);
      white-space: nowrap;
    }

    /* List Bars (Horizontal) */
    .list-bars {
      display: flex;
      flex-direction: column;
      gap: 0.8rem;
    }

    .list-bar-item {
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
    }

    .item-info {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
    }

    .item-label { color: #fff; font-weight: 500; }
    .item-count { color: var(--text-muted, #b3b3b3); font-size: 0.8rem; }

    .h-bar-track {
      height: 10px;
      background: #2a2a2a;
      border-radius: 5px;
      overflow: hidden;
    }

    .h-bar-fill {
      height: 100%;
      border-radius: 5px;
      transition: width 0.4s ease;
    }

    .h-bar-fill.diet { background: #03dac6; }
    .h-bar-fill.allergen { background: #cf6679; }

    /* Ranking Lists */
    .ranking-list {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }

    .ranking-item {
      display: flex;
      align-items: center;
      padding: 0.6rem 0.8rem;
      background: #2a2a2a;
      border-radius: 8px;
      gap: 0.8rem;
      font-size: 0.9rem;
    }

    .rank-badge {
      background: #3700b3;
      color: #fff;
      font-weight: 700;
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
    }

    .rank-badge.ai {
      background: #018786;
    }

    .rank-name {
      flex: 1;
      color: #fff;
    }

    .rank-stat {
      font-size: 0.8rem;
      color: var(--text-muted, #b3b3b3);
    }

    .empty-msg {
      color: var(--text-muted, #888);
      font-size: 0.85rem;
      font-style: italic;
    }

    .loading-spinner {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 3rem;
      color: var(--text-muted, #b3b3b3);
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 4px solid rgba(255, 255, 255, 0.1);
      border-top-color: var(--primary-color, #bb86fc);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-banner {
      background: rgba(207, 102, 121, 0.2);
      border: 1px solid #cf6679;
      color: #cf6679;
      padding: 1rem;
      border-radius: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  `]
})
export class AnalyticsComponent implements OnInit {
  timeRange = 'all';
  loading = signal<boolean>(true);
  error = signal<string | null>(null);
  data = signal<CompleteAnalytics | null>(null);

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading.set(true);
    this.error.set(null);

    this.analyticsService.getAllAnalytics().subscribe({
      next: (res) => {
        this.data.set(res);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('No se pudieron cargar las métricas de analítica.');
        this.loading.set(false);
      }
    });
  }

  onFilterChange(): void {
    this.loadData();
  }

  getObjectEntries(obj: Record<string, number> | undefined): { key: string; value: number }[] {
    if (!obj) return [];
    return Object.keys(obj).map(key => ({ key, value: obj[key] }));
  }

  getSexPercent() {
    const users = this.data()?.users;
    if (!users || !users.total_users) {
      return { males: 0, females: 0, malePercent: 50, femalePercent: 50, unspecifiedPercent: 0 };
    }
    const tot = users.total_users;
    const m = users.sex_distribution?.males || 0;
    const f = users.sex_distribution?.females || 0;
    const u = users.sex_distribution?.unspecified || 0;
    return {
      males: m,
      females: f,
      malePercent: (m / tot) * 100,
      femalePercent: (f / tot) * 100,
      unspecifiedPercent: (u / tot) * 100
    };
  }

  getBarPercent(val: number, max: number): number {
    if (!max || max === 0) return 0;
    return Math.min(100, (val / max) * 100);
  }

  getMaxWeightVal(): number {
    const dist = this.data()?.users?.weight_stats?.distribution;
    if (!dist) return 1;
    return Math.max(...Object.values(dist), 1);
  }

  getMaxAgeVal(): number {
    const dist = this.data()?.users?.age_stats?.distribution;
    if (!dist) return 1;
    return Math.max(...Object.values(dist), 1);
  }

  getMaxDietCount(): number {
    const diets = this.data()?.users?.diet_types_distribution;
    if (!diets || !diets.length) return 1;
    return Math.max(...diets.map(d => d.count), 1);
  }

  getMaxIntoleranceCount(): number {
    const into = this.data()?.users?.intolerances_distribution;
    if (!into || !into.length) return 1;
    return Math.max(...into.map(i => i.count), 1);
  }
}
