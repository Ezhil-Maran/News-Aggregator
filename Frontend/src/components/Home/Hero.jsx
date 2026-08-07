import { useEffect, useState } from "react";
import { fetchNews } from "../../services/api";

const Hero = () => {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadNews() {
      try {
        const data = await fetchNews();

        if (
          data.generated_articles &&
          data.generated_articles.length > 0
        ) {
          setArticle(data.generated_articles[0]);
        } else {
          setError("No AI-generated articles available.");
        }
      } catch (err) {
        setError("Unable to load AI summary.");
      } finally {
        setLoading(false);
      }
    }

    loadNews();
  }, []);

  return (
    <section className="relative min-h-screen bg-slate-950 overflow-hidden">

      {/* Background Glow */}
      <div className="absolute top-20 left-20 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl"></div>
      <div className="absolute bottom-20 right-20 h-96 w-96 rounded-full bg-purple-600/20 blur-3xl"></div>

      <div className="relative max-w-7xl mx-auto px-8 py-24 flex flex-col lg:flex-row items-center justify-between">

        {/* Left Side */}
        <div className="max-w-2xl">

          <p className="text-blue-400 font-semibold mb-4 tracking-widest uppercase">
            AI Powered News Aggregation
          </p>

          <h1 className="text-5xl lg:text-7xl font-extrabold leading-tight">

            Stay Ahead with

            <span className="block bg-gradient-to-r from-blue-400 via-cyan-300 to-purple-500 bg-clip-text text-transparent">
              Intelligent News
            </span>

          </h1>

          <p className="mt-8 text-slate-300 text-lg leading-8">

            Aggregate articles from multiple trusted sources,
            generate AI-powered summaries using Qwen,
            compare viewpoints, and stay informed without information overload.

          </p>

          <div className="mt-10 flex flex-wrap gap-4">

            <button className="px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-700 transition font-semibold">
              Get Started
            </button>

            <button className="px-8 py-4 rounded-xl border border-slate-600 hover:border-blue-400 transition font-semibold">
              Learn More
            </button>

          </div>

        </div>

        {/* Right Side */}

        <div className="mt-20 lg:mt-0">

          <div className="w-[420px] rounded-3xl border border-slate-700 bg-slate-900/70 backdrop-blur-lg p-8 shadow-2xl">

            <h3 className="text-2xl font-bold mb-6">
              Live AI Summary
            </h3>

            {loading && (
              <div className="rounded-xl bg-slate-800 p-5">
                <p className="text-blue-400 font-semibold">
                  Generating today's news...
                </p>

                <p className="mt-3 text-slate-400 text-sm">
                  Fetching RSS feeds, clustering related articles,
                  and generating an AI summary...
                </p>
              </div>
            )}

            {!loading && error && (
              <div className="rounded-xl bg-red-900/30 border border-red-500/30 p-5">
                <p className="text-red-400 font-semibold">
                  {error}
                </p>
              </div>
            )}

            {!loading && article && (
              <div className="space-y-5">

                <div className="rounded-xl bg-slate-800 p-5">

                  <h4 className="font-semibold text-lg text-white">
                    {article.headline}
                  </h4>

                  <p className="mt-4 text-slate-400 text-sm leading-7">
                    {article.content.length > 280
                      ? article.content.substring(0, 280) + "..."
                      : article.content}
                  </p>

                </div>

                <div className="rounded-xl bg-slate-800 p-5">

                  <h4 className="font-semibold mb-3">
                    Sources
                  </h4>

                  <div className="flex flex-wrap gap-2">

                    {article.sources.map((source) => (
                      <span
                        key={source}
                        className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs"
                      >
                        {source}
                      </span>
                    ))}

                  </div>

                </div>

              </div>
            )}

          </div>

        </div>

      </div>

    </section>
  );
};

export default Hero;