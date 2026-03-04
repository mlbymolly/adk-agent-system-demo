import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';

const Dashboard = () => {
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const createProject = async () => {
    setLoading(true);
    const res = await fetch('http://localhost:8000/sdlc/v2/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'New Migration', repo_url: repoUrl })
    });
    const data = await res.json();
    setProject(data);
    setLoading(false);
  };

  const generatePlan = async () => {
    await fetch(`http://localhost:8000/sdlc/v2/projects/${project.id}/plan`, { method: 'POST' });
    alert('Plan generated!');
  };

  const approvePlan = async () => {
    await fetch(`http://localhost:8000/sdlc/v2/projects/${project.id}/approve`, { method: 'POST' });
    pollStatus();
  };

  const pollStatus = () => {
    setInterval(async () => {
      const res = await fetch(`http://localhost:8000/sdlc/v2/projects/${project.id}/status`);
      const data = await res.json();
      setTasks(data.tasks);
    }, 2000);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-blue-600">AI SDLC Orchestrator</h1>

      {!project ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <label className="block text-sm font-medium text-gray-700 mb-2">Target Repository URL</label>
          <input
            type="text"
            className="w-full p-2 border rounded mb-4"
            placeholder="https://github.com/user/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
          />
          <button
            onClick={createProject}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? 'Initializing...' : 'Start Migration'}
          </button>
        </div>
      ) : (
        <div>
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-2">{project.name}</h2>
            <p className="text-gray-600 mb-4">{project.repo_url}</p>
            <div className="flex space-x-4">
              <button onClick={generatePlan} className="bg-green-600 text-white px-4 py-2 rounded">1. Generate Plan</button>
              <button onClick={approvePlan} className="bg-purple-600 text-white px-4 py-2 rounded">2. Approve & Execute</button>
            </div>
          </div>

          <h3 className="text-xl font-bold mb-4">Task Execution DAG</h3>
          <div className="space-y-4">
            {tasks.map(task => (
              <div key={task.id} className={`p-4 rounded-lg border-l-4 ${
                task.status === 'completed' ? 'bg-green-50 border-green-500' :
                task.status === 'in_progress' ? 'bg-blue-50 border-blue-500 animate-pulse' :
                'bg-gray-50 border-gray-300'
              }`}>
                <div className="flex justify-between items-center">
                  <span className="font-medium">{task.title}</span>
                  <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                    task.status === 'completed' ? 'text-green-700' :
                    task.status === 'in_progress' ? 'text-blue-700' : 'text-gray-500'
                  }`}>{task.status}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{task.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Dashboard />);
