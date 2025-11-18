import React, { useState, useEffect } from 'react';
import { onAuthStateChange, logout } from './services/auth';
import Login from './components/Login';
import ChatWindow from './components/ChatWindow';
import './App.css';

function App() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChange((user) => {
      setUser(user);
    });
    return unsubscribe;
  }, []);

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>新谷ラボ AI-CHATBOT</h1>
        {user && (
          <button onClick={handleLogout}>
            Logout
          </button>
        )}
      </header>
      <main>
        {user ? <ChatWindow /> : <Login onLogin={() => {}} />}
      </main>
    </div>
  );
}

export default App;
