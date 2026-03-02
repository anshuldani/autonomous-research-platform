export type MessageRole = "user" | "assistant" | "system";

export interface QualityRecord {
  iteration: number;
  overall: number;
  scores: {
    depth_score: number;
    relevance_score: number;
    clarity_score: number;
    coverage_score: number;
    weaknesses?: string[];
    suggestions?: string[];
  };
}

export interface ResearchResult {
  summary: string;
  quality_history: QualityRecord[];
  iterations: number;
  improvement_history: string[];
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  // Only set on assistant messages that contain a completed research result
  result?: ResearchResult;
  // Timestamp
  createdAt: Date;
}

export type ResearchStatus =
  | "idle"
  | "researching"
  | "done"
  | "error";
