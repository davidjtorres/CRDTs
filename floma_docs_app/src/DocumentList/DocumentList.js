import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axiosInstance from './../AxiosInstance';

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await axiosInstance.get('/documents/');
        setDocuments(response.data);
      } catch (error) {
        console.error('Failed to fetch documents', error);
      }
    };

    fetchDocuments();
  }, []);

  return (
    <div>
      <h1>Documents</h1>
      <Link to="/create-document">Create Document</Link>
      <ul>
        {documents.map((doc) => (
          <li key={doc.id}>
            <Link to={`/document/${doc.id}`}>{doc.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentList;