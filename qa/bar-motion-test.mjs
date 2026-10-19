import { spawn } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const file = process.cwd() + '/精神健康系统-阅读汇报.html';
const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'dsh-bar-'));
const port = 9777;
const proc = spawn(CHROME, ['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--no-default-browser-check','--disable-extensions','--disable-dev-shm-usage','--remote-debugging-port='+port,'--user-data-dir='+ud,'about:blank'], {stdio:'ignore'});
const sleep = ms => new Promise(r=>setTimeout(r,ms));
let target;
for (let i=0;i<100;i++) { try { const list = await (await fetch('http://127.0.0.1:'+port+'/json/list')).json(); target = list.find(t=>t.type==='page'); if(target) break; } catch(e){} await sleep(150); }
if (!target) { console.log('no target'); proc.kill(); process.exit(1); }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res,rej)=>{ws.addEventListener('open',res);ws.addEventListener('error',rej);});
let id=0; const pending=new Map();
ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data); if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}});
const send=(method,params={})=>{const i=++id;return new Promise((res,rej)=>{pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params}));});};
await send('Page.enable'); await send('Runtime.enable');
await send('Page.navigate',{url:'file://'+file+'?p=8'});
await sleep(1000);
await send('Runtime.evaluate',{expression:"window.__deck.goTo(8,{force:true}); 1"});
const read = async () => {
  const expr = "(function(){var b76=document.querySelector('[data-bar=\".76\"]');var b07=document.querySelector('[data-bar=\".07\"]');function info(b){var a=b&&b.getAnimations()[0];return {transform:getComputedStyle(b).transform, anim:a?a.playState:null, ct:a?a.currentTime:null};}return JSON.stringify({b76:info(b76), b07:info(b07)});})()";
  const r = await send('Runtime.evaluate',{expression:expr,returnByValue:true});
  return r.result.value;
};
const out = {};
await sleep(120); out.t120 = await read();
await sleep(400); out.t520 = await read();
await sleep(700); out.t1220 = await read();
fs.writeFileSync(path.join(process.cwd(),'qa','bar-motion.json'), JSON.stringify(out,null,2));
console.log(JSON.stringify(out,null,2));
ws.close(); proc.kill(); await sleep(300); try { fs.rmSync(ud,{recursive:true,force:true,maxRetries:5}); } catch(e) {}
