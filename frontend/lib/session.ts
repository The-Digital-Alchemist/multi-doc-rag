/**
 * Simple session management for Cortex RAG system
 * Auto-generates and persists session IDs
 */

const SESSION_KEY = 'cortex_session_id';

export class SessionManager {
  private sessionId: string | null = null;

  constructor() {
    // Load existing session from localStorage
    try {
      const stored = localStorage.getItem(SESSION_KEY);
      if (stored) {
        this.sessionId = stored;
      }
    } catch (error) {
      console.warn('Failed to load session from localStorage:', error);
    }
  }

  /**
   * Get the current session ID, creating a new one if none exists
   */
  getSessionId(): string {
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
      this.saveSession();
    }
    return this.sessionId;
  }

  /**
   * Clear the current session
   */
  clearSession(): void {
    this.sessionId = null;
    localStorage.removeItem(SESSION_KEY);
  }

  /**
   * Generate a unique session ID
   */
  private generateSessionId(): string {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
  }

  /**
   * Save session to localStorage
   */
  private saveSession(): void {
    try {
      if (this.sessionId) {
        localStorage.setItem(SESSION_KEY, this.sessionId);
      }
    } catch (error) {
      console.warn('Failed to save session to localStorage:', error);
    }
  }
}

// Export a singleton instance
export const sessionManager = new SessionManager();
