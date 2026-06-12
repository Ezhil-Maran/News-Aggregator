function Register() {
    return (
        <div className="auth-container">
            <form className="auth-form">
                <h2>Create Account</h2>

                <input
                    type="text"
                    placeholder="Username"
                />

                <input
                    type="email"
                    placeholder="Email"
                />

                <input
                    type="password"
                    placeholder="Password"
                />

                <input
                    type="password"
                    placeholder="Confirm Password"
                />

                <button type="submit">
                    Register
                </button>
            </form>
        </div>
    );
}

export default Register;