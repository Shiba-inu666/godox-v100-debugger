'use strict';
const $=id=>document.getElementById(id), token=document.querySelector('meta[name="debug-token"]').content;
const order=['M','SUB','A','B','C','D'];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const actionNames={rotate:'旋钮',select:'选择',touch:'触摸编辑',set:'SET',back:'返回',mode:'模式',toggle:'SUB 开关',page:'切页',decimal:'功率显示',presence:'附件状态',step:'步进',sensor:'ZOOM 格式',channel:'信道',radio:'无线编码',serialize:'设置记录',role:'无线角色',flash_mode:'闪光模式',menu:'菜单',setting:'设置',rx_group:'接收组',rx_inject:'模拟接收',lock:'输入锁',zoom_auto:'ZOOM AUTO'};
const actionValue=v=>v&&typeof v==='object'?Object.entries(v).map(([k,x])=>`${k}=${x}`).join(' · '):v??'';
let state=null,queue=Promise.resolve(),pendingReplay=null,replayPosition=0,busy=0;
for(let i=1;i<=32;i++)$('channel').add(new Option(String(i).padStart(2,'0'),String(i)));
function notify(t){$('notice').textContent=t}
async function request(path,body){
 const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Token':token},body:JSON.stringify(body)});
 const s=await r.json();if(!r.ok)throw Error(s.error||'请求失败');return s;
}
function task(fn){busy++;$('connection').textContent='处理中';queue=queue.then(fn).catch(e=>{$('error').textContent=e.message}).finally(()=>{busy--;if(!busy)$('connection').textContent='已连接 · 原厂参数引擎'});return queue}
function send(action,value){return task(async()=>{const s=await request('/api/action',{action,value});$('error').textContent='';render(s);const log=s.logs.at(-1);notify(action==='undo'?'已撤销一步；状态由原厂函数重新执行恢复。':action==='redo'?'已重做一步。':log?`${actionNames[log.action]||log.action}完成 · ${log.calls.length?'已执行原厂函数':'电脑端适配'} · ${Object.keys(log.diff).length} 个监视字节变化`:'已恢复初始测试场景')})}
function render(s){
 state=s;$('online').className='ok';$('channelLabel').textContent=s.screen==='hotshoe'?'':('CH '+String(s.channel).padStart(2,'0'));$('roleLabel').textContent=s.panel==='menu'?'MENU':s.screen_label;$('lockLabel').textContent=s.locked?'LOCK':s.screen==='hotshoe'?s.flash_mode:'2.4G';$('lock').classList.toggle('active',s.locked);
 document.querySelectorAll('[data-role]').forEach(b=>b.classList.toggle('active',b.dataset.role===s.screen));
 const modes=s.screen==='sender'?[['M','分组 Group'],['Multi','Multi']]:[['TTL','TTL'],['M','M'],['Multi','Multi']];
 $('flashMode').innerHTML=modes.map(([v,l])=>`<option value="${v}">${l}</option>`).join('');$('flashMode').value=s.screen==='sender'&&s.flash_mode!=='Multi'?'M':s.flash_mode;
 const menu=s.panel==='menu', receiver=s.screen==='receiver', rows=$('rows'),scroll=rows.scrollTop;
 document.querySelector('.screen').classList.toggle('receiverLayout',receiver&&!menu);
 $('receiverGroup').hidden=!receiver||menu;$('receiverGroupValue').textContent=s.rx_group;$('receiverGroup').setAttribute('aria-label','编辑接收组 '+s.rx_group);$('receiverGroup').classList.toggle('sel',s.focus==='GROUP');
 $('receiverModeOptions').hidden=true;document.querySelectorAll('[data-flash-mode]').forEach(b=>b.classList.toggle('active',b.dataset.flashMode===s.flash_mode));
 let rowEntries=s.entries.filter(e=>menu||!['ZOOM','ALL_ADJUST','GROUP'].includes(e.key));
 rows.classList.toggle('menuRows',menu);rows.classList.toggle('parameterRows',!menu&&(s.screen!=='sender'||s.flash_mode==='Multi'));rows.classList.toggle('singleRows',!menu&&s.screen!=='sender'&&s.flash_mode!=='Multi');
 rows.innerHTML=rowEntries.map(e=>`<button class="row ${e.key===s.focus?'sel':''} ${e.label==='OFF'?'off':''} ${e.key==='MAIN'?'mainRow':''}" data-name="${e.key}" aria-label="编辑 ${esc(e.title)}"><b>${esc(e.title)}</b><span class="mode">${esc(e.mode)}</span><span class="val">${esc(e.label)}</span>${e.key==='SUB'?'<span class="local">LOCAL</span>':''}</button>`).join('');
 rows.scrollTop=scroll;document.querySelectorAll('[data-name]').forEach(b=>{b.disabled=!s.active||s.editor||s.locked;b.onclick=()=>send('touch',b.dataset.name)});
 $('zoom').hidden=menu;$('all').hidden=menu;$('zoomValue').textContent=s.zoom.label;$('zoom').classList.toggle('sel',s.focus==='ZOOM');
 $('all').dataset.target=receiver?'':'ALL_ADJUST';$('secondTitle').textContent=receiver?'模式':'整体调整';
 $('allValue').textContent=receiver?s.flash_mode:s.all_adjust;
 $('all').hidden=menu||s.screen==='hotshoe'||(s.screen==='sender'&&s.flash_mode==='Multi');$('all').classList.toggle('sel',!receiver&&s.focus==='ALL_ADJUST');
 $('all').setAttribute('aria-label',receiver?'切换接收模式 '+s.flash_mode:'编辑整体调整');$('all').setAttribute('aria-expanded','false');
 $('away').hidden=s.active;$('editor').hidden=!s.editor;
 const entry=s.entries.find(e=>e.key===s.focus),group=s.screen==='sender'&&s.flash_mode!=='Multi'&&!menu?s.groups.find(g=>g.name===s.focus):null;
 const sub=!menu&&s.focus==='SUB',zoom=!menu&&s.focus==='ZOOM',all=!menu&&s.focus==='ALL_ADJUST',rxGroup=!menu&&s.focus==='GROUP';
 $('target').textContent=menu?entry.title:entry?.title||s.focus;$('editBadge').textContent=menu?'SETTING':s.flash_mode;
 $('value').textContent=sub?s.sub.label:entry?.label||'';
 $('modeTabs').hidden=!group;document.querySelectorAll('[data-mode]').forEach(b=>{b.classList.toggle('active',b.dataset.mode===group?.mode_label);b.disabled=s.locked});
 $('settingOptions').hidden=!menu||s.focus==='INFO';
 if(menu){$('settingOptions').innerHTML=entry.options.map((v,i)=>`<option value="${i}">${esc(v)}</option>`).join('');$('settingOptions').value=String(entry.index);}
 $('groupOptions').hidden=!rxGroup;$('groupOptions').innerHTML=rxGroup?'ABCDE'.split('').map(x=>`<button data-rxgroup="${x}" class="${s.rx_group===x?'active':''}">${x}</button>`).join(''):'';
 document.querySelectorAll('[data-rxgroup]').forEach(b=>b.onclick=()=>send('rx_group',b.dataset.rxgroup));
 $('toggle').hidden=!sub;$('toggle').textContent=s.sub.enabled?'●  SUB ON':'○  SUB OFF';$('toggle').classList.toggle('on',s.sub.enabled);$('toggle').disabled=s.locked;
 $('zoomAuto').hidden=!zoom;$('zoomAuto').textContent=s.zoom.auto?'AUTO · 自动焦距':'MANUAL · 手动焦距';$('zoomAuto').classList.toggle('on',s.zoom.auto);
 $('editHint').textContent=s.locked?'输入已锁定':menu?'选择设置值':sub?'1/128 — 1/1 · 1/3 档':zoom?'原厂焦距档位':rxGroup?'A — E':all?'同时调整原五个目标':s.focus==='TIMES'?'1 — 100 次':s.focus==='HZ'?'1 — 100 Hz':s.flash_mode==='Multi'?'1/256 — 1/4 · 整档':(group?.mode===0||s.flash_mode==='TTL')?'曝光补偿 / TTL':'原厂手动功率';
 $('editorNote').textContent=menu?'菜单为电脑适配；设置值写入模拟 RAM。':s.screen==='receiver'&&s.flash_mode==='TTL'?'Receiver TTL 由远端控制；此处不增加本地补偿。':sub?(!s.presence?'附件未连接，原厂阻止功率调节。':'电脑端不触发闪光。'):all?'保留共同边界，SUB 不参与整体调整。':'SET / Back 返回；旋转执行原厂参数函数。';
 $('presence').checked=s.presence;$('decimal').checked=!!s.decimal;$('sensor').checked=s.sensor;$('step').value=String(s.step);$('channel').value=String(s.channel);$('page').textContent=s.active?'离开当前页面':'返回当前页面';
 $('summary').innerHTML=s.entries.map(e=>`<tr class="${s.focus===e.key?'current':''}"><td>${esc(e.title)}</td><td><span class="pill">${esc(e.mode)}</span></td><td>${esc(e.label)}</td></tr>`).join('');
 $('focusLabel').textContent=s.active?`${s.screen_label} · ${s.editor?'编辑':'选择'}`:'页面未激活';$('steps').textContent=s.steps+' 步';$('undo').disabled=!s.undo;$('redo').disabled=!s.redo;
 for(const id of ['left','right','set','back','mode','zoom','all','plus','minus','close','zoomAuto','settingOptions','receiverGroup'])$(id).disabled=!s.active||s.locked;
 if(menu&&s.focus==='INFO'){$('plus').disabled=true;$('minus').disabled=true;}
 $('radio').disabled=!s.active||s.screen!=='sender';for(const id of ['serialize','channel'])$(id).disabled=!s.active;
 $('rxTools').hidden=s.screen!=='receiver';$('rxGroup').value=s.rx_group;
 $('rxResult').textContent=s.last_rx?`目标 ${String.fromCharCode(s.last_rx.destination+55)} · ${s.last_rx.command}=${s.last_rx.value} · ${s.last_rx.matched?'匹配组，原厂解析器已接收':'地址不匹配，原厂解析器忽略'}`:'仅执行原厂接收参数解析，不模拟空口传输或触发闪光。';
 const log=s.logs.at(-1),changed=log?.diff||{};renderMemory(changed);
 $('trace').innerHTML=s.logs.slice(-80).reverse().map(x=>`<div class="traceRow"><span>#${x.seq} ${esc(actionNames[x.action]||x.action)} ${esc(actionValue(x.value))}</span><code>${x.calls.length?x.calls.join('<br>'):'电脑端适配'}</code><code class="diff">${Object.keys(x.diff).length?Object.entries(x.diff).map(([k,v])=>`${esc(s.watch[k]||k)}　${v[0]} → ${v[1]}`).join('<br>'):'监视字段无变化'}</code></div>`).join('')||'<p class="notice">操作后显示函数调用和内存变化。</p>';
 $('packets').textContent=s.radio.length?s.radio.map(f=>{const b=f.match(/../g);return `${b.join(' ').toUpperCase()}${parseInt(b[1],16)>=10&&parseInt(b[1],16)<=13?'　→ Group '+String.fromCharCode(65+parseInt(b[1],16)-10):''}`}).join('\n'):'最近一次未捕获到参数变化包，或尚未捕获。首次捕获通常包含所有组同步。';
 $('record').hidden=!s.record;$('record').textContent=s.record?'设置记录 · 79 bytes\n'+s.record.match(/.{1,32}/g).join('\n'):'';
 $('sha').textContent='固件 SHA-256: '+s.sha256+'\n来源：V100F V1.03 原始副本。主镜像没有修改。';
 if(!s.editor&&s.active){const b=rows.querySelector(`[data-name="${s.focus}"]`);if(b){const y=b.offsetTop-rows.offsetTop;if(y<rows.scrollTop)rows.scrollTop=y;else if(y+b.offsetHeight>rows.scrollTop+rows.clientHeight)rows.scrollTop=y+b.offsetHeight-rows.clientHeight;}}
}
function renderMemory(changed=state?.logs.at(-1)?.diff||{}){if(!state)return;const q=$('filter').value.toLowerCase();$('memory').innerHTML=Object.entries(state.memory).filter(([k])=>(k+' '+state.watch[k]).toLowerCase().includes(q)).map(([k,v])=>`<div class="mem ${k in changed?'changed':''}"><b>${esc(state.watch[k])}</b>${k}　${v} / 0x${v.toString(16).padStart(2,'0')}</div>`).join('')}
for(const [id,a,v] of [['left','rotate',-1],['right','rotate',1],['minus','rotate',-1],['plus','rotate',1],['set','set'],['back','back'],['close','back'],['toggle','toggle'],['radio','radio'],['serialize','serialize'],['reset','reset'],['undo','undo'],['redo','redo']])$(id).onclick=()=>send(a,v);
$('mode').onclick=()=>{if(state.panel==='menu')return;const g=state.screen==='sender'&&state.flash_mode!=='Multi'?state.groups.find(g=>g.name===state.focus):null;if(g){if(!state.editor)send('set');send('mode',['TTL','M','OFF'][(g.mode+1)%3])}else send('flash_mode',['TTL','M','Multi'][(['TTL','M','Multi'].indexOf(state.flash_mode)+1)%3])};
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>send('mode',b.dataset.mode));
document.querySelectorAll('[data-target]').forEach(b=>b.onclick=()=>send('touch',b.dataset.target));
$('all').onclick=()=>{if(state.screen==='receiver'){$('receiverModeOptions').hidden=!$('receiverModeOptions').hidden;$('all').setAttribute('aria-expanded',String(!$('receiverModeOptions').hidden))}else send('touch','ALL_ADJUST')};
document.querySelectorAll('[data-flash-mode]').forEach(b=>b.onclick=()=>send('flash_mode',b.dataset.flashMode));
$('lock').onclick=()=>send('lock',!state.locked);$('zoomAuto').onclick=()=>send('zoom_auto',!state.zoom.auto);
for(const id of ['presence','decimal','sensor'])$(id).onchange=e=>send(id,e.target.checked);
$('step').onchange=e=>send('step',Number(e.target.value));$('channel').onchange=e=>send('channel',Number(e.target.value));$('page').onclick=()=>send('page',state.active?'away':'resume');$('returnSender').onclick=()=>send('page','resume');
$('menu').onclick=()=>send('menu');$('channelOpen').onclick=()=>{$('settings').scrollIntoView({behavior:'smooth',block:'center'});$('channel').focus({preventScroll:true})};
document.querySelectorAll('[data-role]').forEach(b=>b.onclick=()=>send('role',b.dataset.role));$('flashMode').onchange=e=>send('flash_mode',e.target.value);
$('settingOptions').onchange=e=>send('setting',{key:state.focus,index:Number(e.target.value)});
$('rxGroup').onchange=e=>send('rx_group',e.target.value);
function rxOptions(){const c=$('rxCommand').value;let options=c==='mode'?[[0,'TTL'],[1,'M'],[2,'Multi']]:c==='multi_power'?[20,30,40,50,60,70,80].map(x=>[x,'1/'+2**(x/10)]):c==='power'?Array.from({length:81},(_,i)=>[i,`编码 ${i}${i%10===0?' · 1/'+2**(i/10):''}`]):Array.from({length:100},(_,i)=>[i+1,(i+1)+(c==='hz'?' Hz':' 次')]);$('rxValue').innerHTML=options.map(([v,l])=>`<option value="${v}">${l}</option>`).join('');}
$('rxCommand').onchange=rxOptions;rxOptions();$('rxInject').onclick=()=>send('rx_inject',{command:$('rxCommand').value,value:Number($('rxValue').value),destination:Number($('rxDestination').value)});
$('save').onclick=()=>task(async()=>{render(await request('/api/save',{}));notify('已保存至 Godox/sessions/saved-session.json，可跨重启恢复。')});
$('load').onclick=()=>task(async()=>{render(await request('/api/load',{}));notify('已按操作序列恢复保存的会话。')});
$('export').onclick=()=>task(async()=>{const r=await fetch('/api/session');if(!r.ok)throw Error('导出失败');const data=await r.json();const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='V100F-debug-session-v3.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notify('已导出可回放操作、状态、调用记录和固件哈希。')});
$('import').onclick=()=>$('importFile').click();$('importFile').onchange=()=>task(async()=>{const file=$('importFile').files[0];if(!file)return;if(file.size>2000000)throw Error('记录文件超过 2 MB');const data=JSON.parse(await file.text()),session=data.session||data;if(![2,3].includes(session.schema)||session.firmware_sha256!==state.sha256||!Array.isArray(session.actions)||session.actions.length>1000)throw Error('会话版本、固件或操作列表不匹配');pendingReplay=session;replayPosition=0;$('replay').hidden=false;updateReplay();notify('回放已载入。执行第一步时恢复初始测试场景。');$('importFile').value=''});
function updateReplay(){$('replayLabel').textContent=`回放 ${replayPosition} / ${pendingReplay.actions.length}`;$('replayStep').disabled=replayPosition>=pendingReplay.actions.length}
$('replayStep').onclick=()=>task(async()=>{const n=Math.min(replayPosition+1,pendingReplay.actions.length);const s=await request('/api/restore',{...pendingReplay,actions:pendingReplay.actions.slice(0,n)});render(s);replayPosition=n;updateReplay();notify('已重建会话并执行到第 '+n+' 步。')});
$('replayAll').onclick=()=>task(async()=>{render(await request('/api/restore',pendingReplay));replayPosition=pendingReplay.actions.length;updateReplay();notify('全部回放完成。')});$('replayStop').onclick=()=>{pendingReplay=null;$('replay').hidden=true;notify('已结束回放，当前状态保留。')};
$('filter').oninput=()=>renderMemory();document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{for(const name of ['trace','memory','coverage'])$(name+'Panel').hidden=name!==b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b))});
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName)||!state)return;if(e.key==='Escape'&&!$('receiverModeOptions').hidden){e.preventDefault();$('receiverModeOptions').hidden=true;$('all').setAttribute('aria-expanded','false');return}const map={ArrowLeft:['rotate',-1],ArrowUp:['rotate',-1],ArrowRight:['rotate',1],ArrowDown:['rotate',1],Enter:['set'],Escape:['back']};if(map[e.key]){e.preventDefault();if(!e.repeat&&state.active&&!state.locked)send(...map[e.key])}});
let lastWheel=0;$('dial').addEventListener('wheel',e=>{e.preventDefault();if(state&&!state.locked&&Date.now()-lastWheel>90){lastWheel=Date.now();send('rotate',e.deltaY>0?1:-1)}},{passive:false});
fetch('/api/state').then(r=>r.json()).then(s=>{render(s);$('connection').textContent='已连接 · 原厂参数引擎'}).catch(e=>{$('connection').textContent='未连接';$('error').textContent='服务不可用：'+e.message});
