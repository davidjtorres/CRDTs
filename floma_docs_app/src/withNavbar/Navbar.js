import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from './../ContextProviders/SessionContext';

const Navbar = () => {
    const navigate = useNavigate();
    const { user } = useSession();

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <nav>
            <h1>Floma Docs</h1>
            <div>
                <span  style={{ marginRight: '10px' }}>
                    {user?.username}
                </span>
                <button onClick={handleLogout}>Logout</button>
            </div>
        </nav>
    );
};

export default Navbar;
