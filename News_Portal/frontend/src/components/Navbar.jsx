import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Menu, X, User, Bookmark, LogOut, Search } from 'lucide-react';
import { useAuth } from '../App';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMenuOpen(false);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <h1>NewsPortal</h1>
        </Link>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="navbar-search">
          <div className="search-input-group">
            <Search className="search-icon" size={20} />
            <input
              type="text"
              placeholder="Search news..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
        </form>

        {/* Desktop Menu */}
        <div className="navbar-menu">
          <Link 
            to="/" 
            className={`navbar-link ${isActive('/') ? 'active' : ''}`}
          >
            Home
          </Link>
          
          {user && (
            <Link 
              to="/bookmarks" 
              className={`navbar-link ${isActive('/bookmarks') ? 'active' : ''}`}
            >
              <Bookmark size={18} />
              Bookmarks
            </Link>
          )}

          {user ? (
            <div className="navbar-user">
              <span className="user-greeting">Welcome, {user.username}</span>
              <button onClick={handleLogout} className="logout-btn">
                <LogOut size={18} />
                Logout
              </button>
            </div>
          ) : (
            <div className="navbar-auth">
              <Link to="/login" className="navbar-link">
                <User size={18} />
                Login
              </Link>
              <Link to="/signup" className="navbar-link signup-link">
                Sign Up
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          className="mobile-menu-btn"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="mobile-menu">
          <Link 
            to="/" 
            className={`mobile-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => setIsMenuOpen(false)}
          >
            Home
          </Link>
          
          {user && (
            <Link 
              to="/bookmarks" 
              className={`mobile-link ${isActive('/bookmarks') ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              <Bookmark size={18} />
              Bookmarks
            </Link>
          )}

          {user ? (
            <div className="mobile-user">
              <span className="user-info">Welcome, {user.username}</span>
              <button onClick={handleLogout} className="mobile-logout-btn">
                <LogOut size={18} />
                Logout
              </button>
            </div>
          ) : (
            <div className="mobile-auth">
              <Link 
                to="/login" 
                className="mobile-link"
                onClick={() => setIsMenuOpen(false)}
              >
                <User size={18} />
                Login
              </Link>
              <Link 
                to="/signup" 
                className="mobile-link signup-link"
                onClick={() => setIsMenuOpen(false)}
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;