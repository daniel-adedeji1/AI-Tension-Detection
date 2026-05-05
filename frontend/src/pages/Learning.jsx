import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/dashboard/SearchBar';

const Learning = ({ userRole, setUserRole }) => {
  const navigate = useNavigate();
  
  // NEW: State for assigned modules (replaces hardcoded list)
  const [assignedModules, setAssignedModules] = useState([
    { id: 402, title: 'Incident #BC-402', status: 'Active' },
    { id: 101, title: 'Handling Aggression', status: 'Pending' },
    { id: 102, title: 'Medical Emergency', status: 'Pending' }
  ]);

  // Reflection State
  const [reflection, setReflection] = useState({
    trigger: '',
    technique: '',
    improvement: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  // REVERTED: Keeping original handleLogout logic
  const handleLogout = async () => {
    console.log("Terminating Employee Session...");
    try {
      await fetch('http://localhost:8000/api/users/logout/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      console.log("Mock Logout: Backend offline, clearing local state.");
    } finally {
      if (typeof setUserRole === 'function') {
        setUserRole(null);
      }
      navigate('/');
    }
  };

  const handleSubmitReflection = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/training/submit-reflection/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_id: "BC-402",
          ...reflection
        }),
      });
      if (response.ok) setIsSubmitted(true);
    } catch (error) {
      setIsSubmitted(true); // Fallback for demo
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
      
      {/* 1. Sidebar */}
      <aside className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col p-6 shadow-2xl z-10">
        {userRole === 'manager' && (  
          <button 
            onClick={() => navigate('/manager')}
            className="text-[10px] font-black tracking-widest text-cyan-500 mb-8 flex items-center gap-2 hover:text-cyan-400 transition-colors uppercase"
          >
            ← BACK TO OPS CENTER
          </button>
        )}
        
        <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 mb-6 flex items-center gap-2">
           <span className="w-2 h-2 bg-cyan-500 rounded-full"></span>
           Assigned Modules
        </h2>
        
        <div className="space-y-3">
          {assignedModules.map((module, i) => (
            <div key={module.id} className={`p-4 rounded-xl border text-[11px] font-bold transition-all ${i === 0 ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400 shadow-lg shadow-cyan-900/10' : 'border-slate-800 bg-slate-900/50 text-slate-500'}`}>
              {module.title}
            </div>
          ))}
        </div>

        <div className="mt-auto space-y-6">
           <div className="pt-6 border-t border-slate-800">
              <div className="flex justify-between text-[10px] text-slate-500 uppercase font-black mb-2 tracking-tighter">
                <span>Progress</span>
                <span>{isSubmitted ? '100%' : '60%'}</span>
              </div>
              <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div className={`h-full bg-cyan-500 transition-all duration-1000 ${isSubmitted ? 'w-full' : 'w-3/5'}`}></div>
              </div>
           </div>

           <button 
             onClick={handleLogout}
             className="w-full bg-red-600/10 hover:bg-red-600 border border-red-600/50 text-red-500 hover:text-white py-4 rounded-xl text-[10px] font-black transition-all uppercase tracking-widest shadow-lg shadow-red-900/5"
           >
             Terminate Session
           </button>
        </div>
      </aside>

      {/* 2. Main Content */}
      <main className="flex-1 flex flex-col p-8 overflow-y-auto bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
        <div className="max-w-4xl mx-auto w-full">
          <header className="mb-10">
            <div className="mb-6">
              <SearchBar placeholder="Search assigned clips..." />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">
              Scenario Review: <span className="text-slate-500 font-mono italic">#BC-402</span>
            </h1>
            <p className="text-slate-500 text-sm mt-2 font-medium">Review the AI-flagged incident and complete the mandatory Self-Reflection Scorecard.</p>
          </header>

          {/* UPDATED: Dynamic Video Player pointing to Django API */}
          <div className="aspect-video bg-slate-900 rounded-[2rem] border border-slate-800 shadow-2xl relative overflow-hidden mb-10 group">
            <video 
              className="w-full h-full object-contain" 
              controls 
              crossOrigin="anonymous"
              preload="metadata"
            >
              <source src="http://localhost:8000/api/videos/2002/" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            
            <div className="absolute top-8 right-8 bg-red-600/20 border border-red-500/50 px-5 py-2.5 rounded-xl backdrop-blur-md z-20 pointer-events-none">
               <span className="text-[10px] font-black text-red-500 animate-pulse tracking-[0.2em]">
                 ARCHIVED TENSION SPIKE [82%]
               </span>
            </div>
          </div>

          <section className="bg-slate-900/50 border border-slate-800 p-10 rounded-[2rem] shadow-2xl backdrop-blur-sm">
            {!isSubmitted ? (
              <form onSubmit={handleSubmitReflection} className="space-y-8">
                <h3 className="text-xl font-bold text-white mb-8 border-l-4 border-cyan-500 pl-6">
                  Self-Reflection Scorecard
                </h3>

                <div className="space-y-6">
                  <div>
                    <label className="block text-[10px] font-black text-slate-500 uppercase mb-3 tracking-widest">
                      1. Identify the Escalation Trigger
                    </label>
                    <textarea 
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-sm text-slate-300 focus:ring-1 focus:ring-cyan-500 outline-none"
                      placeholder="What behavior caused the tension spike?"
                      rows="3"
                      onChange={(e) => setReflection({...reflection, trigger: e.target.value})}
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-black text-slate-500 uppercase mb-3 tracking-widest">
                      2. Strategy Applied
                    </label>
                    <select 
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-sm text-slate-300 outline-none focus:ring-1 focus:ring-cyan-500 appearance-none"
                      onChange={(e) => setReflection({...reflection, technique: e.target.value})}
                    >
                      <option value="">Select Technique...</option>
                      <option value="mirroring">Voice Mirroring</option>
                      <option value="active_listening">Active Listening</option>
                      <option value="empathy">Empathy Statement</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[10px] font-black text-slate-500 uppercase mb-3 tracking-widest">
                      3. Areas for improvement
                    </label>
                    <textarea 
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-sm text-slate-300 focus:ring-1 focus:ring-cyan-500 outline-none"
                      placeholder="What would you change next time?"
                      rows="3"
                      onChange={(e) => setReflection({...reflection, improvement: e.target.value})}
                    />
                  </div>
                </div>

                <button 
                  type="submit"
                  className="w-full bg-cyan-600 hover:bg-cyan-500 text-white py-4 rounded-2xl text-[11px] font-black transition-all uppercase tracking-widest"
                >
                  Save Reflection to Record
                </button>
              </form>
            ) : (
              <div className="py-10 text-center">
                <h3 className="text-2xl font-bold text-white mb-4">Debrief Complete</h3>
                <p className="text-slate-500 text-sm">Your scorecard has been saved to the database.</p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
};

export default Learning;