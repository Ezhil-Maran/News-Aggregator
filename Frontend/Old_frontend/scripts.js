const API_URL = "http://127.0.0.1:8000/news";

let singleArticles = [];
let multiArticles = [];

function readingTime(text){
const words = text.split(" ").length;
return `${Math.max(1,Math.ceil(words/200))} min read`;
}

/* MULTI SOURCE */

function renderMultiSource(articles){

const container=document.getElementById("multiSource");
container.innerHTML="";

articles.forEach(item=>{

const card=document.createElement("div");
card.className="news-card";

card.innerHTML=`

<h3>${item.title}</h3>

<p class="meta">
${item.publisher_count} sources • ${readingTime(item.summary)}
</p>

<div class="summary">${item.summary}</div>

<div class="read-more">Read more ↓</div>

<ul class="sources">
${item.sources.slice(0,3).map(s=>`
<li><a href="${s}" target="_blank">Source</a></li>
`).join("")}
</ul>

`;

card.addEventListener("click",()=>{
card.classList.toggle("expanded");
});

container.appendChild(card);

});

}

/* SINGLE SOURCE */

function renderSingleSource(articles){

const container=document.getElementById("singleSource");
container.innerHTML="";

articles.forEach(item=>{

const card=document.createElement("div");
card.className="news-card";

card.innerHTML=`

<h3>${item.title}</h3>

<p class="meta">
${item.domain} • ${readingTime(item.content)}
</p>

<div class="summary">${item.content}</div>

<div class="article-content">
<a href="${item.link}" target="_blank">Read full article →</a>
</div>

`;

card.addEventListener("click",()=>{
card.classList.toggle("expanded");
});

container.appendChild(card);

});

}

/* FETCH */

async function fetchNews(){

const res=await fetch(API_URL);
const data=await res.json();

singleArticles=data.single_source_articles;
multiArticles=data.multi_source_articles;

renderMultiSource(multiArticles);
renderSingleSource(singleArticles);

}

/* SEARCH */

document.getElementById("searchInput").addEventListener("input",(e)=>{

const text=e.target.value.toLowerCase();

renderMultiSource(
multiArticles.filter(a =>
a.title.includes(text) || a.summary.includes(text)
)
);

renderSingleSource(
singleArticles.filter(a =>
a.title.includes(text) || a.content.includes(text)
)
);

});

document.addEventListener("DOMContentLoaded",fetchNews);