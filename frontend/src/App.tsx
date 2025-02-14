// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ViewerPage from './pages/ViewerPage';
import Header from './components/Header';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />
      <div className="content-container">
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/viewer" element={<ViewerPage />} />
            {/* 其餘路徑導向 Login 頁面 */}
            <Route path="*" element={<Navigate to="/login" />} />
          </Routes>
        </Router>
      </div>
    </div>
  );
};

export default App;
