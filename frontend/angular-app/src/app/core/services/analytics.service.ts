import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserAnalytics {
  total_users: number;
  sex_distribution: {
    males: number;
    females: number;
    unspecified: number;
  };
  weight_stats: {
    avg_weight_kg: number;
    distribution: Record<string, number>;
  };
  height_stats?: {
    avg_height_cm: number;
  };
  age_stats: {
    avg_age_years: number;
    distribution: Record<string, number>;
  };
  activity_stats: Record<string, number>;
  diet_types_distribution: { diet_type: string; count: number }[];
  intolerances_distribution: { intolerance: string; count: number }[];
}

export interface GraphAnalytics {
  total_recipes: number;
  total_ingredients?: number;
  total_allergens?: number;
  top_ingredients_used: { ingredient: string; recipe_count: number }[];
  top_recipes: { name: string; ingredient_count: number }[];
  allergens_stats: { name: string; active_count: number }[];
}

export interface AiAnalytics {
  total_conversations: number;
  total_messages: number;
  user_messages: number;
  ai_responses: number;
  average_latency_ms: number;
  p95_latency_ms: number;
  top_asked_ingredients: { keyword: string; count: number }[];
}

export interface CompleteAnalytics {
  users: UserAnalytics;
  graph: GraphAnalytics;
  ai: AiAnalytics;
}

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private readonly userAnalyticsUrl = `${environment.apiUrl}/admin/analytics/users`;
  private readonly graphAnalyticsUrl = `${(environment as any).graphApiUrl || 'http://localhost:8001/api/v1'}/admin/analytics/graph`;
  private readonly aiAnalyticsUrl = `${environment.chatApiUrl || 'http://localhost:8002/api/v1'}/admin/analytics/ai`;

  constructor(private http: HttpClient) {}

  getUserAnalytics(): Observable<UserAnalytics> {
    return this.http.get<UserAnalytics>(this.userAnalyticsUrl);
  }

  getGraphAnalytics(): Observable<GraphAnalytics> {
    return this.http.get<GraphAnalytics>(this.graphAnalyticsUrl);
  }

  getAiAnalytics(): Observable<AiAnalytics> {
    return this.http.get<AiAnalytics>(this.aiAnalyticsUrl);
  }

  getAllAnalytics(): Observable<CompleteAnalytics> {
    return forkJoin({
      users: this.getUserAnalytics(),
      graph: this.getGraphAnalytics(),
      ai: this.getAiAnalytics()
    });
  }
}
