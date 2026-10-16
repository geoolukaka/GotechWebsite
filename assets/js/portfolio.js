var PR=window.PROJECTS||[];
var $=function(i){return document.getElementById(i)},cur=0,fl="all",o=$("out");
function list(){return PR.filter(function(p){return fl==="all"||p.c===fl})}
function show(f){fl=f;var L=list();$("cnt").textContent="("+L.length+")";$("pg").innerHTML="";
L.forEach(function(p){var b=document.createElement("button");b.className="card";b.innerHTML="<div><span class=perm></span><h3></h3><p></p><div class=tags></div></div>";if(p.imgs&&p.imgs[0]){var im=document.createElement("img");im.src=p.imgs[0];im.alt=p.n;im.loading="lazy";b.insertBefore(im,b.firstChild)}b.querySelector("p").textContent=p.d;b.querySelector(".perm").textContent="drwxr-xr-x "+p.k+"/"+(p.link?"  · live site":"");b.querySelector("h3").textContent=p.n;p.tg.slice(0,3).forEach(function(t){var s=document.createElement("span");s.textContent=t;b.querySelector(".tags").appendChild(s)});b.onclick=function(){openP(p)};$("pg").appendChild(b)});
[].forEach.call($("flt").children,function(x){x.setAttribute("aria-pressed",x.dataset.f===f)})}
[["all","All"],["brand","Brand identity"],["web","Websites"],["software","Software"]].forEach(function(f){var b=document.createElement("button");b.textContent=f[1];b.dataset.f=f[0];b.onclick=function(){show(f[0])};$("flt").appendChild(b)});show("all");
function gal(p,i){var im=p.imgs||[],b=$("db"),t=$("dth");t.innerHTML="";if(!im.length){b.hidden=true;return}b.hidden=false;b.src=im[i];b.alt=p.n+" - image "+(i+1);if(im.length>1)im.forEach(function(sr,j){var x=document.createElement("button");x.setAttribute("aria-label","Image "+(j+1));if(j===i)x.setAttribute("aria-current","true");var g=document.createElement("img");g.src=sr;g.alt="";x.appendChild(g);x.onclick=function(){gal(p,j)};t.appendChild(x)})}
function openP(p){cur=PR.indexOf(p);gal(p,0);var L=$("dl");if(p.link){L.href=p.link;L.hidden=false}else L.hidden=true;$("dt").textContent=p.n;$("dd").textContent=p.d;$("dc").innerHTML="";p.tg.forEach(function(t){var s=document.createElement("span");s.textContent=t;$("dc").appendChild(s)});
var q=$("dq");if(p.q){q.hidden=false;q.innerHTML="<span></span><b></b>";q.children[0].textContent="\u201C"+p.q[0]+"\u201D";q.children[1].textContent=p.q[1]}else q.hidden=true;
if(!$("dg").open)$("dg").showModal();try{history.replaceState(null,"","#"+p.k)}catch(e){}}
function step(n){cur=(cur+n+PR.length)%PR.length;openP(PR[cur])}
$("pv").onclick=function(){step(-1)};$("nx").onclick=function(){step(1)};
function closeD(){$("dg").close();try{history.replaceState(null,"",location.pathname)}catch(e){}}
$("dx").onclick=closeD;$("dg").onclick=function(e){if(e.target===$("dg"))closeD()};
document.addEventListener("keydown",function(e){if($("dg").open){if(e.key==="ArrowRight")step(1);if(e.key==="ArrowLeft")step(-1)}});
var r=document.documentElement;try{var th=localStorage.getItem("gt-theme");if(th)r.dataset.theme=th}catch(e){}
$("theme").onclick=function(){var d=r.dataset.theme?r.dataset.theme==="dark":!matchMedia("(prefers-color-scheme:light)").matches;var n=d?"light":"dark";r.dataset.theme=n;try{localStorage.setItem("gt-theme",n)}catch(e){}};
function pr(t,c){var d=document.createElement("div");if(c)d.className=c;d.textContent=t;o.appendChild(d);o.scrollTop=o.scrollHeight}
function prl(t,u){var d=document.createElement("div"),a=document.createElement("a");a.href=u;a.target="_blank";a.rel="noopener";a.textContent=t;d.appendChild(a);o.appendChild(d);o.scrollTop=o.scrollHeight}
function find(a){return PR.filter(function(x){return a&&(x.k===a||x.n.toLowerCase().indexOf(a)>-1)})[0]}
var CM={help:function(){pr("ls              list projects\nopen <name>     view a project\nfilter <type>   all | brand | web | software\nvisit <name>    open a project's live website\nclear           clear screen\ntheme           switch light/dark","m")},
ls:function(){list().forEach(function(p){pr("drwxr-xr-x  "+p.k+"/  "+p.tg.join(" · "),"m")});if(PR[0])pr("try: open "+PR[0].k,"c")},
open:function(a){var p=find(a);if(p){pr("opening "+p.k+"/","c");openP(p)}else pr("usage: open <"+PR.map(function(x){return x.k}).join("|")+">","m")},
filter:function(a){if(["all","brand","web","software"].indexOf(a)>-1){show(a);pr("showing "+a,"c");CM.ls()}else pr("usage: filter <all|brand|web|software>","m")},
visit:function(a){var p=find(a);if(!p){var L=PR.filter(function(x){return x.link}).map(function(x){return x.k});pr("usage: visit <"+(L.join("|")||"name")+">","m");return}if(!p.link){pr(p.k+" has no live website.","m");return}pr("opening "+p.link,"c");prl(p.link,p.link);window.open(p.link,"_blank","noopener")},
theme:function(){$("theme").click();pr("theme switched","m")},clear:function(){o.innerHTML=""}};
pr("GoTech Solutions — portfolio","c");pr("Type help, or tap a command below.","m");
["help","ls",PR[0]?"open "+PR[0].k:"help","visit sallytrends"].forEach(function(c){var b=document.createElement("button");b.textContent=c;b.onclick=function(){run(c)};$("chips").appendChild(b)});
function run(v){v=v.trim();if(!v)return;pr("$ "+v,"c");var p=v.split(/\s+/),f=CM[p[0].toLowerCase()];f?f(p.slice(1).join(" ").toLowerCase()):pr("command not found: "+p[0]+". try help","m")}
$("tf").onsubmit=function(e){e.preventDefault();run($("ti").value);$("ti").value=""};
var h=find(location.hash.slice(1).toLowerCase());if(h)openP(h);
