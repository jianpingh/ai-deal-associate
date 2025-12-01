export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface DealState {
  messages: Message[];
  // Add other state properties here
}
