export type VerificationStatus = "VERIFIED" | "PARTIAL" | "UNVERIFIED";

export interface OntologyReference {
  concept_id: string;
  domain: string;
  truth_level: number;
}

export interface ReasoningTrace {
  sources_consulted: string[];
  retrieval_confidence: number;
}

export interface RoutingMetadata {
  query_type: string;
  route: string;
  router_latency_ms?: number;
}

export interface CoreAlignment {
  read_only?: boolean;
  source?: string;
  [key: string]: unknown;
}

export interface PresentationMetadata {
  summary?: string;
  body?: string;
  details?: string;
  source?: string;
  paragraphs?: string[];
  bullet_points?: string[];
  disclaimer?: string;
  fallback_mode?: boolean;
}

export interface UniGuruResponse {
  decision: string;
  answer: string;
  verification_status: VerificationStatus;
  ontology_reference?: OntologyReference;
  enforcement_signature?: string;
  reasoning_trace?: ReasoningTrace;
  routing?: RoutingMetadata;
  core_alignment?: CoreAlignment;
  integration_notes?: string[];
  raw_answer?: string;
  presentation?: PresentationMetadata;
}
