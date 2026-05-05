import { useState } from "react";


// Equipment & Personnel Tracking Section
const DeviceStatus = () => {
  const [devices] = useState([
    { id: "BC-101", employee: "Marcus Thorne", battery: 88, status: "Active", signal: "Strong" },
    { id: "BC-102", employee: "Elena Rodriguez", battery: 42, status: "Active", signal: "Moderate" },
    { id: "BC-103", employee: "Unassigned", battery: 12, status: "Charging", signal: "N/A" },
    { id: "BC-104", employee: "James Wilson", battery: 95, status: "Active", signal: "Strong" },
  ]);

  return (
    <div className="mt-8 bg-slate-900/50 rounded-2xl border border-slate-800 overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-800/30 flex justify-between items-center">
        <h3 className="text-sm font-bold uppercase tracking-widest text-cyan-400">Hardware Inventory & Assignments</h3>
        <button className="text-[10px] bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded-md transition-all">Scan New Device</button>
      </div>
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="text-slate-500 border-b border-slate-800">
            <th className="p-4 font-semibold uppercase">Device ID</th>
            <th className="p-4 font-semibold uppercase">Assigned To</th>
            <th className="p-4 font-semibold uppercase">Battery Life</th>
            <th className="p-4 font-semibold uppercase">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {devices.map((device) => (
            <tr key={device.id} className="hover:bg-slate-800/20 transition-colors">
              <td className="p-4 font-mono text-cyan-500">{device.id}</td>
              <td className="p-4 text-slate-300">{device.employee}</td>
              <td className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
                    <div 
                      className={`h-full ${device.battery < 20 ? 'bg-red-500' : 'bg-green-500'}`} 
                      style={{ width: `${device.battery}%` }}
                    ></div>
                  </div>
                  <span className={device.battery < 20 ? 'text-red-400 font-bold' : 'text-slate-400'}>
                    {device.battery}%
                  </span>
                </div>
              </td>
              <td className="p-4">
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                  device.status === 'Active' ? 'bg-green-500/10 text-green-500' : 'bg-amber-500/10 text-amber-500'
                }`}>
                  {device.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DeviceStatus;