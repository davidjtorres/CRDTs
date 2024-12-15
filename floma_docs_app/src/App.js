import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './Login/Login';
import DocumentEditor from './DocumentEditor/DocumentEditor';
import DocumentList from './DocumentList/DocumentList';
import PrivateRoute from './PrivateRoute/PrivateRoute';
import withNavbar from './withNavbar/withNavbar';
import CreateDocument from './CreateDocument/CreateDocument';
import axiosInstance from './AxiosInstance';
import { useSession } from './ContextProviders/SessionContext';

const App = () => {
    const { setUser } = useSession();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await axiosInstance.get('/user');
                setUser(response.data);
            } catch (error) {
                console.log('Failed to fetch user');
            }
        };
        fetchUser();
    }, [setUser]);

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                    path="/document/:document_id"
                    element={
                        <PrivateRoute element={withNavbar(DocumentEditor)} />
                    }
                />
                <Route
                    path="/documents"
                    element={
                        <PrivateRoute element={withNavbar(DocumentList)} />
                    }
                />
                <Route
                    path="/create-document"
                    element={
                        <PrivateRoute element={withNavbar(CreateDocument)} />
                    }
                />
                <Route path="/" element={<Navigate to="/documents" />} />
            </Routes>
        </Router>
    );
};

export default App;
