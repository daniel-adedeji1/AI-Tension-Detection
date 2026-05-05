import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Import all pages
import Login from './pages/Login';
import Manager from './pages/Manager';
import Learning from './pages/Learning';
import Register from './pages/Register';

function App() {
  // This state controls access to protected routes
  const [userRole, setUserRole] = useState(null);

  return (
    <Router>
      <Routes>
        {/* 1. PUBLIC ROUTES */}
        <Route path="/" element={<Login setUserRole={setUserRole} />} />
        <Route path="/register" element={<Register />} />

        {/* 2. PROTECTED ROUTES */}
        {/* Manager Route: Now correctly passes the setter prop */}
        <Route 
          path="/manager" 
          element={userRole === 'manager' ? <Manager setUserRole={setUserRole} /> : <Navigate to="/" />} 
        />
        
        {/* Learning Route: Added setUserRole here too so logout works from this page */}
        <Route 
          path="/learning" 
          element={userRole ? <Learning userRole={userRole} setUserRole={setUserRole} /> : <Navigate to="/" />} 
        />

        {/* 3. CATCH-ALL */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;