// scripts.js
const API_URL = "http://127.0.0.1:8000/news";

function renderSingleSource(articles) {
  const container = document.getElementById("singleSource");
  container.innerHTML = "";

  if (!articles || articles.length === 0) {
    container.innerHTML = "<p>No articles available.</p>";
    return;
  }

  articles.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "news-card";

    const contentId = `single-content-${index}`;

    card.innerHTML = `
      <h3 class="clickable-title" data-target="${contentId}">
        ${item.title}
      </h3>
      <p class="source">Source: ${item.domain}</p>

      <div id="${contentId}" class="article-content hidden">
        <p>${item.content}</p>
        <p class="original-link">
          <a href="${item.link}" target="_blank" rel="noopener noreferrer">
            🔗 Read original article
          </a>
        </p>
      </div>
    `;

    container.appendChild(card);
  });

  // Add click handlers
  document.querySelectorAll(".clickable-title").forEach(el => {
    el.addEventListener("click", () => {
      const target = document.getElementById(el.dataset.target);
      target.classList.toggle("hidden");
    });
  });
}

function renderMultiSource(articles) {
  const container = document.getElementById("multiSource");
  container.innerHTML = "";

  if (!articles || articles.length === 0) {
    container.innerHTML = "<p>No unified articles available.</p>";
    return;
  }

  articles.forEach(item => {
    const div = document.createElement("div");
    div.className = "news-card unified";

    div.innerHTML = `
      <h3>${item.title}</h3>
      <p class="meta">Sources used: ${item.publisher_count}</p>
      <div class="summary">
  <p>${item.summary}</p>
</div>

      <ul class="sources">
        ${item.sources.map(s => `<li><a href="${s}" target="_blank">${s}</a></li>`).join("")}
      </ul>
    `;

    container.appendChild(div);
  });
}

async function fetchNews() {
  try {
    const res = await fetch(API_URL);
    const data = await res.json();

    renderMultiSource(data.multi_source_articles);
    renderSingleSource(data.single_source_articles);
  } catch (err) {
    console.error("Failed to fetch news", err);
  }
}

document.addEventListener("DOMContentLoaded", fetchNews);
