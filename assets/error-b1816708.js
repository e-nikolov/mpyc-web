import{h as r,__tla as __tla_0}from"./index-4e437038.js";let n;let __tla=Promise.all([(()=>{try{return __tla_0}catch{}})()]).then(async()=>{r.onInterpreterReady.add(function o(e){r.onInterpreterReady.delete(o);const{stderr:d}=e.io;e.io.stderr=(t,...a)=>(n(t.message||t),d(t,...a)),addEventListener("error",({message:t})=>{t.startsWith("Uncaught PythonError")&&n(t)})});n=function(o){const e=document.createElement("div");e.className="py-error",e.textContent=o,e.style.cssText=`
    border: 1px solid red;
    background: #ffdddd;
    color: black;
    font-family: courier, monospace;
    white-space: pre;
    overflow-x: auto;
    padding: 8px;
    margin-top: 8px;
  `,document.body.append(e)}});export{n as notify,__tla};