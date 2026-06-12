function Login() {
    return (
        <div className="auth-container">
            <form className="auth-form">
                <h2>Login</h2>

                <input
                    type="email"
                    placeholder="Email"
                />

                <input
                    type="password"
                    placeholder="Password"
                />

                <button type="submit">
                    Login
                </button>
            </form>
        </div>
    );
}

export default Login;