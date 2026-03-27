import axios, { AxiosInstance } from 'axios';
import type { Player, TacticName } from '../data/players';

const API_BASE_URL = ((import.meta as any).env?.VITE_API_URL as string | undefined) || 'http://localhost:8000/api';

export interface OptimizeRequest {
  tactic: TacticName;
  formation: string;
  budget: number;
  maxPerClub: number;
  manualSelections?: number[];
  objectivePrompt?: string;
}

export interface OptimizeResponse {
  squad: Player[];
  score: number;
  status: string;
  ai_source: string;
  warning?: string;
}

export interface AnalyzeResponse {
  score_100: number;
  verdict: string;
  review: string;
  studio_chat?: string;
  ai_source: string;
  warning?: string;
}

export interface DraftAnalysisResponse {
  coach_commentary: string;
  analyst_breakdown: string;
  pundit_reaction: string;
  ai_source: string;
  warning?: string;
}

export interface DraftAnalysisOptions {
  p1_tactic?: string;
  p2_tactic?: string;
  p1_formation?: string;
  p2_formation?: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        throw new Error(error.response?.data?.detail || 'API request failed');
      }
    );
  }

  async getPlayers(): Promise<Player[]> {
    const response = await this.client.get<Player[]>('/players');
    return response.data;
  }

  async optimize(request: OptimizeRequest): Promise<OptimizeResponse> {
    const response = await this.client.post<OptimizeResponse>('/optimize', request);
    return response.data;
  }

  async analyzeSquad(squad: Player[], tactic?: TacticName, formation?: string): Promise<AnalyzeResponse> {
    const response = await this.client.post<AnalyzeResponse>('/analyze-squad', {
      squad: squad.map(p => p.id),
      tactic,
      formation,
      objectivePrompt: `Analyze this XI for ${formation ?? '4-3-3'} with ${tactic ?? 'Gegenpress'}.`,
    });
    return response.data;
  }

  async getDraftAnalysis(p1Squad: Player[], p2Squad: Player[], options?: DraftAnalysisOptions): Promise<DraftAnalysisResponse> {
    const response = await this.client.post<DraftAnalysisResponse>('/draft-analysis', {
      p1_squad: p1Squad.map(p => p.id),
      p2_squad: p2Squad.map(p => p.id),
      ...options,
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
