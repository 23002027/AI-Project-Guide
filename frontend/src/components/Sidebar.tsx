import React from 'react';
import type { PageView, User as UserType } from '../types';
import {
  LayoutDashboard,
  GraduationCap,
  Briefcase,
  Bot,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  X,
  HardDrive,
} from 'lucide-react';

interface SidebarProps {
  currentPage: PageView;
  onNavigate: (page: PageView) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  user?: UserType | null;
  onLogout?: () => void;
  onOpenAuth?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onNavigate,
  collapsed,
  onToggleCollapse,
  mobileOpen,
  onCloseMobile,
  user,
}) => {
  const navItems = [
    {
      id: 'dashboard' as PageView,
      label: 'Overview',
      icon: LayoutDashboard,
      badge: null,
      description: 'Project dashboard & metrics',
    },
    {
      id: 'project-guidance' as PageView,
      label: 'Project Guide',
      icon: GraduationCap,
      badge: null,
      description: 'AI Project specification & blueprints',
    },
    {
      id: 'workspace' as PageView,
      label: 'Workspace',
      icon: Briefcase,
      badge: null,
      description: 'Tasks, notes & deliverables',
    },
    {
      id: 'ai-agents' as PageView,
      label: 'AI Planning Agent',
      icon: Bot,
      badge: 'Ollama Live',
      badgeColor: 'text-[#27C995] bg-[#27C995]/15 border-[#27C995]/30',
      description: 'Local Ollama qwen3:4b planning engine',
    },
    {
      id: 'settings' as PageView,
      label: 'Settings',
      icon: Settings,
      badge: null,
      description: 'Environment & local configuration',
    },
  ];

  const handleItemClick = (page: PageView) => {
    onNavigate(page);
    onCloseMobile();
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#0D1422] border-r border-[#26344A] select-none text-slate-300">
      {/* Brand Header */}
      <div className={`flex items-center justify-between h-16 border-b border-[#26344A]/80 px-4 ${collapsed ? 'justify-center' : ''}`}>
        <div
          onClick={() => handleItemClick('dashboard')}
          className="flex items-center space-x-3 cursor-pointer group overflow-hidden"
          title="AI Project Guide"
        >
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#638BFF] via-indigo-600 to-[#9B7BFF] flex items-center justify-center shrink-0 shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col leading-tight min-w-0">
              <span className="font-bold text-sm tracking-tight text-white group-hover:text-blue-200 transition-colors truncate">
                AI Project Guide
              </span>
              <span className="text-[10px] text-slate-400 font-medium tracking-wide">
                Local AI Planning Engine
              </span>
            </div>
          )}
        </div>

        {/* Mobile close button */}
        <button
          onClick={onCloseMobile}
          className="md:hidden text-slate-400 hover:text-white p-1 rounded-lg hover:bg-[#131D2E]"
          aria-label="Close mobile menu"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = currentPage === item.id;
          const Icon = item.icon;

          return (
            <div key={item.id} className="relative group">
              <button
                onClick={() => handleItemClick(item.id)}
                className={`w-full flex items-center rounded-xl text-xs font-medium transition-all duration-150 ${
                  collapsed ? 'justify-center p-3' : 'px-3.5 py-2.5 space-x-3'
                } ${
                  isActive
                    ? 'bg-[#638BFF]/15 text-[#638BFF] border border-[#638BFF]/30 font-semibold shadow-sm shadow-[#638BFF]/10'
                    : 'text-slate-300 hover:text-white hover:bg-[#131D2E] border border-transparent'
                }`}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    isActive ? 'text-[#638BFF]' : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                {!collapsed && (
                  <div className="flex-1 flex items-center justify-between text-left truncate">
                    <span className="truncate">{item.label}</span>
                    {item.badge && (
                      <span
                        className={`text-[9px] px-1.5 py-0.5 rounded-md font-semibold border ${
                          item.badgeColor || 'text-blue-300 bg-blue-500/10 border-blue-500/20'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </button>

              {/* Collapsed Tooltip */}
              {collapsed && (
                <div className="hidden md:group-hover:flex absolute left-full ml-2 top-1/2 -translate-y-1/2 z-50 bg-[#131D2E] text-white text-xs px-2.5 py-1.5 rounded-lg border border-[#26344A] shadow-xl whitespace-nowrap flex-col pointer-events-none">
                  <span className="font-semibold text-white">{item.label}</span>
                  <span className="text-[10px] text-slate-400">{item.description}</span>
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* Local Workspace Status & Collapse Toggle */}
      <div className="p-3 border-t border-[#26344A]/80 space-y-2 bg-[#0A101C]/60">
        {/* Local Single-User Card */}
        <div
          className={`flex items-center rounded-xl p-2 bg-[#131D2E]/80 border border-[#26344A] ${
            collapsed ? 'justify-center' : 'space-x-2.5'
          }`}
          title="Local Workspace (Single-User Mode)"
        >
          <div className="w-7 h-7 rounded-lg bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-[#27C995] shrink-0">
            <HardDrive className="w-3.5 h-3.5" />
          </div>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <div className="text-xs font-semibold text-white truncate">
                {user?.name || 'Local Workspace'}
              </div>
              <div className="text-[10px] text-[#27C995] font-medium flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#27C995]" />
                <span className="truncate">Single-User Mode</span>
              </div>
            </div>
          )}
        </div>

        {/* Desktop Collapse Trigger */}
        <div className="hidden md:flex justify-end pt-1">
          <button
            onClick={onToggleCollapse}
            className="w-full flex items-center justify-center text-slate-400 hover:text-white py-1.5 px-2 rounded-lg hover:bg-[#131D2E] text-xs transition-colors space-x-2"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <>
                <ChevronLeft className="w-4 h-4" />
                <span className="text-[11px]">Collapse Menu</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={`hidden md:flex flex-col shrink-0 transition-all duration-200 z-30 sticky top-0 h-screen ${
          collapsed ? 'w-[72px]' : 'w-[250px]'
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {mobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden animate-in fade-in duration-200"
        />
      )}

      {/* Mobile Drawer Panel */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-[270px] transform transition-transform duration-200 ease-out md:hidden ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </div>
    </>
  );
};
