import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, UserCheck, FileText, Search, AlertCircle, FileCheck,
  Brain, Mic, Kanban as KanbanIcon, MessageSquare, Sun, Moon, Bell, LogOut,
  Sparkles, Menu, X, ChevronRight, CheckCircle2, Shield, Bookmark, Clock
} from 'lucide-react';
import { useAuth } from '../lib/auth';
import { useTheme } from '../lib/theme';
import { CareerAssistantDrawer } from '../components/CareerAssistantDrawer';
import { api } from '../services/api';
import { NotificationItem } from '../types';

export const DashboardLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isNotifOpen, setIsNotifOpen] = useState(false);

  useEffect(() => {
    api.notifications.list()
      .then(setNotifications)
      .catch(() => {});
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAllRead = async () => {
    try {
      await api.notifications.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch {
      // fallback
    }
  };

  const primaryNavItems = [
    { name: 'Agent Workspace', path: '/workspace', icon: Sparkles, badge: 'Primary' },
    { name: 'Agent Runs', path: '/agent-runs', icon: Clock },
    { name: 'Opportunities', path: '/internships', icon: Search },
    { name: 'Applications', path: '/applications', icon: KanbanIcon || LayoutDashboard },
  ];

  const secondaryNavItems = [
    { name: 'Resume Studio', path: '/resume-studio', icon: FileText },
    { name: 'Skill Gap Matrix', path: '/skill-gaps', icon: AlertCircle },
    { name: 'Interview Prep', path: '/interview-prep', icon: Brain },
    { name: 'AI Mock Interview', path: '/mock-interview', icon: Mic, badge: 'Voice' },
    { name: 'Profile Wizard', path: '/profile-wizard', icon: UserCheck },
    { name: 'Saved Jobs', path: '/saved-jobs', icon: Bookmark },
  ];

  if (user?.role === 'admin') {
    secondaryNavItems.push({ name: 'Admin Portal', path: '/admin', icon: Shield, badge: 'Admin' });
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col md:flex-row">
      {/* Mobile Top Header */}
      <header className="md:hidden flex items-center justify-between p-4 border-b border-border bg-card">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground font-bold text-base shadow-sm">
            CF
          </div>
          <span className="font-bold text-lg tracking-tight">CareerForge AI</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsAssistantOpen(true)}
            className="p-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20"
          >
            <Sparkles className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 rounded-lg hover:bg-accent text-muted-foreground"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 z-40 h-screen w-64 border-r border-border bg-card/95 backdrop-blur flex flex-col transition-transform duration-300 ease-in-out ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-border/80 flex items-center justify-between">
          <NavLink to="/workspace" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground font-black text-lg shadow-md shadow-primary/20">
              CF
            </div>
            <div>
              <h1 className="font-bold text-base tracking-tight leading-none">CareerForge</h1>
              <p className="text-[11px] text-muted-foreground mt-0.5 font-medium">Autonomous Task Agent</p>
            </div>
          </NavLink>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-4">
          {/* Primary Agent Flow */}
          <div className="space-y-1">
            <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/80 mb-1">
              Autonomous Agent
            </div>
            {primaryNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path === '/workspace' && location.pathname === '/dashboard');
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-sm shadow-primary/30'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent/60'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                  {item.badge && (
                    <span className="ml-auto text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full bg-accent/20 text-accent">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </div>

          {/* Secondary Tools */}
          <div className="space-y-1 pt-2 border-t border-border/60">
            <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/80 mb-1">
              Career Intelligence Tools
            </div>
            {secondaryNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-accent text-foreground font-semibold shadow-sm'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent/40'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 shrink-0" />
                  <span>{item.name}</span>
                  {item.badge === 'Voice' && (
                    <span className="ml-auto text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full bg-accent/20 text-accent">
                      Voice
                    </span>
                  )}
                  {item.badge === 'Admin' && (
                    <span className="ml-auto text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full bg-rose-500/20 text-rose-600 dark:text-rose-400">
                      Admin
                    </span>
                  )}
                </NavLink>
              );
            })}
          </div>
        </nav>

        {/* AI Assistant Banner Card */}
        <div className="p-3 m-3 rounded-2xl bg-gradient-to-br from-primary/10 via-accent/10 to-primary/5 border border-primary/20">
          <div className="flex items-center gap-2 mb-1.5">
            <Sparkles className="w-4 h-4 text-primary" />
            <h4 className="text-xs font-semibold">AI Assistant Ready</h4>
          </div>
          <p className="text-[11px] text-muted-foreground mb-2.5">Ask questions about jobs, gaps, and preparation.</p>
          <button
            onClick={() => setIsAssistantOpen(true)}
            className="w-full py-1.5 px-3 rounded-lg text-xs font-medium bg-primary text-primary-foreground hover:opacity-90 transition flex items-center justify-center gap-1.5"
          >
            Launch Chat <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        {/* User Profile & Logout Footer */}
        <div className="p-4 border-t border-border/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center font-bold text-xs uppercase text-secondary-foreground shrink-0">
              {user?.full_name ? user.full_name[0] : 'S'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold truncate">{user?.full_name || 'Student'}</p>
              <p className="text-[11px] text-muted-foreground truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            title="Logout"
            className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="sticky top-0 z-30 h-16 border-b border-border bg-card/80 backdrop-blur-md px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-base font-semibold hidden sm:block">
              {[...primaryNavItems, ...secondaryNavItems].find(n => n.path === location.pathname)?.name || 'CareerForge AI'}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            {/* Quick AI Launch Button */}
            <button
              onClick={() => setIsAssistantOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20 transition"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ask Assistant</span>
            </button>

            {/* Notifications Dropdown */}
            <div className="relative">
              <button
                onClick={() => setIsNotifOpen(!isNotifOpen)}
                className="p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent relative transition"
              >
                <Bell className="w-4 h-4" />
                {unreadCount > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-card" />
                )}
              </button>

              {isNotifOpen && (
                <div className="absolute right-0 mt-2 w-80 rounded-2xl bg-card border border-border shadow-xl p-3 z-50 animate-in fade-in zoom-in-95">
                  <div className="flex items-center justify-between pb-2 mb-2 border-b border-border">
                    <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Notifications</span>
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllRead}
                        className="text-[11px] text-primary hover:underline font-medium"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <p className="text-xs text-muted-foreground text-center py-4">No notifications</p>
                    ) : (
                      notifications.slice(0, 5).map((n) => (
                        <div
                          key={n.id}
                          className={`p-2.5 rounded-xl text-xs transition ${
                            n.read ? 'bg-muted/30' : 'bg-primary/5 border border-primary/20 font-medium'
                          }`}
                        >
                          <div className="flex items-center gap-1.5 mb-1 text-primary font-semibold">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>{n.title}</span>
                          </div>
                          <p className="text-muted-foreground leading-relaxed">{n.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent transition"
              title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
            </button>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>

      {/* Floating AI Career Assistant Drawer */}
      <CareerAssistantDrawer
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
      />
    </div>
  );
};

export default DashboardLayout;
