"use strict";

const canvas = document.getElementById("scene");
const ctx = canvas.getContext("2d");
const $ = (id) => document.getElementById(id);

const PICK = [189.19, 499.91, 252.13, -18.49, 176.03, 87.36];
const DROP_BASE = [58.41, 352.35, 306.07, 0.03, -179.46, 0.08];
const palletOffsets = [[0, 0], [80, 0], [80, -80], [0, -80]];
const dropTargets = [0, 30].flatMap((z, layer) => palletOffsets.map(([x, y], cell) => ({
  pose: [DROP_BASE[0] + x, DROP_BASE[1] + y, DROP_BASE[2] + z, ...DROP_BASE.slice(3)],
  layer, cell,
})));

const state = {
  running: false, stepOnce: false, sequenceIndex: 0, phaseTime: 0, speed: 35,
  gripperClosed: false, carrying: false, completed: 0,
  pose: [0, 360, 520, 0, 180, 0], fromPose: null,
  joints: [0, -30, 75, 0, 45, 0],
  camera: { yaw: -0.72, pitch: 0.38, zoom: 1.05 },
};

function rad(v){ return v * Math.PI / 180; }
function rotMatrix([rx, ry, rz]) {
  const [x,y,z]=[rad(rx),rad(ry),rad(rz)], cx=Math.cos(x),sx=Math.sin(x),cy=Math.cos(y),sy=Math.sin(y),cz=Math.cos(z),sz=Math.sin(z);
  return [[cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx],[sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx],[-sy,cy*sx,cy*cx]];
}
function toolOffset(pose, mm) {
  const r=rotMatrix(pose.slice(3)), p=[...pose];
  for(let i=0;i<3;i++) p[i]+=r[i][2]*mm;
  return p;
}
const pickApproach=toolOffset(PICK,-100);
const phases=[];
dropTargets.forEach((drop,i)=>{
  const da=toolOffset(drop.pose,-100), tag=`${i+1}/8`;
  phases.push(
    {name:"Pick 접근",detail:tag,target:pickApproach,duration:1.15},
    {name:"Pick 타겟",detail:tag,target:PICK,duration:.55},
    {name:"그리퍼 닫기",detail:"DO.0 OFF · DO.1 ON",action:"close",duration:.38},
    {name:"Pick 회수",detail:tag,target:pickApproach,duration:.6},
    {name:"Drop 접근",detail:`${drop.layer+1}단 · ${drop.cell+1}번`,target:da,duration:1.15},
    {name:"Drop 타겟",detail:`${drop.layer+1}단 · ${drop.cell+1}번`,target:drop.pose,duration:.55},
    {name:"그리퍼 열기",detail:"DO.0 ON · DO.1 OFF",action:"open",duration:.38},
    {name:"Drop 회수",detail:tag,target:da,duration:.6,complete:true}
  );
});

const jointList=$("jointList");
for(let i=0;i<6;i++){
  const row=document.createElement("div"); row.className="joint";
  row.innerHTML=`<label>J${i+1}</label><input type="range" min="-180" max="180" value="${state.joints[i]}" disabled><output>${state.joints[i].toFixed(1)}°</output>`;
  jointList.appendChild(row);
}
const jointInputs=[...jointList.querySelectorAll("input")], jointOutputs=[...jointList.querySelectorAll("output")];

function phase(){ return phases[Math.min(state.sequenceIndex,phases.length-1)]; }
function startPhase(){
  const p=phase(); state.phaseTime=0; state.fromPose=[...state.pose];
  if(p.action==="close"){state.gripperClosed=true;state.carrying=true;}
  if(p.action==="open"){state.gripperClosed=false;state.carrying=false;}
}
function advance(){
  const p=phase(); if(p.target) state.pose=[...p.target];
  if(p.complete) state.completed++;
  state.sequenceIndex++;
  if(state.sequenceIndex>=phases.length){state.running=false;state.stepOnce=false;state.sequenceIndex=phases.length-1;}
  else startPhase();
}
function reset(){
  Object.assign(state,{running:false,stepOnce:false,sequenceIndex:0,phaseTime:0,gripperClosed:false,carrying:false,completed:0,pose:[0,360,520,0,180,0]});
  startPhase(); updateUI();
}

function lerp(a,b,t){return a+(b-a)*t;}
function ease(t){return t*t*(3-2*t);}
function update(dt){
  if(!state.running&&!state.stepOnce) return;
  const p=phase(), rate=.35+state.speed/40;
  state.phaseTime+=dt*rate;
  const t=Math.min(1,state.phaseTime/p.duration);
  if(p.target) state.pose=p.target.map((v,i)=>lerp(state.fromPose[i],v,ease(t)));
  if(t>=1){advance();if(state.stepOnce){state.stepOnce=false;state.running=false;}}
  solveIK(); updateUI();
}

function solveIK(){
  const [x,y,z]=state.pose.map(v=>v/1000), yaw=Math.atan2(y,x), r=Math.max(.05,Math.hypot(x,y)-.07), dz=z-.22, l1=.34,l2=.34;
  const c=Math.max(-1,Math.min(1,(r*r+dz*dz-l1*l1-l2*l2)/(2*l1*l2))), elbow=Math.acos(c);
  const shoulder=Math.atan2(dz,r)-Math.atan2(l2*Math.sin(elbow),l1+l2*Math.cos(elbow));
  state.joints=[yaw*180/Math.PI,shoulder*180/Math.PI,elbow*180/Math.PI-90,state.pose[3],-shoulder*180/Math.PI-elbow*180/Math.PI,state.pose[5]];
}

function updateUI(){
  const p=phase(), progress=Math.round(state.completed/8*100);
  $("progressValue").textContent=`${progress}%`; $("progressBar").style.width=`${progress}%`; $("cycleCount").textContent=`${state.completed} / 8 CYCLES`;
  $("phaseIndex").textContent=String((state.sequenceIndex%8)+1).padStart(2,"0"); $("phaseName").textContent=p?.name||"완료"; $("phaseDetail").textContent=p?.detail||"팔레타이징 완료";
  ["tcpX","tcpY","tcpZ"].forEach((id,i)=>$(id).textContent=state.pose[i].toFixed(2));
  $("gripperIcon").classList.toggle("closed",state.gripperClosed); $("gripperText").textContent=state.gripperClosed?"CLOSE":"OPEN";
  $("gripperText").nextElementSibling.textContent=state.gripperClosed?"DO.0 OFF · DO.1 ON":"DO.0 ON · DO.1 OFF";
  jointInputs.forEach((el,i)=>{el.value=state.joints[i];jointOutputs[i].textContent=`${state.joints[i].toFixed(1)}°`;});
  $("runBtn").classList.toggle("running",state.running); $("runBtn").innerHTML=state.running?"Ⅱ PAUSE":"<span>▶</span> RUN";
}

function resize(){const d=devicePixelRatio||1,r=canvas.getBoundingClientRect();canvas.width=r.width*d;canvas.height=r.height*d;ctx.setTransform(d,0,0,d,0,0);}
function rotatePoint(p){
  let [x,y,z]=p, c=Math.cos(state.camera.yaw),s=Math.sin(state.camera.yaw); [x,y]=[x*c-y*s,x*s+y*c];
  c=Math.cos(state.camera.pitch);s=Math.sin(state.camera.pitch); [y,z]=[y*c-z*s,y*s+z*c]; return [x,y,z];
}
function project(p){const r=canvas.getBoundingClientRect(),q=rotatePoint(p),scale=Math.min(r.width,r.height)*.7*state.camera.zoom;return [r.width*.51+q[0]*scale,r.height*.68-q[2]*scale,q[1]];}
function line3(a,b,color,width=1){const A=project(a),B=project(b);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(A[0],A[1]);ctx.lineTo(B[0],B[1]);ctx.stroke();}
function dot3(p,r,color,stroke){const q=project(p);ctx.beginPath();ctx.arc(q[0],q[1],r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.stroke();}}
function polygon(points,fill,stroke="#294043"){ctx.beginPath();points.map(project).forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle=stroke;ctx.stroke();}
function box3(center,size,color){const [x,y,z]=center,[sx,sy,sz]=size,v=[[x-sx/2,y-sy/2,z],[x+sx/2,y-sy/2,z],[x+sx/2,y+sy/2,z],[x-sx/2,y+sy/2,z],[x-sx/2,y-sy/2,z+sz],[x+sx/2,y-sy/2,z+sz],[x+sx/2,y+sy/2,z+sz],[x-sx/2,y+sy/2,z+sz]];polygon([v[0],v[1],v[5],v[4]],color);polygon([v[1],v[2],v[6],v[5]],color);polygon([v[4],v[5],v[6],v[7]],color.replace(".55",".75"));}

function robotPoints(){
  const j=state.joints.map(rad), yaw=j[0], sh=j[1], el=j[2]+Math.PI/2, base=[0,0,.08], shoulder=[0,0,.24];
  const dir=(len,a)=>[Math.cos(yaw)*Math.cos(a)*len,Math.sin(yaw)*Math.cos(a)*len,Math.sin(a)*len];
  const d1=dir(.34,sh), elbow=shoulder.map((v,i)=>v+d1[i]),d2=dir(.34,sh+el),wrist=elbow.map((v,i)=>v+d2[i]),tcp=state.pose.slice(0,3).map(v=>v/1000);
  return [base,shoulder,elbow,wrist,tcp];
}
function draw(){
  const r=canvas.getBoundingClientRect();ctx.clearRect(0,0,r.width,r.height);
  const grd=ctx.createRadialGradient(r.width*.52,r.height*.45,10,r.width*.52,r.height*.45,r.width*.65);grd.addColorStop(0,"#13292b");grd.addColorStop(1,"#071012");ctx.fillStyle=grd;ctx.fillRect(0,0,r.width,r.height);
  for(let i=-8;i<=8;i++){line3([i*.1,-.8,0],[i*.1,.8,0],i===0?"#275255":"#183033",i===0?1.5:1);line3([-.8,i*.1,0],[.8,i*.1,0],i===0?"#275255":"#183033",i===0?1.5:1);}
  box3([.098,.312,.015],[.28,.28,.03],"rgba(69,240,191,.13)");
  dropTargets.forEach((d,i)=>{const p=d.pose.map(v=>v/1000);if(i<state.completed)box3([p[0],p[1],p[2]-.015],[.065,.065,.03],"rgba(255,134,92,.55)");else{dot3([p[0],p[1],p[2]],3,"#203b3d","#45f0bf");}});
  const pp=PICK.map(v=>v/1000);box3([pp[0],pp[1],.015],[.12,.12,.03],"rgba(64,190,209,.18)");if(!state.carrying)box3([pp[0],pp[1],pp[2]-.015],[.065,.065,.03],"rgba(255,134,92,.55)");
  const pts=robotPoints();box3([0,0,.04],[.22,.22,.08],"rgba(216,229,227,.55)");
  for(let i=0;i<pts.length-1;i++)line3(pts[i],pts[i+1],i===3?"#9db4b1":"#d5dfdd",i===3?9:18);
  pts.forEach((p,i)=>dot3(p,i===4?7:12,i===4?"#45f0bf":"#172326","#d7e2df"));
  const tcp=pts[4];line3(tcp,[tcp[0],tcp[1],tcp[2]+.07],"#40bed1",2);if(state.carrying)box3([tcp[0],tcp[1],tcp[2]-.035],[.065,.065,.03],"rgba(255,134,92,.8)");
  const target=phase()?.target;if(target){const a=target.map(v=>v/1000);dot3(a,5,"#ff865c","#fff");}
}

$("runBtn").onclick=()=>{state.running=!state.running;state.stepOnce=false;if(state.sequenceIndex>=phases.length-1)reset();updateUI();};
$("stepBtn").onclick=()=>{state.stepOnce=true;state.running=false;}; $("resetBtn").onclick=reset;
$("speed").oninput=e=>{state.speed=+e.target.value;$("speedValue").textContent=`${state.speed}%`;};
let dragging=false,last=[0,0];canvas.onpointerdown=e=>{dragging=true;last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};canvas.onpointerup=()=>dragging=false;canvas.onpointermove=e=>{if(!dragging)return;state.camera.yaw+=(e.clientX-last[0])*.007;state.camera.pitch=Math.max(-.2,Math.min(1.15,state.camera.pitch+(e.clientY-last[1])*.006));last=[e.clientX,e.clientY]};canvas.onwheel=e=>{e.preventDefault();state.camera.zoom=Math.max(.55,Math.min(2,state.camera.zoom*(e.deltaY>0?.92:1.08)))},{passive:false};
setInterval(()=>$("clock").textContent=new Date().toLocaleTimeString("ko-KR",{hour12:false}),1000);
let previous=performance.now();function frame(now){const dt=Math.min(.05,(now-previous)/1000);previous=now;update(dt);draw();requestAnimationFrame(frame)}
addEventListener("resize",resize);resize();reset();requestAnimationFrame(frame);
