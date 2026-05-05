import React, { useState } from 'react';

const SearchBar = ({ placeholder }) => {
  const [query, setQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    console.log("Searching database for:", query);
    // Stage 2: fetch(`http://api/clips/search?q=${query}`)
  };

  return (
    <form onSubmit={handleSearch} className="relative w-full max-w-md group">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <span className="text-slate-500 group-focus-within:text-cyan-500 transition-colors">🔍</span>
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="block w-full pl-10 pr-3 py-2 border border-slate-800 rounded-xl bg-slate-950/50 text-slate-200 text-xs placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 transition-all"
        placeholder={placeholder}
      />
      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <span className="text-[10px] text-slate-700 font-mono tracking-tighter">CTRL + K</span>
      </div>
    </form>
  );
};

export default SearchBar;