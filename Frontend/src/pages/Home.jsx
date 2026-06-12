import {Link} from 'react-router-dom';

function Home(){
    return(
        <div>
            <section className="hero">
                 <h1>Welcome to the News Aggregation System</h1>
                 <p>Your one-stop destination for personalized news from around the world.</p>
            </section>
            
            <section className = "about">
            <h2> About </h2>
            <p>
                Our News Aggregation System is designed to provide users with a comprehensive and personalized news experience. By aggregating news from various sources, we ensure that users have access to a wide range of perspectives and topics. Our platform allows users to customize their news feed based on their interests, ensuring that they receive relevant and timely information. Whether you're interested in politics, technology, sports, or entertainment, our system has you covered. With a user-friendly interface and advanced algorithms, we strive to deliver the most relevant news content to our users efficiently and effectively.
            </p>
            </section>

            <section className="features">
                <h2>Features</h2>

                <ul>
                    <li>Multi-source News Collection</li>
                    <li>Smart News Grouping</li>
                    <li>Semantic Analysis</li>
                    <li>AI Article Generation</li>
                </ul>
            </section>

            <section className="actions">
            <h2>If you are a new user, Register by clicking the button below</h2>

            <Link to = "/register">
                <button> Register </button>
            </Link>

            <h2>If you are an existing user, Login by clicking the button below</h2>

            <Link to = "/login">
                <button> Login </button>
            </Link>
            </section>

        </div>
    );
}

export default Home;