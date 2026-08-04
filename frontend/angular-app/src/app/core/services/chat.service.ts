import { Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import { AuthService } from './auth.service';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface Conversation {
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly apiUrl = `${environment.chatApiUrl}/chat`;
  
  // State Signals
  public messages = signal<ChatMessage[]>([]);
  public pastConversations = signal<Conversation[]>([]);
  public isAgentTyping = signal<boolean>(false);
  public error = signal<string | null>(null);

  constructor(private authService: AuthService) {}

  async loadConversations(userId: string): Promise<void> {
    const token = this.authService.getToken();
    try {
      const response = await fetch(`${this.apiUrl}/conversations?user_id=${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        this.pastConversations.set(data.conversations || []);
      }
    } catch (e) {
      console.error("Error loading conversations", e);
    }
  }

  async loadConversationHistory(sessionId: string): Promise<void> {
    const token = this.authService.getToken();
    this.messages.set([]); // Clear current
    try {
      const response = await fetch(`${this.apiUrl}/conversations/${sessionId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        const history: ChatMessage[] = (data.messages || []).map((m: any) => ({
          id: crypto.randomUUID(),
          role: m.role === 'ai' ? 'assistant' : 'user',
          content: m.content,
          timestamp: new Date(m.timestamp)
        }));
        this.messages.set(history);
      }
    } catch (e) {
      console.error("Error loading history", e);
    }
  }

  /**
   * Envía un mensaje al endpoint de streaming (SSE) y actualiza el DOM de forma progresiva
   * usando Signals (token by token). 
   */
  async sendMessageStream(messageText: string, sessionId: string): Promise<void> {
    if (!messageText.trim()) return;

    // Is this the first message in the chat? We'll refresh sidebar afterwards
    const isFirstMessage = this.messages().length === 0;

    // Add user message to UI immediately
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };
    this.messages.update(msgs => [...msgs, userMsg]);

    const token = this.authService.getToken();
    const userId = this.authService.currentUser()?.email;

    if (!userId) {
      this.error.set("Usuario no autenticado");
      return;
    }

    this.isAgentTyping.set(true);

    // Create an empty assistant message that will be populated via stream
    const assistantMsgId = crypto.randomUUID();
    const initialAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    };
    this.messages.update(msgs => [...msgs, initialAssistantMsg]);

    try {
      const response = await fetch(`${this.apiUrl}/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          message: messageText
        })
      });

      if (!response.ok || !response.body) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete events split by double newline
        const events = buffer.split('\n\n');
        // The last element is either empty (if buffer ended with \n\n) or a partial event
        buffer = events.pop() || '';

        for (const event of events) {
          const lines = event.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6).trim();
              if (dataStr === '[DONE]') {
                continue;
              }
              
              let isBackendError = false;
              let parsed;
              try {
                parsed = JSON.parse(dataStr);
                if (parsed.error) {
                  isBackendError = true;
                  throw new Error(parsed.error);
                }
                
                const tokenContent = parsed.content || '';
                // Append the token to the assistant's message content using Signals
                this.messages.update(msgs => msgs.map(msg => {
                  if (msg.id === assistantMsgId) {
                    return { ...msg, content: msg.content + tokenContent };
                  }
                  return msg;
                }));
              } catch (e) {
                // If the error is from the parsed response, propagate it
                if (isBackendError) {
                  throw e;
                }
                console.error("Error parsing SSE data", e, dataStr);
              }
            }
          }
        }
      }
      
      // Finished streaming
      this.messages.update(msgs => msgs.map(msg => 
        msg.id === assistantMsgId ? { ...msg, isStreaming: false } : msg
      ));
      
      if (isFirstMessage) {
         // Reload conversations so the sidebar updates automatically
         this.loadConversations(userId);
      }

    } catch (err: any) {
      this.error.set(err.message || 'Error communicating with AI agent');
      this.messages.update(msgs => msgs.map(msg => 
        msg.id === assistantMsgId ? { ...msg, content: 'Error de red. Intenta nuevamente.', isStreaming: false } : msg
      ));
    } finally {
      this.isAgentTyping.set(false);
    }
  }

  clearChat(): void {
    this.messages.set([]);
  }
}
