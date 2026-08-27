import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { Sparkles, ArrowRight, Shield, CheckCircle2, Lock, Mail, AlertCircle, Loader2, UserCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const { login, loginAsDemo, loginAsAdmin } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoStudentLogin = async () => {
    setError('');
    setIsLoading(true);
    try {
      await loginAsDemo();
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Demo student login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoAdminLogin = async () => {
    setError('');
    setIsLoading(true);
    try {
      await loginAsAdmin();
      navigate('/admin');
    } catch (err: any) {
      setError(err.message || 'Demo admin login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Gradient Mesh */}
      <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 via-accent/5 to-transparent pointer-events-none" />

      <div className="w-full max-w-md z-10 space-y-6">
        {/* Brand */}
        <div className="text-center">
          <Link to="/" className="inline-flex w-12 h-12 rounded-2xl bg-gradient-to-tr from-primary to-accent items-center justify-center text-primary-foreground font-bold text-xl shadow-lg shadow-primary/30 mb-3">
            CB
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">Sign In to CareerBridge</h1>
          <p className="text-sm text-muted-foreground mt-1.5">
            "From Resume to Internship — AI-powered matching and preparation."
          </p>
        </div>

        {/* Card */}
        <div className="p-6 sm:p-8 rounded-3xl bg-card/70 backdrop-blur-md border border-border/80 shadow-2xl space-y-5">
          {error && (
            <div className="p-3.5 rounded-2xl bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* 1-Click Quick Logins Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              type="button"
              onClick={handleDemoStudentLogin}
              disabled={isLoading}
              className="py-2.5 px-3 rounded-xl font-semibold text-xs bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md shadow-primary/20 hover:opacity-95 transition flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Demo Student</span>
            </button>

            <button
              type="button"
              onClick={handleDemoAdminLogin}
              disabled={isLoading}
              className="py-2.5 px-3 rounded-xl font-semibold text-xs border border-border bg-background hover:bg-accent text-foreground transition flex items-center justify-center gap-1.5"
            >
              <Shield className="w-3.5 h-3.5 text-primary" />
              <span>Demo Admin</span>
            </button>
          </div>

          <div className="relative flex items-center justify-center">
            <div className="border-t border-border w-full" />
            <span className="bg-card px-3 text-[11px] uppercase tracking-wider text-muted-foreground font-semibold">Or sign in with email</span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3.5 top-3.5 text-muted-foreground" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@careerbridge.ai"
                  className="w-full bg-background border border-input rounded-xl pl-10 pr-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3.5 top-3.5 text-muted-foreground" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-background border border-input rounded-xl pl-10 pr-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 rounded-xl font-semibold text-sm bg-primary text-primary-foreground hover:bg-primary/90 transition flex items-center justify-center gap-2 shadow-md shadow-primary/20"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-xs text-muted-foreground">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary font-semibold hover:underline">
              Create student account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
