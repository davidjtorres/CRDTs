import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './Login/Login';
import DocumentEditor from './DocumentEditor/DocumentEditor';
import DocumentList from './DocumentList/DocumentList';
import PrivateRoute from './PrivateRoute/PrivateRoute';
import withNavbar from './withNavbar/withNavbar';
import CreateDocument from './CreateDocument/CreateDocument';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/document/:document_id" element={<PrivateRoute element={withNavbar(DocumentEditor)} />} />
        <Route path="/documents" element={<PrivateRoute element={withNavbar(DocumentList)} />} />
        <Route path="/create-document" element={<PrivateRoute element={withNavbar(CreateDocument)} />} />
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </Router>
  );
};


export default App;