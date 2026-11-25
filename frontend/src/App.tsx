import { useState, useEffect } from 'react';
import type { PageView, User } from './types';
import { Sidebar } from './components/Sidebar';
import { AppHeader } from './components/AppHeader';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectGuidancePage } from './pages/ProjectGuidancePage';
import { ProjectWorkspacePage } from './pages/ProjectWorkspacePage';
import { AIAgentsPage } from './pages/AIAgentsPage';
import { SettingsPage } from './pages/SettingsPage';
import { ToastProvider } from './components/Toast';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageView>('dashboard');
  const [user, setUser] = useState<User | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  // Load user profile and sidebar preference on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user_profile');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {}
    }

    const savedCollapsed = localStorage.getItem('sidebar_collapsed');
    if (savedCollapsed !== null) {
      setSidebarCollapsed(savedCollapsed === 'true');
    }
  }, []);

  const handleToggleCollapse = () => {
    const nextState = !sidebarCollapsed;
    setSidebarCollapsed(nextState);
    localStorage.setItem('sidebar_collapsed', String(nextState));
  };

  return (
    <ToastProvider>
      <div className="min-h-screen bg-[#090D18] text-[#F8FAFC] flex font-sans selection:bg-[#638BFF] selection:text-white relative antialiased">
        <div className="flex-1 flex w-full min-h-screen">
          {/* Collapsible Sidebar */}
          <Sidebar
            currentPage={currentPage}
            onNavigate={setCurrentPage}
            collapsed={sidebarCollapsed}
            onToggleCollapse={handleToggleCollapse}
            mobileOpen={mobileMenuOpen}
            onCloseMobile={() => setMobileMenuOpen(false)}
            user={user}
          />

          {/* Right Main Content Area */}
          <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
            <AppHeader
              currentPage={currentPage}
              onNavigate={setCurrentPage}
              onOpenMobileMenu={() => setMobileMenuOpen(true)}
              user={user}
            />

            <main className="flex-1 flex flex-col">
              {currentPage === 'dashboard' && <DashboardPage user={user} onNavigate={setCurrentPage} />}
              {currentPage === 'project-guidance' && <ProjectGuidancePage />}
              {currentPage === 'workspace' && <ProjectWorkspacePage />}
              {currentPage === 'ai-agents' && <AIAgentsPage />}
              {currentPage === 'settings' && <SettingsPage user={user} onUpdateUser={setUser} />}
            </main>

            {/* Clean Footer */}
            <footer className="border-t border-[#26344A]/60 bg-[#090D18] py-3.5 px-6 text-[11px] text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[#27C995]" />
                <span className="text-slate-400 font-medium">AI Project Guide</span>
                <span>•</span>
                <span>Local AI Planning Engine</span>
              </div>
              <div className="text-slate-500 font-mono text-[10px]">
                Ollama Local Inference (qwen3:4b) • FastAPI • SQLite
              </div>
            </footer>
          </div>
        </div>
      </div>
    </ToastProvider>
  );
}

export default App;
