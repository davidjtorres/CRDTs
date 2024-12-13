import React from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav>
      <h1>My App</h1>
      <button onClick={handleLogout}>Logout</button>
    </nav>
  );
};

export default Navbar;