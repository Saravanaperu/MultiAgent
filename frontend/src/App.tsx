import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:8000'); // Assuming backend is on port 8000

function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [lastTick, setLastTick] = useState<any>(null);

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }

    function onTick(value: any) {
      setLastTick(value);
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('market:tick', onTick);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('market:tick', onTick);
    };
  }, []);

  return (
    <div className="App">
      <h1>Options Scalping System</h1>
      <p>State: {isConnected ? 'Connected' : 'Disconnected'}</p>
      {lastTick && (
        <div>
          <h2>Last Tick</h2>
          <pre>{JSON.stringify(lastTick, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
