// components/Header.tsx
import React from 'react';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-logo">
        {/* 假設 logo.png 放在 public 資料夾中 */}
        <img src="/logo.png" alt="Logo" />
        <span className="header-text">Sit Smart Detector</span>
      </div>
    </header>
  );
};

export default Header;
