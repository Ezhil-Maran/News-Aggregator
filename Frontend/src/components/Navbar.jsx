import { Link } from "react-router-dom";

function Navbar() {
    return (
        <nav className="navbar">
            <h2>News Aggregator</h2>

            <div className="nav-links">
                <Link to="/">Home</Link>
                <Link to="/login">Login</Link>
                <Link to="/register">Register</Link>
            </div>
        </nav>
    );
}

export default Navbar;