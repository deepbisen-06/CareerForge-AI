import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User, GraduationCap, Code2, FolderGit2, Briefcase, Compass,
  ChevronRight, ChevronLeft, Check, Plus, Trash2, Save, Loader2, Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { Profile, Education, Experience, Project, UserSkillItem } from '../types';

export const ProfileWizard: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Form State
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [careerObjective, setCareerObjective] = useState('');
  
  const [educations, setEducations] = useState<Education[]>([
    { degree: 'B.Tech in Computer Science', institution: 'National Institute of Technology', field: 'Computer Science', start_year: 2022, end_year: 2026, cgpa_or_percentage: '8.8 / 10.0' }
  ]);

  const [skills, setSkills] = useState<UserSkillItem[]>([
    { name: 'Python', proficiency: 'Advanced' },
    { name: 'FastAPI', proficiency: 'Advanced' },
    { name: 'React', proficiency: 'Intermediate' },
    { name: 'Machine Learning', proficiency: 'Intermediate' },
    { name: 'PostgreSQL', proficiency: 'Advanced' },
    { name: 'Docker', proficiency: 'Intermediate' }
  ]);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProf, setNewSkillProf] = useState('Intermediate');

  const [projects, setProjects] = useState<Project[]>([
    {
      title: 'Autonomous Multi-Agent RAG Assistant',
      description: 'Built a distributed multi-agent system using LangChain, ChromaDB, and FastAPI to parse and summarize research papers in real time.',
      technologies: ['Python', 'FastAPI', 'RAG', 'LangChain', 'Docker'],
      project_url: 'https://github.com/student/multi-agent-rag'
    }
  ]);

  const [experiences, setExperiences] = useState<Experience[]>([
    {
      company: 'TechCorp Innovations',
      role: 'Software Engineering Intern',
      description: 'Engineered RESTful microservices with FastAPI and PostgreSQL. Reduced latency by 35% using Redis caching.',
      start_date: 'May 2025',
      end_date: 'July 2025'
    }
  ]);

  const [preferredDomains, setPreferredDomains] = useState<string[]>(['AI/ML', 'Software Development']);
  const [preferredLocations, setPreferredLocations] = useState<string[]>(['Bangalore, India', 'Remote']);
  const [preferredWorkMode, setPreferredWorkMode] = useState('Any');
  const [preferredStipend, setPreferredStipend] = useState('₹40,000+/month');
  const [preferredDuration, setPreferredDuration] = useState('3-6 months');

  const allDomainOptions = [
    'AI/ML', 'Data Science', 'Software Development', 'Fullstack Development',
    'Frontend Development', 'Cloud & DevOps', 'Cybersecurity', 'Mobile Development',
    'Robotics & IoT', 'Product Management'
  ];

  useEffect(() => {
    api.profile.get()
      .then((p) => {
        if (p) {
          setFullName(p.full_name || '');
          setPhone(p.phone || '');
          setLocation(p.location || '');
          setCareerObjective(p.career_objective || '');
          if (p.educations && p.educations.length > 0) setEducations(p.educations);
          if (p.skills && p.skills.length > 0) setSkills(p.skills);
          if (p.projects && p.projects.length > 0) setProjects(p.projects);
          if (p.experiences && p.experiences.length > 0) setExperiences(p.experiences);
          if (p.preferred_domains && p.preferred_domains.length > 0) setPreferredDomains(p.preferred_domains);
          if (p.preferred_locations && p.preferred_locations.length > 0) setPreferredLocations(p.preferred_locations);
          if (p.preferred_work_mode) setPreferredWorkMode(p.preferred_work_mode);
          if (p.preferred_stipend) setPreferredStipend(p.preferred_stipend);
          if (p.preferred_duration) setPreferredDuration(p.preferred_duration);
        }
      })
      .catch((err) => console.error("Error loading profile:", err))
      .finally(() => setIsLoading(false));
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setSavedSuccess(false);
    try {
      await api.profile.update({
        full_name: fullName,
        phone,
        location,
        career_objective: careerObjective,
        educations,
        skills,
        projects,
        experiences,
        preferred_domains: preferredDomains,
        preferred_locations: preferredLocations,
        preferred_work_mode: preferredWorkMode,
        preferred_stipend: preferredStipend,
        preferred_duration: preferredDuration
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error("Error updating profile:", err);
    } finally {
      setIsSaving(false);
    }
  };

  const toggleDomain = (domain: string) => {
    setPreferredDomains(prev =>
      prev.includes(domain) ? prev.filter(d => d !== domain) : [...prev, domain]
    );
  };

  const addSkill = () => {
    if (!newSkillName.trim()) return;
    setSkills(prev => [...prev, { name: newSkillName.trim(), proficiency: newSkillProf }]);
    setNewSkillName('');
  };

  const removeSkill = (index: number) => {
    setSkills(prev => prev.filter((_, i) => i !== index));
  };

  const addEducation = () => {
    setEducations(prev => [...prev, { degree: '', institution: '', field: '', start_year: 2023, end_year: 2027, cgpa_or_percentage: '' }]);
  };

  const addProject = () => {
    setProjects(prev => [...prev, { title: '', description: '', technologies: ['Python'], project_url: '' }]);
  };

  const addExperience = () => {
    setExperiences(prev => [...prev, { company: '', role: '', description: '', start_date: '', end_date: '' }]);
  };

  const steps = [
    { num: 1, name: 'Personal Details', icon: User },
    { num: 2, name: 'Education', icon: GraduationCap },
    { num: 3, name: 'Skills Inventory', icon: Code2 },
    { num: 4, name: 'Projects', icon: FolderGit2 },
    { num: 5, name: 'Experience', icon: Briefcase },
    { num: 6, name: 'Career Preferences', icon: Compass },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Wizard Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            Student Profile & Career Setup
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
              Step {currentStep} of 6
            </span>
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Define your profile once to unlock high-precision RAG matching and explainable compatibility scores.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-4 py-2 rounded-xl bg-primary text-primary-foreground font-semibold text-xs hover:opacity-90 transition flex items-center gap-1.5 self-start sm:self-auto"
        >
          {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
          {savedSuccess ? 'Saved to Database!' : 'Save Changes'}
        </button>
      </div>

      {/* Step Indicators */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 p-1.5 bg-muted/60 rounded-2xl border border-border/80">
        {steps.map((step) => {
          const Icon = step.icon;
          const isActive = currentStep === step.num;
          const isCompleted = currentStep > step.num;
          return (
            <button
              key={step.num}
              onClick={() => setCurrentStep(step.num)}
              className={`p-2.5 rounded-xl text-xs font-semibold flex flex-col items-center gap-1.5 transition-all ${
                isActive
                  ? 'bg-card text-foreground shadow-sm border border-border/60'
                  : isCompleted
                  ? 'text-primary hover:bg-card/50'
                  : 'text-muted-foreground hover:bg-card/30'
              }`}
            >
              <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                isActive ? 'bg-primary text-primary-foreground' : isCompleted ? 'bg-primary/15 text-primary' : 'bg-muted text-muted-foreground'
              }`}>
                {isCompleted ? <Check className="w-3.5 h-3.5" /> : <Icon className="w-3.5 h-3.5" />}
              </div>
              <span className="text-[11px] truncate max-w-[80px]">{step.name}</span>
            </button>
          );
        })}
      </div>

      {/* Wizard Form Container */}
      <div className="p-6 sm:p-8 rounded-3xl bg-card border border-border/80 shadow-sm space-y-6">
        {/* Step 1: Personal Details */}
        {currentStep === 1 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <h2 className="text-lg font-bold">Personal Details</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Aarav Sharma"
                  className="w-full bg-muted/40 border border-input rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Phone Number</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="w-full bg-muted/40 border border-input rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Current Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Bangalore, India"
                className="w-full bg-muted/40 border border-input rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Career Objective / Bio</label>
              <textarea
                rows={3}
                value={careerObjective}
                onChange={(e) => setCareerObjective(e.target.value)}
                placeholder="Aspiring AI Engineer and Full-Stack Developer passionate about scalable distributed systems..."
                className="w-full bg-muted/40 border border-input rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>
        )}

        {/* Step 2: Education */}
        {currentStep === 2 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Academic Background</h2>
              <button
                onClick={addEducation}
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Degree
              </button>
            </div>

            {educations.map((edu, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-muted/40 border border-border/70 space-y-3 relative">
                {educations.length > 1 && (
                  <button
                    onClick={() => setEducations(prev => prev.filter((_, i) => i !== idx))}
                    className="absolute top-3 right-3 text-muted-foreground hover:text-destructive transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Degree</label>
                    <input
                      type="text"
                      value={edu.degree}
                      onChange={(e) => {
                        const val = e.target.value;
                        setEducations(prev => prev.map((item, i) => i === idx ? { ...item, degree: val } : item));
                      }}
                      placeholder="B.Tech in Computer Science"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Institution</label>
                    <input
                      type="text"
                      value={edu.institution}
                      onChange={(e) => {
                        const val = e.target.value;
                        setEducations(prev => prev.map((item, i) => i === idx ? { ...item, institution: val } : item));
                      }}
                      placeholder="NIT / IIT / University"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Field of Study</label>
                    <input
                      type="text"
                      value={edu.field || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setEducations(prev => prev.map((item, i) => i === idx ? { ...item, field: val } : item));
                      }}
                      placeholder="Computer Science & AI"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Graduation Year</label>
                    <input
                      type="number"
                      value={edu.end_year || 2026}
                      onChange={(e) => {
                        const val = parseInt(e.target.value) || 2026;
                        setEducations(prev => prev.map((item, i) => i === idx ? { ...item, end_year: val } : item));
                      }}
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">CGPA / Percentage</label>
                    <input
                      type="text"
                      value={edu.cgpa_or_percentage || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setEducations(prev => prev.map((item, i) => i === idx ? { ...item, cgpa_or_percentage: val } : item));
                      }}
                      placeholder="8.8 / 10.0"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Step 3: Skills Inventory */}
        {currentStep === 3 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <h2 className="text-lg font-bold">Technical Skills Inventory</h2>
            <p className="text-xs text-muted-foreground">Add all programming languages, frameworks, cloud tools, and domain skills.</p>

            {/* Add Skill Bar */}
            <div className="flex gap-2">
              <input
                type="text"
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="e.g. PyTorch, Docker, React, Golang"
                className="flex-1 bg-muted/40 border border-input rounded-xl px-3.5 py-2 text-sm"
              />
              <select
                value={newSkillProf}
                onChange={(e) => setNewSkillProf(e.target.value)}
                className="bg-muted/40 border border-input rounded-xl px-3 py-2 text-xs font-semibold"
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Expert">Expert</option>
              </select>
              <button
                type="button"
                onClick={addSkill}
                className="px-4 py-2 rounded-xl bg-primary text-primary-foreground font-semibold text-xs hover:opacity-90 transition flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add
              </button>
            </div>

            {/* Skills Chips */}
            <div className="flex flex-wrap gap-2 pt-2">
              {skills.map((s, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-secondary border border-border text-xs font-semibold"
                >
                  <span>{s.name}</span>
                  <span className="text-[10px] text-muted-foreground font-normal">({s.proficiency || 'Intermediate'})</span>
                  <button
                    onClick={() => removeSkill(idx)}
                    className="text-muted-foreground hover:text-destructive ml-1"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Step 4: Projects */}
        {currentStep === 4 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Featured Projects</h2>
              <button
                onClick={addProject}
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Project
              </button>
            </div>

            {projects.map((proj, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-muted/40 border border-border/70 space-y-3 relative">
                {projects.length > 1 && (
                  <button
                    onClick={() => setProjects(prev => prev.filter((_, i) => i !== idx))}
                    className="absolute top-3 right-3 text-muted-foreground hover:text-destructive transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Project Title</label>
                    <input
                      type="text"
                      value={proj.title}
                      onChange={(e) => {
                        const val = e.target.value;
                        setProjects(prev => prev.map((item, i) => i === idx ? { ...item, title: val } : item));
                      }}
                      placeholder="Autonomous Multi-Agent RAG Assistant"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Repository / Demo URL</label>
                    <input
                      type="text"
                      value={proj.project_url || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setProjects(prev => prev.map((item, i) => i === idx ? { ...item, project_url: val } : item));
                      }}
                      placeholder="https://github.com/username/project"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Technologies Used (comma separated)</label>
                  <input
                    type="text"
                    value={proj.technologies.join(', ')}
                    onChange={(e) => {
                      const val = e.target.value.split(',').map(t => t.trim()).filter(Boolean);
                      setProjects(prev => prev.map((item, i) => i === idx ? { ...item, technologies: val } : item));
                    }}
                    placeholder="Python, FastAPI, Docker, PyTorch"
                    className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Description & Impact</label>
                  <textarea
                    rows={2}
                    value={proj.description || ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      setProjects(prev => prev.map((item, i) => i === idx ? { ...item, description: val } : item));
                    }}
                    placeholder="Built a high-performance system processing 10k events/min..."
                    className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Step 5: Experience */}
        {currentStep === 5 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">Past Experience & Internships</h2>
              <button
                onClick={addExperience}
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Add Experience
              </button>
            </div>

            {experiences.map((exp, idx) => (
              <div key={idx} className="p-4 rounded-2xl bg-muted/40 border border-border/70 space-y-3 relative">
                {experiences.length > 1 && (
                  <button
                    onClick={() => setExperiences(prev => prev.filter((_, i) => i !== idx))}
                    className="absolute top-3 right-3 text-muted-foreground hover:text-destructive transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Company</label>
                    <input
                      type="text"
                      value={exp.company}
                      onChange={(e) => {
                        const val = e.target.value;
                        setExperiences(prev => prev.map((item, i) => i === idx ? { ...item, company: val } : item));
                      }}
                      placeholder="TechCorp Innovations"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Role Title</label>
                    <input
                      type="text"
                      value={exp.role}
                      onChange={(e) => {
                        const val = e.target.value;
                        setExperiences(prev => prev.map((item, i) => i === idx ? { ...item, role: val } : item));
                      }}
                      placeholder="Software Engineering Intern"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Start Date</label>
                    <input
                      type="text"
                      value={exp.start_date || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setExperiences(prev => prev.map((item, i) => i === idx ? { ...item, start_date: val } : item));
                      }}
                      placeholder="May 2025"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">End Date</label>
                    <input
                      type="text"
                      value={exp.end_date || ''}
                      onChange={(e) => {
                        const val = e.target.value;
                        setExperiences(prev => prev.map((item, i) => i === idx ? { ...item, end_date: val } : item));
                      }}
                      placeholder="July 2025"
                      className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-muted-foreground uppercase mb-1">Role Description</label>
                  <textarea
                    rows={2}
                    value={exp.description || ''}
                    onChange={(e) => {
                      const val = e.target.value;
                      setExperiences(prev => prev.map((item, i) => i === idx ? { ...item, description: val } : item));
                    }}
                    placeholder="Engineered microservices and reduced API latency by 35%..."
                    className="w-full bg-card border border-input rounded-xl px-3 py-2 text-sm"
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Step 6: Career Preferences */}
        {currentStep === 6 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <h2 className="text-lg font-bold">Career & Internship Preferences</h2>
            <p className="text-xs text-muted-foreground">Select your targeted domains to personalize your RAG search & matching algorithm.</p>

            <div>
              <label className="block text-xs font-semibold text-muted-foreground uppercase mb-2">Target Domains</label>
              <div className="flex flex-wrap gap-2">
                {allDomainOptions.map((domain) => {
                  const isSelected = preferredDomains.includes(domain);
                  return (
                    <button
                      key={domain}
                      type="button"
                      onClick={() => toggleDomain(domain)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                        isSelected
                          ? 'bg-primary text-primary-foreground shadow-sm'
                          : 'bg-secondary text-secondary-foreground hover:bg-accent'
                      }`}
                    >
                      {domain}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Work Mode</label>
                <select
                  value={preferredWorkMode}
                  onChange={(e) => setPreferredWorkMode(e.target.value)}
                  className="w-full bg-muted/40 border border-input rounded-xl px-3 py-2 text-xs font-semibold"
                >
                  <option value="Any">Any (Remote / Hybrid / Onsite)</option>
                  <option value="Remote">Remote Only</option>
                  <option value="Hybrid">Hybrid</option>
                  <option value="Onsite">Onsite</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Stipend Preference</label>
                <input
                  type="text"
                  value={preferredStipend}
                  onChange={(e) => setPreferredStipend(e.target.value)}
                  placeholder="₹40,000+/month"
                  className="w-full bg-muted/40 border border-input rounded-xl px-3 py-2 text-xs"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted-foreground uppercase mb-1">Duration</label>
                <input
                  type="text"
                  value={preferredDuration}
                  onChange={(e) => setPreferredDuration(e.target.value)}
                  placeholder="3-6 months"
                  className="w-full bg-muted/40 border border-input rounded-xl px-3 py-2 text-xs"
                />
              </div>
            </div>
          </div>
        )}

        {/* Wizard Navigation Footer */}
        <div className="pt-6 border-t border-border/80 flex items-center justify-between">
          <button
            type="button"
            disabled={currentStep === 1}
            onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-accent transition disabled:opacity-30 flex items-center gap-1"
          >
            <ChevronLeft className="w-4 h-4" /> Previous
          </button>

          <div className="flex items-center gap-2">
            {currentStep < 6 ? (
              <button
                type="button"
                onClick={() => setCurrentStep(prev => Math.min(6, prev + 1))}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:opacity-90 transition flex items-center gap-1"
              >
                Next Step <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={async () => {
                  await handleSave();
                  navigate('/internships');
                }}
                className="px-5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 text-white hover:opacity-90 transition flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
              >
                <Sparkles className="w-3.5 h-3.5" /> Finish & View Matches
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
