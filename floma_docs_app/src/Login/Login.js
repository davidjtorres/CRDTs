// Login.js
import React, { useState } from 'react';
import axiosInstance from './../AxiosInstance';
import { useNavigate } from 'react-router-dom';
import { useSession } from './../ContextProviders/SessionContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { setUser } = useSession();



  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance.post('/token/', { username, password });
      localStorage.setItem('token', response.data.access);
      const userResponse = await axiosInstance.get('/user');
      setUser(userResponse.data);
      navigate('/documents');
    } catch (error) {
      alert('Invalid credentials');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Username:</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
      </div>
      <div>
        <label>Password:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      <button type="submit">Login</button>
    </form>
  );
};

export default Login;