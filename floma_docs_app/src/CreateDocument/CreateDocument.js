import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from './../AxiosInstance';

const CreateDocument = () => {
  const [title, setTitle] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post('/documents/', { title });
      navigate('/documents');
    } catch (error) {
      alert('Document creation failed');
    }
  };

  return (
    <div>
      <h1>Create Document</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <button type="submit">Create</button>
      </form>
    </div>
  );
};

export default CreateDocument;