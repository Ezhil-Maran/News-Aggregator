const API_URL = "http://127.0.0.1:8000/news";

let singleArticles = [];
let multiArticles = [];

function readingTime(text){
const words = text.split(" ").length;
const minutes = Math.max(1,Math.ceil(words/200));
return `${minutes} min read`;
}

/* unified articles */

function renderMultiSource(articles){

const container=document.getElementById("multiSource");
container.innerHTML="";

articles.forEach(item=>{

const card=document.createElement("div");
card.className="news-card";

card.innerHTML=`

<h3>${item.title}</h3>

<p class="meta">
Sources used: ${item.publisher_count} • ${readingTime(item.summary)}
</p>

<div class="summary">
<p>${item.summary}</p>
</div>

<ul class="sources">
${item.sources.map(s=>`
<li><a href="${s}" target="_blank">${s}</a></li>
`).join("")}
</ul>

`;

container.appendChild(card);

});

}

/* single articles */

function renderSingleSource(articles){

const container=document.getElementById("singleSource");
container.innerHTML="";

articles.forEach((item,index)=>{

const card=document.createElement("div");
card.className="news-card";

const contentId=`single-${index}`;

card.innerHTML=`

<h3 class="clickable-title" data-target="${contentId}">
${item.title}
</h3>

<p class="meta">
Source: ${item.domain} • ${readingTime(item.content)}
</p>

<div id="${contentId}" class="article-content hidden">

<p>${item.content}</p>

<p>
<a href="${item.link}" target="_blank">
Read original article →
</a>
</p>

</div>

`;

container.appendChild(card);

});

addClickEvents();

}

function addClickEvents(){

document.querySelectorAll(".clickable-title").forEach(el=>{

el.addEventListener("click",()=>{

const target=document.getElementById(el.dataset.target);
target.classList.toggle("hidden");

});

});

}

/* fetch */

async function fetchNews(){

const res=await fetch(API_URL);
const data=await res.json();

singleArticles=data.single_source_articles;
multiArticles=data.multi_source_articles;

renderMultiSource(multiArticles);
renderSingleSource(singleArticles);

}

/* search */

document.getElementById("searchInput").addEventListener("input",(e)=>{

const text=e.target.value.toLowerCase();

const filteredMulti = multiArticles.filter(a =>
a.title.toLowerCase().includes(text) ||
a.summary.toLowerCase().includes(text)
);

const filteredSingle = singleArticles.filter(a =>
a.title.toLowerCase().includes(text) ||
a.content.toLowerCase().includes(text)
);

renderMultiSource(filteredMulti);
renderSingleSource(filteredSingle);

});

document.addEventListener("DOMContentLoaded",fetchNews);
