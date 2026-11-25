/**
 * TypeScript type definitions for AI Project Guide
 */

export type PageView =
  | 'dashboard'
  | 'project-guidance'
  | 'workspace'
  | 'ai-agents'
  | 'settings';

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  institution?: string;
  avatar?: string;
}

export interface ProjectDomainOption {
  value: string;
  label: string;
}

export interface TechnologyItem {
  technology_name?: string;
  tech_name?: string;
  category: string;
  role_in_project?: string;
  role?: string;
  why_suitable?: string;
  why_recommended?: string;
  implementation_guide?: string;
  cost_tier?: string;
  license_type?: string;
  free_tier_limits?: string;
  free_alternative?: string;
  alternatives?: string[];
}

export interface AIToolAdvisor {
  tool_name: string;
  development_activity: string;
  how_to_use: string;
  when_to_use: string;
  free_alternative: string;
}

export interface ProjectAnalysis {
  project_title: string;
  domain: string;
  problem_statement: string;
  existing_limitations: string[];
  proposed_solution: string;
  target_users: string[];
  main_objectives: string[];
  expected_outcomes: string[];
  unique_selling_proposition: string;
  innovation_opportunities: string[];
  feasibility_assessment: string;
  project_complexity: string;
  follow_up_questions?: string[];
}

export interface TechnologyStack {
  project_title: string;
  technology_recommendations?: TechnologyItem[];
  technologies?: TechnologyItem[];
  ai_tool_advisors?: AIToolAdvisor[];
  ai_tools?: string[];
  rationale_summary?: string;
  summary?: string;
}

export interface ModuleArchitectureItem {
  module_name: string;
  responsibility: string;
  technologies_used: string[];
  inputs: string;
  outputs: string;
}

export interface APIEndpointSuggestion {
  method: string;
  path: string;
  description: string;
}

export interface ArchitectureResponse {
  project_title: string;
  architecture_pattern?: string;
  high_level_overview?: string;
  frontend_layer?: string;
  frontend_backend_flow?: string;
  backend_layer?: string;
  database_architecture?: string;
  data_layer?: string;
  data_flow_explanation?: string;
  ai_pipeline_layer?: string;
  infrastructure_layer?: string;
  mermaid_diagram: string;
  component_interactions?: string[];
  module_breakdown?: ModuleArchitectureItem[];
  api_endpoint_suggestions?: APIEndpointSuggestion[];
}

export interface RoadmapPhase {
  phase_number: number;
  phase_title?: string;
  phase_name?: string;
  estimated_duration?: string;
  duration?: string;
  tasks?: string[];
  dependencies?: string[];
  required_tools?: string[];
  expected_output?: string;
  completion_checklist?: string[];
  key_milestones?: string[];
  deliverables?: string[];
  suggested_tools?: string[];
}

export interface DeploymentGuidance {
  hosting_platform: string;
  environment_variables_checklist: string[];
  step_by_step_deployment: string[];
  testing_strategy: string[];
  maintenance_practices: string[];
}

export interface RoadmapResponse {
  project_title: string;
  total_estimated_duration?: string;
  total_duration?: string;
  phases: RoadmapPhase[];
  deployment_and_testing?: DeploymentGuidance;
  risk_mitigation?: string[];
}

export interface ModuleCodingStep {
  module_name: string;
  purpose: string;
  folder_structure: string;
  implementation_steps: string[];
  example_code_snippet: string;
  required_dependencies: string[];
  testing_instructions: string;
  common_errors_and_solutions: string[];
}

export interface AICopyReadyPrompt {
  target_tool: string;
  use_case: string;
  prompt_text: string;
}

export interface CodingPromptItem {
  module_name: string;
  description?: string;
  purpose?: string;
  recommended_files?: string[];
  claude_coding_prompt?: string;
  antigravity_coding_prompt?: string;
  example_code_snippet?: string;
  testing_steps?: string[];
}

export interface CodingPromptsResponse {
  project_title: string;
  modules?: CodingPromptItem[];
  module_walkthroughs?: ModuleCodingStep[];
  copy_ready_prompts?: AICopyReadyPrompt[];
}

export interface DocumentationResponse {
  project_title: string;
  abstract: string;
  introduction: string;
  problem_statement?: string;
  literature_review_outline?: string[];
  literature_survey_summary?: string;
  objectives?: string[];
  methodology?: string;
  system_methodology?: string;
  proposed_architecture_summary?: string;
  implementation_plan_summary?: string;
  testing_methodology?: string;
  results_section_template?: string;
  experimental_results_plan?: string;
  conclusion?: string;
  conclusion_and_future_work?: string;
  future_scope?: string[];
  references_structure?: string[];
}

export interface FullProjectBlueprint {
  project_title?: string;
  analysis: ProjectAnalysis;
  technology_stack: TechnologyStack;
  architecture: ArchitectureResponse;
  roadmap: RoadmapResponse;
  coding_prompts?: CodingPromptsResponse;
  coding_and_prompts?: CodingPromptsResponse;
  documentation: DocumentationResponse;
  metadata?: Record<string, any>;
}

// Hackathon Guidance Types
export interface HackathonIdeaItem {
  idea_id: number;
  project_title: string;
  problem_solved: string;
  proposed_solution: string;
  innovation_angle: string;
  key_features: string[];
  suggested_tech_stack: string[];
  technical_feasibility: string;
  expected_impact: string;
  demo_potential: string;
}

export interface IdeaScoreBreakdown {
  idea_id: number;
  project_title: string;
  problem_relevance: number;
  innovation: number;
  technical_feasibility: number;
  social_business_impact: number;
  demo_potential: number;
  time_feasibility: number;
  weighted_total_score: number;
  strengths: string[];
  risks_and_pitfalls: string[];
}

export interface IdeaEvaluationResponse {
  scoring_method: string;
  ranked_ideas: IdeaScoreBreakdown[];
  recommended_idea_id: number;
  recommended_idea_title: string;
  recommendation_rationale: string;
  disclaimer: string;
}

export interface MVPPlanResponse {
  project_title: string;
  core_mvp_summary: string;
  must_have_features: string[];
  should_have_features: string[];
  nice_to_have_features: string[];
  minimal_demo_flow: string[];
  potential_failure_points: string[];
}

export interface RoadmapTimeBlock {
  time_window: string;
  focus_milestone: string;
  frontend_tasks: string[];
  backend_ai_tasks: string[];
  integration_and_testing: string[];
  deliverable: string;
}

export interface HackathonRoadmapResponse {
  hackathon_duration: string;
  total_hours: number;
  time_blocks: RoadmapTimeBlock[];
  reserved_buffer_hours: number;
  submission_checklist: string[];
}

export interface MemberAssignment {
  member_identifier: string;
  assigned_role: string;
  key_responsibilities: string[];
  specific_tasks: string[];
  expected_deliverables: string[];
}

export interface TeamAllocationResponse {
  project_title: string;
  team_size: number;
  member_assignments: MemberAssignment[];
  coordination_practices: string[];
}

export interface TechTierItem {
  tech_name: string;
  category: string;
  license_type: string;
  why_recommended: string;
  free_tier_limits: string;
  free_alternative?: string;
}

export interface HackathonDevGuidanceResponse {
  project_title: string;
  recommended_tech_stack: TechTierItem[];
  database_design_summary: string;
  suggested_api_endpoints: string[];
  integration_quickstart_guide: string[];
  copy_ready_claude_prompt: string;
  copy_ready_antigravity_prompt: string;
  testing_and_sanity_checks: string[];
  deployment_plan: string;
}

export interface JudgeQAItem {
  anticipated_question: string;
  suggested_answer: string;
  highlight_aspect: string;
}

export interface PitchAndDemoResponse {
  project_title: string;
  pitch_30_seconds: string;
  pitch_1_minute: string;
  pitch_3_minute: string;
  pitch_5_minute: string;
  live_demo_walkthrough: string[];
  technical_explanation: string;
  innovation_explanation: string;
  judge_qa_preparation: JudgeQAItem[];
  future_scope: string[];
}

export interface FullHackathonStrategy {
  hackathon_name: string;
  duration: string;
  analysis: any;
  ideas: { hackathon_name: string; ideas: HackathonIdeaItem[] };
  evaluation: IdeaEvaluationResponse;
  mvp_plan: MVPPlanResponse;
  roadmap: HackathonRoadmapResponse;
  team_allocation: TeamAllocationResponse;
  development_guidance: HackathonDevGuidanceResponse;
  pitch_and_demo: PitchAndDemoResponse;
}

// Workspace Project Tracker Types
export interface WorkspaceTask {
  id: string;
  title: string;
  category: 'frontend' | 'backend' | 'ai' | 'docs' | 'pitch';
  status: 'pending' | 'in_progress' | 'completed';
  assignedTo?: string;
}

export interface WorkspaceProject {
  id: string;
  title: string;
  domain: string;
  description?: string;
  mode: 'project' | 'hackathon';
  progress: number;
  tasks: WorkspaceTask[];
  createdAt: string;
  updatedAt: string;
  blueprint?: any;
  strategy?: any;
}

export interface GitHubScaffoldResponse {
  readme_content: string;
  gitignore_content: string;
  directory_structure: string;
  milestone_issues: Array<{
    title: string;
    body: string;
    labels: string[];
  }>;
  summary: string;
}

export interface PresentationInput {
  title: string;
  description: string;
  domain: string;
  problem_statement: string;
  target_audience: string;
  key_features: string[];
  architecture_overview: string;
  frontend_stack: string[];
  backend_stack: string[];
  database_stack: string[];
  deployment_target: string;
  phases: Array<{ name: string; duration: string; deliverables: string[] }>;
  future_scope: string[];
}
