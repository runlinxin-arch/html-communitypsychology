import { spawn } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const file = process.cwd() + '/精神健康系统-阅读汇报.html';
const ud = fs.mkdtempSync(path.join(os.tmpdir(), 'dsh-fs-'));
const port = 9666;
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
await send('Page.navigate',{url:'file://'+file});
await sleep(1200);
const expr = "(async()=>{ if(!document.documentElement.requestFullscreen) return 'no-api'; try { await document.documentElement.requestFullscreen(); return document.fullscreenElement ? 'fullscreen' : 'no-element'; } catch(e){ return 'error:'+e.name+':'+e.message; } })()";
const r = await send('Runtime.evaluate',{expression:expr,awaitPromise:true,userGesture:true,returnByValue:true});
const r2 = await send('Runtime.evaluate',{expression:"typeof document.documentElement.requestFullscreen+'|'+typeof document.documentElement.webkitRequestFullscreen",returnByValue:true});
await send('Page.navigate',{url:'file://'+file});
await sleep(1200);
await send('Runtime.evaluate',{expression:"document.dispatchEvent(new KeyboardEvent('keydown',{key:'f',bubbles:true})); 1",userGesture:true});
await sleep(700);
const r3 = await send('Runtime.evaluate',{expression:"document.fullscreenElement ? 'fullscreen' : 'no-element'",returnByValue:true});
const out = { api: r2.result.value, direct: r.result.value, keyHandler: r3.result.value, ok: r.result.value === 'fullscreen' && r3.result.value === 'fullscreen' };
fs.writeFileSync(path.join(process.cwd(),'qa','fullscreen.json'), JSON.stringify(out,null,2));
console.log(JSON.stringify(out));
ws.close(); proc.kill();
await sleep(300);
try { fs.rmSync(ud,{recursive:true,force:true,maxRetries:5}); } catch(e) {}
