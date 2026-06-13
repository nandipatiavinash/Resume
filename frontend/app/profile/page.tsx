"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchWithAuth } from "../../lib/api/client";
import { motion } from "framer-motion";
import { User, GraduationCap, Briefcase, Award, ListChecks, CheckCircle, Plus, Trash2, Loader2 } from "lucide-react";

type TabType = "personal" | "education" | "skills" | "experience" | "certs" | "achievements";

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState<TabType>("personal");
  const queryClient = useQueryClient();

  // Queries
  const { data: profile, isLoading, isError, error } = useQuery({
    queryKey: ["profile"],
    queryFn: () => fetchWithAuth("/profile"),
    retry: false
  });

  // Mutations
  const createProfileMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile", { method: "PUT", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const addEduMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile/education", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const deleteEduMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/profile/education/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const addSkillMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile/skills", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const deleteSkillMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/profile/skills/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const addExpMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile/experience", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const deleteExpMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/profile/experience/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const addCertMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile/certifications", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const deleteCertMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/profile/certifications/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const addAchMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/profile/achievements", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  const deleteAchMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/profile/achievements/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] })
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  // Handle case where profile does not exist
  if (isError && (error as any).message?.includes("not found")) {
    return <CreateProfileForm onCreate={(data) => createProfileMutation.mutate(data)} loading={createProfileMutation.isPending} />;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      {/* Sidebar Navigation */}
      <div className="glass-panel p-4 rounded-2xl flex flex-col gap-2 h-fit">
        <h3 className="font-bold text-white mb-4 px-4">Profile Sections</h3>
        <TabButton active={activeTab === "personal"} onClick={() => setActiveTab("personal")} icon={<User size={18} />} label="Personal Details" />
        <TabButton active={activeTab === "education"} onClick={() => setActiveTab("education")} icon={<GraduationCap size={18} />} label="Education" />
        <TabButton active={activeTab === "skills"} onClick={() => setActiveTab("skills")} icon={<ListChecks size={18} />} label="Technical Skills" />
        <TabButton active={activeTab === "experience"} onClick={() => setActiveTab("experience")} icon={<Briefcase size={18} />} label="Work Experience" />
        <TabButton active={activeTab === "certs"} onClick={() => setActiveTab("certs")} icon={<Award size={18} />} label="Certifications" />
        <TabButton active={activeTab === "achievements"} onClick={() => setActiveTab("achievements")} icon={<Award size={18} />} label="Achievements" />
      </div>

      {/* Editor Content Area */}
      <div className="lg:col-span-3 glass-panel p-6 md:p-8 rounded-2xl">
        {activeTab === "personal" && (
          <PersonalTab
            profile={profile}
            onSave={(data) => updateProfileMutation.mutate(data)}
            loading={updateProfileMutation.isPending}
          />
        )}
        {activeTab === "education" && (
          <EducationTab
            educations={profile.educations || []}
            onAdd={(data) => addEduMutation.mutate(data)}
            onDelete={(id) => deleteEduMutation.mutate(id)}
            loading={addEduMutation.isPending}
          />
        )}
        {activeTab === "skills" && (
          <SkillsTab
            skills={profile.skills || []}
            onAdd={(data) => addSkillMutation.mutate(data)}
            onDelete={(id) => deleteSkillMutation.mutate(id)}
            loading={addSkillMutation.isPending}
          />
        )}
        {activeTab === "experience" && (
          <ExperienceTab
            experiences={profile.experiences || []}
            onAdd={(data) => addExpMutation.mutate(data)}
            onDelete={(id) => deleteExpMutation.mutate(id)}
            loading={addExpMutation.isPending}
          />
        )}
        {activeTab === "certs" && (
          <CertificationsTab
            certifications={profile.certifications || []}
            onAdd={(data) => addCertMutation.mutate(data)}
            onDelete={(id) => deleteCertMutation.mutate(id)}
            loading={addCertMutation.isPending}
          />
        )}
        {activeTab === "achievements" && (
          <AchievementsTab
            achievements={profile.achievements || []}
            onAdd={(data) => addAchMutation.mutate(data)}
            onDelete={(id) => deleteAchMutation.mutate(id)}
            loading={addAchMutation.isPending}
          />
        )}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-3 py-3 px-4 rounded-xl text-sm font-medium transition-all ${
        active ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white hover:bg-slate-800/40"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

// --- SUB TABS IMPLEMENTATION ---

function CreateProfileForm({ onCreate, loading }: { onCreate: (data: any) => void; loading: boolean }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreate({ full_name: name, email, phone });
  };

  return (
    <div className="max-w-xl mx-auto glass-panel p-8 rounded-3xl mt-12">
      <h3 className="text-xl font-bold text-white mb-2">Create Your Master Profile</h3>
      <p className="text-sm text-slate-400 mb-6">Initialize your contact details. This is used for all resume compiles.</p>
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-slate-400">Full Name</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white" required />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-slate-400">Email Address</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="jane@example.com" className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white" required />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs text-slate-400">Phone Number</label>
          <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+1234567890" className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white" />
        </div>
        <button type="submit" disabled={loading} className="bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl font-semibold text-sm transition-colors mt-2">
          {loading ? "Creating..." : "Save Details"}
        </button>
      </form>
    </div>
  );
}

function PersonalTab({ profile, onSave, loading }: { profile: any; onSave: (data: any) => void; loading: boolean }) {
  const [name, setName] = useState(profile?.full_name || "");
  const [email, setEmail] = useState(profile?.email || "");
  const [phone, setPhone] = useState(profile?.phone || "");
  const [web, setWeb] = useState(profile?.website || "");
  const [github, setGithub] = useState(profile?.github_url || "");
  const [linkedin, setLinkedin] = useState(profile?.linkedin_url || "");
  const [summary, setSummary] = useState(profile?.summary || "");

  const handleSave = () => {
    onSave({ full_name: name, email, phone, website: web, github_url: github, linkedin_url: linkedin, summary });
  };

  return (
    <div className="flex flex-col gap-6">
      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Personal Details</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormInput label="Full Name" value={name} onChange={setName} />
        <FormInput label="Email" value={email} onChange={setEmail} />
        <FormInput label="Phone" value={phone} onChange={setPhone} />
        <FormInput label="Website" value={web} onChange={setWeb} />
        <FormInput label="GitHub Link" value={github} onChange={setGithub} />
        <FormInput label="LinkedIn Link" value={linkedin} onChange={setLinkedin} />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-slate-400 font-medium">Professional Summary</label>
        <textarea value={summary} onChange={(e) => setSummary(e.target.value)} rows={4} className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500" placeholder="Brief elevator pitch about your experience..." />
      </div>
      <button onClick={handleSave} disabled={loading} className="bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl font-semibold text-sm text-center transition-colors mt-2 max-w-xs">
        {loading ? "Saving..." : "Save Changes"}
      </button>
    </div>
  );
}

function FormInput({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-slate-400 font-medium">{label}</label>
      <input type="text" value={value} onChange={(e) => onChange(e.target.value)} className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-indigo-500" />
    </div>
  );
}

function EducationTab({ educations, onAdd, onDelete, loading }: { educations: any[]; onAdd: (data: any) => void; onDelete: (id: string) => void; loading: boolean }) {
  const [inst, setInst] = useState("");
  const [deg, setDeg] = useState("");
  const [field, setField] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");

  const handleAdd = () => {
    if (inst && deg && field) {
      onAdd({ institution: inst, degree: deg, field_of_study: field, start_date: start, end_date: end });
      setInst(""); setDeg(""); setField(""); setStart(""); setEnd("");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Education History</h3>
      
      {/* Existing list */}
      <div className="flex flex-col gap-3">
        {educations.map((edu) => (
          <div key={edu.id} className="glass-card p-4 rounded-xl flex justify-between items-center">
            <div>
              <h4 className="font-bold text-white text-sm">{edu.institution}</h4>
              <p className="text-xs text-slate-400 mt-1">{edu.degree} in {edu.field_of_study}</p>
              <p className="text-xs text-slate-500 mt-0.5">{edu.start_date} - {edu.end_date || "Present"}</p>
            </div>
            <button onClick={() => onDelete(edu.id)} className="text-rose-400 hover:text-rose-300 p-2"><Trash2 size={16} /></button>
          </div>
        ))}
      </div>

      {/* Add Form */}
      <div className="border-t border-slate-800 pt-6 mt-4">
        <h4 className="font-semibold text-slate-300 mb-3 text-sm">Add Education</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormInput label="Institution" value={inst} onChange={setInst} />
          <FormInput label="Degree (e.g. B.S.)" value={deg} onChange={setDeg} />
          <FormInput label="Field of Study" value={field} onChange={setField} />
          <FormInput label="Start Date" value={start} onChange={setStart} />
          <FormInput label="End Date (or Present)" value={end} onChange={setEnd} />
        </div>
        <button onClick={handleAdd} disabled={loading} className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 font-semibold text-xs py-2.5 px-4 rounded-xl mt-4 flex items-center gap-2">
          <Plus size={14} /> Add Education Record
        </button>
      </div>
    </div>
  );
}

function SkillsTab({ skills, onAdd, onDelete, loading }: { skills: any[]; onAdd: (data: any) => void; onDelete: (id: string) => void; loading: boolean }) {
  const [name, setName] = useState("");
  const [cat, setCat] = useState("Languages");

  const handleAdd = () => {
    if (name.trim()) {
      onAdd({ name, category: cat });
      setName("");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Technical Skills</h3>
      
      {/* Existing Skill Tags */}
      <div className="flex flex-wrap gap-2">
        {skills.map((s) => (
          <div key={s.id} className="bg-slate-900/80 border border-slate-800 rounded-full px-3 py-1 text-xs text-slate-300 flex items-center gap-2">
            <span>{s.name} <span className="text-slate-600">({s.category})</span></span>
            <button onClick={() => onDelete(s.id)} className="text-rose-400 hover:text-rose-300"><Trash2 size={12} /></button>
          </div>
        ))}
      </div>

      {/* Add Skill Form */}
      <div className="border-t border-slate-800 pt-6 mt-4 max-w-md">
        <h4 className="font-semibold text-slate-300 mb-3 text-sm">Add Skill</h4>
        <div className="flex gap-3">
          <div className="flex-1 flex flex-col gap-1">
            <label className="text-xs text-slate-500">Skill Name</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Python" className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white" />
          </div>
          <div className="flex flex-col gap-1 w-40">
            <label className="text-xs text-slate-500">Category</label>
            <select value={cat} onChange={(e) => setCat(e.target.value)} className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white">
              <option value="Languages">Languages</option>
              <option value="Frameworks">Frameworks</option>
              <option value="Libraries">Libraries</option>
              <option value="Tools">Tools</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
        <button onClick={handleAdd} disabled={loading} className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 font-semibold text-xs py-2.5 px-4 rounded-xl mt-4 flex items-center gap-2">
          <Plus size={14} /> Add Skill
        </button>
      </div>
    </div>
  );
}

function ExperienceTab({ experiences, onAdd, onDelete, loading }: { experiences: any[]; onAdd: (data: any) => void; onDelete: (id: string) => void; loading: boolean }) {
  const [comp, setComp] = useState("");
  const [pos, setPos] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [bullet, setBullet] = useState("");
  const [bullets, setBullets] = useState<string[]>([]);

  const handleAddBullet = () => {
    if (bullet.trim()) {
      setBullets([...bullets, bullet.trim()]);
      setBullet("");
    }
  };

  const handleAddExp = () => {
    if (comp && pos && start) {
      onAdd({ company: comp, position: pos, start_date: start, end_date: end, bullets });
      setComp(""); setPos(""); setStart(""); setEnd(""); setBullets([]);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Work Experience</h3>
      
      {/* Existing List */}
      <div className="flex flex-col gap-4">
        {experiences.map((exp) => (
          <div key={exp.id} className="glass-card p-5 rounded-xl flex justify-between">
            <div>
              <h4 className="font-bold text-white text-sm">{exp.position} at {exp.company}</h4>
              <p className="text-xs text-slate-500 mt-1">{exp.start_date} - {exp.end_date || "Present"}</p>
              <ul className="list-disc pl-5 mt-2 flex flex-col gap-1">
                {exp.bullets.map((b: string, i: number) => (
                  <li key={i} className="text-xs text-slate-400">{b}</li>
                ))}
              </ul>
            </div>
            <button onClick={() => onDelete(exp.id)} className="text-rose-400 hover:text-rose-300 p-2 self-start"><Trash2 size={16} /></button>
          </div>
        ))}
      </div>

      {/* Add Form */}
      <div className="border-t border-slate-800 pt-6 mt-4">
        <h4 className="font-semibold text-slate-300 mb-3 text-sm">Add Position</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <FormInput label="Company" value={comp} onChange={setComp} />
          <FormInput label="Position" value={pos} onChange={setPos} />
          <FormInput label="Start Date" value={start} onChange={setStart} />
          <FormInput label="End Date (or Present)" value={end} onChange={setEnd} />
        </div>

        {/* Bullet builder */}
        <div className="flex flex-col gap-1 mb-4">
          <label className="text-xs text-slate-500">Add Bullet Points (quantified, action verb-based)</label>
          <div className="flex gap-2">
            <input type="text" value={bullet} onChange={(e) => setBullet(e.target.value)} placeholder="e.g. Optimized database indexing, reducing search times by 40%." className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white" />
            <button type="button" onClick={handleAddBullet} className="bg-slate-800 text-slate-300 hover:text-white px-4 rounded-xl text-xs">Add</button>
          </div>
          {bullets.length > 0 && (
            <ul className="list-disc pl-5 mt-2 flex flex-col gap-1 bg-slate-900/30 p-3 rounded-xl border border-slate-800/40">
              {bullets.map((b, idx) => (
                <li key={idx} className="text-xs text-slate-400 flex justify-between items-center">
                  <span>{b}</span>
                  <button type="button" onClick={() => setBullets(bullets.filter((_, i) => i !== idx))} className="text-rose-400 hover:underline text-[10px]">Remove</button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <button onClick={handleAddExp} disabled={loading} className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 font-semibold text-xs py-2.5 px-4 rounded-xl flex items-center gap-2">
          <Plus size={14} /> Add Position Record
        </button>
      </div>
    </div>
  );
}

function CertificationsTab({ certifications, onAdd, onDelete, loading }: { certifications: any[]; onAdd: (data: any) => void; onDelete: (id: string) => void; loading: boolean }) {
  const [name, setName] = useState("");
  const [issuer, setIssuer] = useState("");
  const [date, setDate] = useState("");

  const handleAdd = () => {
    if (name && issuer) {
      onAdd({ name, issuer, issue_date: date });
      setName(""); setIssuer(""); setDate("");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Certifications</h3>
      <div className="flex flex-col gap-3">
        {certifications.map((c) => (
          <div key={c.id} className="glass-card p-4 rounded-xl flex justify-between items-center">
            <div>
              <h4 className="font-bold text-white text-sm">{c.name}</h4>
              <p className="text-xs text-slate-400 mt-1">Issued by {c.issuer} ({c.issue_date})</p>
            </div>
            <button onClick={() => onDelete(c.id)} className="text-rose-400 hover:text-rose-300 p-2"><Trash2 size={16} /></button>
          </div>
        ))}
      </div>

      <div className="border-t border-slate-800 pt-6 mt-4">
        <h4 className="font-semibold text-slate-300 mb-3 text-sm">Add Certification</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormInput label="Certification Name" value={name} onChange={setName} />
          <FormInput label="Issuer" value={issuer} onChange={setIssuer} />
          <FormInput label="Issue Date" value={date} onChange={setDate} />
        </div>
        <button onClick={handleAdd} disabled={loading} className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 font-semibold text-xs py-2.5 px-4 rounded-xl mt-4 flex items-center gap-2">
          <Plus size={14} /> Add Certification
        </button>
      </div>
    </div>
  );
}

function AchievementsTab({ achievements, onAdd, onDelete, loading }: { achievements: any[]; onAdd: (data: any) => void; onDelete: (id: string) => void; loading: boolean }) {
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [date, setDate] = useState("");

  const handleAdd = () => {
    if (title && desc) {
      onAdd({ title, description: desc, date });
      setTitle(""); setDesc(""); setDate("");
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Achievements</h3>
      <div className="flex flex-col gap-3">
        {achievements.map((ach) => (
          <div key={ach.id} className="glass-card p-4 rounded-xl flex justify-between items-center">
            <div>
              <h4 className="font-bold text-white text-sm">{ach.title}</h4>
              <p className="text-xs text-slate-400 mt-1">{ach.description} ({ach.date})</p>
            </div>
            <button onClick={() => onDelete(ach.id)} className="text-rose-400 hover:text-rose-300 p-2"><Trash2 size={16} /></button>
          </div>
        ))}
      </div>

      <div className="border-t border-slate-800 pt-6 mt-4">
        <h4 className="font-semibold text-slate-300 mb-3 text-sm">Add Achievement</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput label="Achievement Title" value={title} onChange={setTitle} />
          <FormInput label="Date" value={date} onChange={setDate} />
        </div>
        <div className="flex flex-col gap-1 mt-3">
          <label className="text-xs text-slate-500">Description</label>
          <textarea value={desc} onChange={(e) => setDesc(e.target.value)} rows={3} className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500" placeholder="Describe your achievement..." />
        </div>
        <button onClick={handleAdd} disabled={loading} className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 font-semibold text-xs py-2.5 px-4 rounded-xl mt-4 flex items-center gap-2">
          <Plus size={14} /> Add Achievement
        </button>
      </div>
    </div>
  );
}
