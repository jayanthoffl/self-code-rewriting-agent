import { useState, useEffect, useRef } from 'react';
import { Terminal, Play, Loader2, Square } from 'lucide-react'; // Added Square

const API_URL = "http://localhost:8000"; // Make sure this matches Docker port

export default function App() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/jayanthoffl/broken-python-test");
  const [token, setToken] = useState("");
  const [status, setStatus] = useState("IDLE");
  const [logs, setLogs] = useState([]);
  const [isDeploying, setIsDeploying] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Polling Loop
  useEffect(() => {
    let interval;
    if (isDeploying) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_URL}/status`);
          const data = await res.json();
          setStatus(data.status);
          setLogs(data.logs || []);
          if (data.status === "SUCCESS") setIsDeploying(false);
        } catch (e) { console.error("API Error", e); }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isDeploying]);

  const handleDeploy = async () => {
    setIsDeploying(true);
    setLogs(["🚀 Initializing Connection..."]);
    try {
      await fetch(`${API_URL}/deploy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl, github_token: token }),
      });
    } catch (e) {
      setLogs(p => [...p, `❌ Error: ${e.message}`]);
      setIsDeploying(false);
    }
  };

  const handleStop = async () => {
    try {
      await fetch(`${API_URL}/stop`, { method: "POST" });
      setIsDeploying(false); // Stops the React polling loop
      setStatus("STOPPED");
    } catch (e) {
      console.error("Stop failed", e);
    }
  };

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4 border-b border-green-900 pb-4">
        <Terminal className="w-8 h-8" />
        <h1 className="text-2xl font-bold tracking-wider">AUTODEV_OS v2.0</h1>
        <div className="ml-auto px-3 py-1 bg-green-900/30 rounded text-sm">
          STATUS: {status}
        </div>
      </div>

      {/* Input Form */}
      <div className="flex gap-4">
        <input 
          value={repoUrl} 
          onChange={(e) => setRepoUrl(e.target.value)}
          className="flex-1 bg-gray-900 border border-green-800 p-3 rounded focus:outline-none focus:border-green-500"
          placeholder="Repository URL"
        />
        <input 
          type="password"
          value={token} 
          onChange={(e) => setToken(e.target.value)}
          className="w-48 bg-gray-900 border border-green-800 p-3 rounded focus:outline-none focus:border-green-500"
          placeholder="GitHub Token"
        />
        <button 
          onClick={handleDeploy} 
          disabled={isDeploying}
          className="bg-green-700 hover:bg-green-600 text-black font-bold px-6 rounded flex items-center gap-2 disabled:opacity-50"
        >
          {isDeploying ? <Loader2 className="animate-spin" /> : <Play />}
          DEPLOY
        </button>
        {/* --- NEW STOP BUTTON --- */}
        {isDeploying && (
          <button 
            onClick={handleStop}
            className="bg-red-600 hover:bg-red-500 text-white font-bold px-4 rounded flex items-center gap-2"
          >
            <Square className="w-4 h-4 fill-current" />
            STOP
          </button>
        )}
      </div>

      {/* Terminal Window */}
      <div className="flex-1 bg-gray-950 border border-green-800 rounded-lg p-4 h-[500px] overflow-y-auto font-mono text-sm shadow-[0_0_20px_rgba(0,255,65,0.1)]">
        {logs.map((log, i) => (
          <div key={i} className="mb-2 break-words">
            <span className="opacity-50 mr-3">{log.split(']')[0]}]</span>
            <span className={log.includes('🚨') ? 'text-red-500 font-bold' : log.includes('✅') ? 'text-blue-400 font-bold' : ''}>
              {log.split(']').slice(1).join(']')}
            </span>
          </div>
        ))}
        <div ref={scrollRef} />
      </div>
    </div>
  );
}