import"./modulepreload-polyfill-xwJNGKPl.js";/* empty css              */var e={version:"0.9.2",dirty:!1,timestamp:1702400076973,time:"12/12/2023, 17:54:36",revision:"3f2e0eb"};document.title="MPyC Web - Bench Channels"+(e.deployment?` (${e.deployment})`:""),function(){let e=document.querySelector("#out");function o(o,t,s){e.innerHTML+=`${o}, ${n(t/1e3)}, ${n(1e3*s/t)} <br>`}function n(e){return(Math.round(100*e)/100).toLocaleString()}let t=3e6,s=new MessageChannel,r=0;s.port1.onmessage=e=>{if(r+=1,r>999990&&(o("done up to",1e3*r,0),o("n=",1e3*t,0),s.port2.postMessage(void 0)),r%1e5==0&&(o("done up to",1e3*r,0),o("n=",1e3*t,0),s.port2.postMessage(void 0)),r>=t){s.port2.postMessage(void 0),o("done receiving",performance.now()-i,t)}},console.log("start sending"),o("start sending",1,1);let i=performance.now();for(let d=0;d<t;d++)s.port2.postMessage(void 0);let l=performance.now()-i;o("done sending",l,t),console.log("done sending",n(l/1e3),n(1e3*t/l))}();
//# sourceMappingURL=index-D31lzpka.js.map
