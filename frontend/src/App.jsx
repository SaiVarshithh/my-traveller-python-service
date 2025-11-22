import React, { useState } from 'react';
import { ApolloProvider } from '@apollo/client';
import client from './graphql/client';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import Navbar from './components/common/Navbar';
import AnimatedBackground from './components/common/AnimatedBackground';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <>
      <AnimatedBackground />
      {isLogin ? (
        <Login onToggle={() => setIsLogin(false)} />
      ) : (
        <Register onToggle={() => setIsLogin(true)} />
      )}
    </>
  );
};

const MainApp = () => {
  const { user, logout, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        fontSize: '2rem'
      }}>
        <div style={{
          width: '60px',
          height: '60px',
          border: '6px solid rgba(255, 255, 255, 0.3)',
          borderTopColor: 'white',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite'
        }}></div>
      </div>
    );
  }

  return (
    <>
      <AnimatedBackground />
      {user ? (
        <>
          <Navbar user={user} onLogout={logout} />
          <Dashboard />
        </>
      ) : (
        <AuthPage />
      )}
    </>
  );
};

function App() {
  return (
    <ApolloProvider client={client}>
      <AuthProvider>
        <MainApp />
      </AuthProvider>
    </ApolloProvider>
  );
}

export default App;