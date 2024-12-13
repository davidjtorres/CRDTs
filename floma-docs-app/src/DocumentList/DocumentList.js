// DocumentList.js
import React, { useEffect, useState } from 'react';
import axiosInstance from './../AxiosInstance';

const DocumentList = () => {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await axiosInstance.get('/documents');
        setDocuments(response.data);
      } catch (error) {
        console.error('Failed to fetch documents', error);
      }
    };

    fetchDocuments();
  }, []);

  return (
    <div>
      <h1>Document List</h1>
      <ul>
        {documents.map((doc) => (
          <li key={doc.id}>{doc.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default DocumentList;