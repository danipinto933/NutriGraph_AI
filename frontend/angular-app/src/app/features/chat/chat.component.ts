import { Component, ElementRef, ViewChild, OnInit, AfterViewChecked, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatMessage } from '../../core/services/chat.service';
import { AuthService } from '../../core/services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="dashboard-layout animate-fade-in">
      <!-- Sidebar -->
      <aside class="sidebar glass-panel">
        <div class="brand">
          <h2 class="text-gradient">NutriGraph AI</h2>
        </div>

        <div class="past-conversations">
          <h4 class="sidebar-title">Conversaciones Anteriores</h4>
          <button class="btn-primary" style="width: 100%; margin-bottom: 1rem; padding: 0.5rem; font-size: 0.85rem;" (click)="newConversation()">+ Nueva Conversación</button>
          
          <div *ngIf="chatService.pastConversations().length === 0" class="empty-history" style="text-align: center; color: var(--text-secondary); font-size: 0.85rem; padding-top: 1rem;">
            No hay conversaciones guardadas aún.
          </div>
          
          <div *ngFor="let conv of chatService.pastConversations()" 
               class="conv-item" 
               [class.active]="conv.session_id === sessionId"
               (click)="loadConversation(conv.session_id)">
            <span class="icon">💬</span> {{ conv.title }}
          </div>
        </div>
        
        <div class="sidebar-bottom">
          <div class="gear-menu-container">
            <button class="icon-btn gear-btn" (click)="toggleMenu()">
              ⚙️
            </button>
            <div class="gear-menu" *ngIf="showMenu">
              <button class="menu-item" (click)="goToProfile()">👤 Perfil</button>
              <button class="menu-item text-error" (click)="logout()">🚪 Salir</button>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Chat Area -->
      <main class="chat-main">
        <div class="chat-header glass-panel">
          <h3>Asistente Nutricional</h3>
          <p class="subtitle">Con tecnología GraphRAG y LlamaIndex</p>
        </div>

        <div class="chat-messages" #scrollMe>
          <div *ngIf="chatService.messages().length === 0" class="empty-state">
            <div class="icon">🥗</div>
            <h2>¿Qué te gustaría comer hoy, {{ authService.currentUser()?.first_name }}?</h2>
            <p>Pregúntame sobre recetas, dietas sin alérgenos o planes nutricionales.</p>
          </div>

          <div 
            *ngFor="let msg of chatService.messages()" 
            class="message-wrapper" 
            [ngClass]="{'is-user': msg.role === 'user'}"
          >
            <div class="message-bubble glass-panel" [ngClass]="{'streaming': msg.isStreaming}">
              <div class="role-badge">{{ msg.role === 'user' ? 'Tú' : 'AI' }}</div>
              <div class="content" [innerHTML]="formatMessage(msg.content)"></div>
            </div>
          </div>
          
          <div *ngIf="chatService.isAgentTyping() && !isReceivingStream()" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>

        <div class="chat-input-area glass-panel">
          <input 
            type="text" 
            class="input-glass chat-input" 
            [(ngModel)]="userInput" 
            (keyup.enter)="sendMessage()"
            placeholder="Escribe tu consulta nutricional..."
            [disabled]="chatService.isAgentTyping()"
          >
          <button 
            class="btn-primary send-btn" 
            (click)="sendMessage()" 
            [disabled]="!userInput.trim() || chatService.isAgentTyping()"
          >
            Enviar
          </button>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .dashboard-layout {
      display: flex;
      height: 100vh;
      overflow: hidden;
      background: radial-gradient(circle at center, rgba(15,17,21,1) 0%, rgba(10,12,15,1) 100%);
    }

    /* Sidebar */
    .sidebar {
      width: 280px;
      margin: 1rem;
      display: flex;
      flex-direction: column;
      border-radius: var(--border-radius-lg);
    }
    .brand {
      padding: 2rem;
      border-bottom: 1px solid var(--border-light);
    }
    .user-info {
      padding: 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      border-bottom: 1px solid var(--border-light);
    }
    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
    }
    .user-details .name { font-weight: 500; }
    .user-details .email { font-size: 0.8rem; color: var(--text-muted); }
    .past-conversations {
      flex: 1;
      padding: 1rem;
      overflow-y: auto;
    }
    .sidebar-title {
      font-size: 0.85rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 1rem;
    }
    .conv-item {
      padding: 0.75rem;
      color: var(--text-primary);
      border-radius: var(--border-radius-sm);
      cursor: pointer;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
      transition: background 0.2s;
    }
    .conv-item.active {
      background: rgba(0, 210, 255, 0.1);
      border-left: 3px solid var(--accent-primary);
    }
    .conv-item:hover {
      background: var(--bg-glass-hover);
    }
    .sidebar-bottom {
      padding: 1rem;
      border-top: 1px solid var(--border-light);
    }
    .gear-menu-container {
      position: relative;
    }
    .icon-btn {
      background: transparent;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: var(--text-secondary);
      transition: transform 0.2s;
    }
    .icon-btn:hover {
      transform: rotate(45deg);
      color: var(--accent-primary);
    }
    .gear-menu {
      position: absolute;
      bottom: 40px;
      left: 0;
      background: var(--bg-secondary);
      border: 1px solid var(--border-light);
      border-radius: var(--border-radius-sm);
      display: flex;
      flex-direction: column;
      min-width: 150px;
      overflow: hidden;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .menu-item {
      padding: 0.75rem 1rem;
      background: transparent;
      border: none;
      color: var(--text-primary);
      text-align: left;
      cursor: pointer;
      font-size: 0.9rem;
    }
    .menu-item:hover {
      background: var(--bg-glass-hover);
    }
    .text-error { color: var(--error); }
    .text-error:hover { background: rgba(239, 68, 68, 0.1); color: var(--error); }

    /* Main Chat */
    .chat-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 1rem 1rem 1rem 0;
    }
    .chat-header {
      padding: 1.5rem 2rem;
      margin-bottom: 1rem;
      border-radius: var(--border-radius-lg);
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .chat-header h3 { margin: 0; }
    .chat-header .subtitle { font-size: 0.85rem; color: var(--text-secondary); }

    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .chat-messages::-webkit-scrollbar { width: 8px; }
    .chat-messages::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 4px; }
    
    .empty-state {
      margin: auto;
      text-align: center;
      color: var(--text-secondary);
    }
    .empty-state .icon { font-size: 4rem; margin-bottom: 1rem; }

    .message-wrapper {
      display: flex;
      justify-content: flex-start;
      padding-right: 20%;
    }
    .message-wrapper.is-user {
      justify-content: flex-end;
      padding-right: 0;
      padding-left: 20%;
    }
    
    .message-bubble {
      padding: 1.5rem;
      border-radius: var(--border-radius-lg);
      position: relative;
    }
    .message-wrapper.is-user .message-bubble {
      background: rgba(0, 210, 255, 0.05);
      border-color: rgba(0, 210, 255, 0.2);
    }
    .role-badge {
      position: absolute;
      top: -10px;
      left: 20px;
      background: var(--bg-secondary);
      padding: 2px 10px;
      font-size: 0.75rem;
      border-radius: 12px;
      border: 1px solid var(--border-light);
      color: var(--text-secondary);
    }
    .message-wrapper.is-user .role-badge {
      left: auto;
      right: 20px;
      background: var(--accent-primary);
      color: var(--bg-primary);
      border: none;
      font-weight: 600;
    }
    
    .content {
      line-height: 1.6;
      white-space: pre-wrap;
    }
    .streaming .content::after {
      content: '▋';
      animation: blink 1s step-end infinite;
      color: var(--accent-primary);
    }

    .chat-input-area {
      display: flex;
      gap: 1rem;
      padding: 1rem;
      border-radius: var(--border-radius-lg);
      margin-top: 1rem;
    }
    .chat-input {
      flex: 1;
      border: none;
      background: rgba(0,0,0,0.3);
    }
    .send-btn {
      padding: 0 2rem;
    }

    /* Typing Indicator */
    .typing-indicator {
      display: flex;
      gap: 5px;
      padding: 1rem;
      opacity: 0.7;
    }
    .typing-indicator span {
      width: 8px;
      height: 8px;
      background: var(--accent-primary);
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out both;
    }
    .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
    .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

    @keyframes blink { 50% { opacity: 0; } }
    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }
  `]
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('scrollMe') private myScrollContainer!: ElementRef;
  
  userInput: string = '';
  sessionId: string = crypto.randomUUID(); // Persist session during component lifecycle
  showMenu: boolean = false;

  constructor(
    public chatService: ChatService, 
    public authService: AuthService,
    public router: Router
  ) {
    // Auto-scroll on new messages via Signal effect
    effect(() => {
      // Accessing signals registers dependency
      const msgs = this.chatService.messages();
      setTimeout(() => this.scrollToBottom(), 100);
    });
  }

  ngOnInit() {
    this.sessionId = crypto.randomUUID();
    this.chatService.clearChat();
    const userId = this.authService.currentUser()?.email;
    if (userId) {
      this.chatService.loadConversations(userId);
    }
  }

  newConversation() {
    this.sessionId = crypto.randomUUID();
    this.chatService.clearChat();
  }

  loadConversation(sessionId: string) {
    this.sessionId = sessionId;
    this.chatService.loadConversationHistory(sessionId);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.myScrollContainer.nativeElement.scrollTop = this.myScrollContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  sendMessage(): void {
    if (!this.userInput.trim() || this.chatService.isAgentTyping()) return;
    
    const text = this.userInput;
    this.userInput = ''; // clear input immediately
    this.chatService.sendMessageStream(text, this.sessionId);
  }

  isReceivingStream(): boolean {
    const msgs = this.chatService.messages();
    if (msgs.length === 0) return false;
    return msgs[msgs.length - 1].isStreaming || false;
  }

  formatMessage(text: string): string {
    // Basic formatting for Markdown-like bold tags
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return formatted;
  }

  logout(): void {
    this.authService.logout();
  }

  toggleMenu(): void {
    this.showMenu = !this.showMenu;
  }

  goToProfile(): void {
    this.router.navigate(['/profile']);
  }
}
