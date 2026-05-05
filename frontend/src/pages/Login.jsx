import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Added Link import

const Login = ({ setUserRole }) => {
  const navigate = useNavigate();
  const [idValue, setIdValue] = useState("");
  const [passwordValue, setPasswordValue] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    // --- 1. MOCK LOGIC (For Testing/Quick Demo) ---
    if (idValue.toUpperCase().includes('ADMIN') || idValue.toUpperCase().includes('MANAGER')) {
      console.log("Mock Login: Manager Role Assigned");
      setUserRole('manager');
      navigate('/manager');
      return; 
    }
    
    if (idValue.toUpperCase().includes('EMP')) {
      console.log("Mock Login: Employee Role Assigned");
      setUserRole('employee');
      navigate('/learning');
      return;
    }

    // --- 2. BACKEND API LOGIC (Actual Integration) ---
    try {
      const response = await fetch('http://localhost:8000/api/users/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          employee_id: idValue, 
          e_password: passwordValue 
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Use the 'role' returned by the AuthenticationService [cite: 12]
        setUserRole(data.is_manager ? 'manager' : 'employee'); 
        navigate(data.is_manager ? '/manager' : '/learning');
      } else {
        alert("Invalid Employee ID or Password.");
      }
    } catch (error) {
      console.error("Backend unreachable. Ensure Django is running.");
      alert("Backend Error: Falling back to Mock Login for testing.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl">
        
        {/* Logo Section */}
        <div className="text-center mb-10">
          <div className="inline-block p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/20 mb-4">
             <div className="w-12 h-12 bg-cyan-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)]">
                <span className="text-slate-950 font-black text-xl">S2</span>
             </div>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">SuperSecure AI </h1>
          <p className="text-slate-500 text-sm mt-1">Division Operations Portal</p>
        </div>

        {/* Form Section */}
        <form onSubmit={handleLogin} className="space-y-6 flex flex-col">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 ml-1">
              Employee ID
            </label>
            <input 
              type="text" 
              required
              value={idValue}
              onChange={(e) => setIdValue(e.target.value)}
              placeholder="e.g. EMP12345 or MANAGER_JANE"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all placeholder:text-slate-700"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 ml-1">
              Security PIN
            </label>
            <input 
              type="password" 
              placeholder="••••"
              required
              value={passwordValue} 
              onChange={(e) => setPasswordValue(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all placeholder:text-slate-700"
            />
          </div>

          <div className="flex flex-col gap-3">
            <button 
              type="submit"
              className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-cyan-900/20 transition-all active:scale-[0.98]"
            >
              Access Command Center
            </button>

            {/* Link must be inside a flex/block container for full width */}
            <Link 
              to="/register"
              className="w-full bg-transparent border border-slate-700 hover:border-slate-500 hover:bg-slate-800/50 text-slate-400 font-bold py-4 rounded-xl transition-all text-center uppercase text-[10px] tracking-widest"
            >
              New Employee Registration
            </Link>
          </div>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-800 flex justify-between items-center text-[10px] text-slate-600 uppercase font-bold tracking-widest">
          <span>Encrypted Session</span>
          <span>v1.0.4-Alpha</span>
        </div>
      </div>
    </div>
  );
};

export default Login;