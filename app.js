/* My Experiments with Logic Gates — lab engine (vanilla JS, no build chain) */
(function(){
'use strict';

/* ============================================================
   1. Expression parser + multi-logic evaluator
   ============================================================ */
var VARS=['A','B','C'];
var OPWORDS=new Set(['AND','OR','NOT','NAND','NOR','XOR','XNOR','IMP']);
var SYM={'&':'AND','∧':'AND','·':'AND','.':'AND','|':'OR','∨':'OR','+':'OR',
         '^':'XOR','⊕':'XOR','!':'NOT','~':'NOT','¬':'NOT','→':'IMP'};

function tokenize(s){
  var toks=[],i=0;
  while(i<s.length){
    var c=s[i];
    if(/\s/.test(c)){i++;continue;}
    if(/[A-Za-z]/.test(c)){
      var j=i; while(j<s.length && /[A-Za-z0-9]/.test(s[j])) j++;
      toks.push({t:'word',v:s.slice(i,j).toUpperCase()}); i=j; continue;
    }
    if(c==='('||c===')'){ toks.push({t:c}); i++; continue; }
    if(c===','){ toks.push({t:','}); i++; continue; }
    if(s.substr(i,2)==='->'){ toks.push({t:'op',v:'IMP'}); i+=2; continue; }
    if(SYM[c]){ toks.push({t:'op',v:SYM[c]}); i++; continue; }
    throw new Error('unexpected character “'+c+'”');
  }
  return toks;
}

function binOpAt(tokens,i){
  var t=tokens[i]; if(!t) return null;
  if(t.t==='op') return t.v;
  if(t.t==='word' && OPWORDS.has(t.v)){
    var nx=tokens[i+1];
    if(nx && nx.t==='(') return null;   // it's a function call, not an operator
    return t.v;
  }
  return null;
}

function parse(s){
  var tokens=tokenize(s), pos=0;
  function peek(){return tokens[pos];}
  function nextTok(){return tokens[pos++];}
  function parseImp(){
    var left=parseOr();
    while(binOpAt(tokens,pos)==='IMP'){ pos++; left={k:'imp',l:left,r:parseOr()}; }
    return left;
  }
  function parseOr(){
    var left=parseXor(), op;
    while((op=binOpAt(tokens,pos))==='OR'||op==='NOR'){ pos++; left={k:(op==='NOR'?'nor':'or'),l:left,r:parseXor()}; }
    return left;
  }
  function parseXor(){
    var left=parseAnd(), op;
    while((op=binOpAt(tokens,pos))==='XOR'||op==='XNOR'){ pos++; left={k:(op==='XNOR'?'xnor':'xor'),l:left,r:parseAnd()}; }
    return left;
  }
  function parseAnd(){
    var left=parseUnary(), op;
    while((op=binOpAt(tokens,pos))==='AND'||op==='NAND'){ pos++; left={k:(op==='NAND'?'nand':'and'),l:left,r:parseUnary()}; }
    return left;
  }
  function parseUnary(){
    var t=peek();
    if(t && ((t.t==='op'&&t.v==='NOT') || (t.t==='word'&&t.v==='NOT'))){ pos++; return {k:'not',x:parseUnary()}; }
    return parsePrimary();
  }
  function parsePrimary(){
    var t=nextTok();
    if(!t) throw new Error('the sentence ends early');
    if(t.t==='('){ var e=parseImp(); var q=nextTok(); if(!q||q.t!==')') throw new Error('missing “)”'); return e; }
    if(t.t==='word'){
      var w=t.v;
      if(w==='0') return {k:'const',v:0};
      if(w==='1') return {k:'const',v:1};
      if(VARS.indexOf(w)>=0) return {k:'var',v:w};
      if(OPWORDS.has(w)||w==='MAJ'){
        if(peek() && peek().t==='('){
          pos++; var args=[parseImp()];
          while(peek() && peek().t===','){ pos++; args.push(parseImp()); }
          var q2=nextTok(); if(!q2||q2.t!==')') throw new Error('missing “)” after '+w);
          return {k:'fn',name:w,args:args};
        }
        throw new Error('“'+w+'” is missing an operand');
      }
      throw new Error('unknown symbol “'+w+'”');
    }
    if(t.t==='op') throw new Error('“'+t.v+'” is missing an operand');
    throw new Error('unexpected input');
  }
  var ast=parseImp();
  if(pos<tokens.length) throw new Error('unexpected extra input after the sentence');
  return ast;
}

function usedVars(ast,acc){
  acc=acc||{};
  if(!ast) return acc;
  if(ast.k==='var') acc[ast.v]=true;
  if(ast.l) usedVars(ast.l,acc);
  if(ast.r) usedVars(ast.r,acc);
  if(ast.x) usedVars(ast.x,acc);
  if(ast.args) ast.args.forEach(function(a){usedVars(a,acc);});
  return acc;
}

var LOGICS={
  classical:{label:'Classical',vals:[0,1],fmt:function(v){return String(v);},
    not_:function(x){return 1-x;},and_:function(a,b){return Math.min(a,b);},or_:function(a,b){return Math.max(a,b);},
    imp_:function(a,b){return Math.max(1-a,b);},top:1},
  k3:{label:'Kleene K₃ (unknown)',vals:[0,0.5,1],fmt:function(v){return v===0.5?'U':String(v);},
    not_:function(x){return 1-x;},and_:function(a,b){return Math.min(a,b);},or_:function(a,b){return Math.max(a,b);},
    imp_:function(a,b){return Math.max(1-a,b);},top:1},
  l3:{label:'Łukasiewicz Ł₃ (not-yet)',vals:[0,0.5,1],fmt:function(v){return v===0.5?'U':String(v);},
    not_:function(x){return 1-x;},and_:function(a,b){return Math.min(a,b);},or_:function(a,b){return Math.max(a,b);},
    imp_:function(a,b){return Math.min(1,1-a+b);},top:1},
  fuzzy:{label:'Fuzzy (graded)',vals:[0,0.25,0.5,0.75,1],fmt:function(v){return v.toFixed(2);},
    not_:function(x){return 1-x;},and_:function(a,b){return Math.min(a,b);},or_:function(a,b){return Math.max(a,b);},
    imp_:function(a,b){return Math.min(1,1-a+b);},top:1},
  sql:{label:'SQL (NULL)',vals:[0,1,null],fmt:function(v){return v===null?'NULL':(v?'TRUE':'FALSE');},
    not_:function(x){return x===null?null:1-x;},
    and_:function(a,b){return (a===0||b===0)?0:((a===null||b===null)?null:1);},
    or_:function(a,b){return (a===1||b===1)?1:((a===null||b===null)?null:0);},
    imp_:function(a,b){return (a===0||b===1)?1:((a===null||b===null)?null:0);},top:1}
};

function ev(n,env,L){
  switch(n.k){
    case 'const': return n.v;
    case 'var': return env[n.v];
    case 'not': return L.not_(ev(n.x,env,L));
    case 'and': return L.and_(ev(n.l,env,L),ev(n.r,env,L));
    case 'or':  return L.or_(ev(n.l,env,L),ev(n.r,env,L));
    case 'nand':return L.not_(L.and_(ev(n.l,env,L),ev(n.r,env,L)));
    case 'nor': return L.not_(L.or_(ev(n.l,env,L),ev(n.r,env,L)));
    case 'xor': return xor(ev(n.l,env,L),ev(n.r,env,L),L);
    case 'xnor':return L.not_(xor(ev(n.l,env,L),ev(n.r,env,L),L));
    case 'imp': return L.imp_(ev(n.l,env,L),ev(n.r,env,L));
    case 'fn': return callFn(n,env,L);
  }
  throw new Error('bad node');
}
function xor(a,b,L){ return L.or_(L.and_(a,L.not_(b)),L.and_(L.not_(a),b)); }
function callFn(n,env,L){
  var a=n.args.map(function(x){return ev(x,env,L);});
  switch(n.name){
    case 'NOT': return L.not_(a[0]);
    case 'AND': return a.reduce(function(p,c){return L.and_(p,c);});
    case 'OR':  return a.reduce(function(p,c){return L.or_(p,c);});
    case 'NAND':return L.not_(a.reduce(function(p,c){return L.and_(p,c);}));
    case 'NOR': return L.not_(a.reduce(function(p,c){return L.or_(p,c);}));
    case 'XOR': return a.reduce(function(p,c){return xor(p,c,L);});
    case 'XNOR':return L.not_(a.reduce(function(p,c){return xor(p,c,L);}));
    case 'IMP': return L.imp_(a[0],a[1]);
    case 'MAJ': return L.or_(L.or_(L.and_(a[0],a[1]),L.and_(a[1],a[2])),L.and_(a[0],a[2]));
  }
  throw new Error('unknown function '+n.name);
}

/* enumerate the input combinations over a set of variables */
function combos(vars,vals){
  var out=[{}];
  vars.forEach(function(v){
    var nxt=[];
    out.forEach(function(env){ vals.forEach(function(val){ var e=Object.assign({},env); e[v]=val; nxt.push(e); }); });
    out=nxt;
  });
  return out;
}

function valClass(v){
  if(v===null) return 'u';
  if(v===1||v===true) return '1';
  if(v===0||v===false) return '0';
  if(v===0.5) return 'u';
  return 'n';
}
function colorOf(v){
  var c=valClass(v);
  return c==='1'?'#5eead4':c==='0'?'#fb7185':c==='u'?'#fbbf24':'#a78bfa';
}

/* ============================================================
   2. GATE LAB
   ============================================================ */
var NAMED={
  AND:{e:'A & B',t:'and',sym:'A·B'},
  OR:{e:'A | B',t:'or',sym:'A+B'},
  NOT:{e:'!A',t:'not',sym:'¬A'},
  NAND:{e:'NAND(A,B)',t:'nand',sym:'A↑B'},
  NOR:{e:'NOR(A,B)',t:'nor',sym:'A↓B'},
  XOR:{e:'A ^ B',t:'xor',sym:'A⊕B'},
  XNOR:{e:'XNOR(A,B)',t:'xnor',sym:'A⊙B'}
};
var state={gate:'AND',expr:'A & B',a:0,b:0};

function initGates(){
  var chips=document.getElementById('gateChips');
  Object.keys(NAMED).forEach(function(k){
    var b=document.createElement('button');
    b.className='chip'+(k==='AND'?' on':''); b.textContent=k+'  '+NAMED[k].sym;
    b.onclick=function(){
      state.gate=k; state.expr=NAMED[k].e;
      [].forEach.call(chips.children,function(c){c.classList.remove('on');});
      b.classList.add('on');
      document.getElementById('exprInput').value=NAMED[k].e;
      document.getElementById('exprErr').textContent='';
      renderGates();
    };
    chips.appendChild(b);
  });
  var swA=document.getElementById('swA'), swB=document.getElementById('swB');
  swA.onclick=function(){ state.a=state.a?0:1; renderGates(); };
  swB.onclick=function(){ state.b=state.b?0:1; renderGates(); };
  document.getElementById('exprGo').onclick=function(){
    var v=document.getElementById('exprInput').value;
    try{ parse(v); state.expr=v; state.gate='CUSTOM'; document.getElementById('exprErr').textContent='';
      [].forEach.call(chips.children,function(c){c.classList.remove('on');}); renderGates(); }
    catch(err){ document.getElementById('exprErr').textContent='⚠ '+err.message; }
  };
  document.getElementById('exprInput').addEventListener('keydown',function(e){ if(e.key==='Enter') document.getElementById('exprGo').click(); });
  renderGates();
}

function renderGates(){
  var swA=document.getElementById('swA'), swB=document.getElementById('swB');
  swA.classList.toggle('on',state.a===1); swB.classList.toggle('on',state.b===1);
  document.getElementById('valA').textContent=state.a;
  document.getElementById('valB').textContent=state.b;
  document.getElementById('exprEcho').textContent=state.expr;
  var ast,L=LOGICS.classical,out;
  try{ ast=parse(state.expr); out=ev(ast,{A:state.a,B:state.b,C:0},L); }
  catch(e){ out=null; }
  var ob=document.getElementById('gateOut');
  if(out===null){ ob.textContent='—'; ob.className='badge u'; }
  else { ob.textContent=out; ob.className='badge '+(out?'t':'f'); }

  document.getElementById('gateSvg').innerHTML=drawGate(state.gate,state.a,state.b,out);
  renderTT('ttClassic',ast,L,{A:state.a,B:state.b},false);
}

function renderTT(id,ast,L,hot,forceAB){
  var tbl=document.getElementById(id);
  if(!ast){ tbl.innerHTML='<tr><td>—</td></tr>'; return; }
  var uv=Object.keys(usedVars(ast)).sort();
  if(forceAB){ uv=['A','B']; }
  var rows=combos(uv,L.vals);
  var html='<tr>'+uv.map(function(v){return '<th>'+v+'</th>';}).join('')+'<th>out</th></tr>';
  rows.forEach(function(env){
    var o=ev(ast,env,L);
    var isHot=hot && uv.every(function(v){return env[v]===hot[v];});
    html+='<tr'+(isHot?' class="hot"':'')+'>';
    uv.forEach(function(v){ html+='<td>'+L.fmt(env[v])+'</td>'; });
    html+='<td class="out'+valClass(o)+'">'+L.fmt(o)+'</td></tr>';
  });
  tbl.innerHTML=html;
}

/* --- gate symbol drawing --- */
function drawGate(type,a,b,out){
  var two=(type!=='not'&&type!=='NOT');
  var col=function(v){return colorOf(v);};
  var svg='<svg viewBox="0 0 330 170" width="100%">';
  svg+='<defs><linearGradient id="gb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b2544"/><stop offset="1" stop-color="#111a33"/></linearGradient></defs>';
  var yA=two?58:85, yB=112, yO=85;
  // input wires
  svg+='<line x1="45" y1="'+yA+'" x2="150" y2="'+yA+'" stroke="'+col(a)+'" stroke-width="3"/>';
  svg+='<text x="20" y="'+(yA+5)+'" fill="#94a0bd" font-family="monospace" font-size="15">A</text>';
  svg+='<text x="120" y="'+(yA-10)+'" fill="'+col(a)+'" font-family="monospace" font-size="14">'+a+'</text>';
  if(two){
    svg+='<line x1="45" y1="'+yB+'" x2="150" y2="'+yB+'" stroke="'+col(b)+'" stroke-width="3"/>';
    svg+='<text x="20" y="'+(yB+5)+'" fill="#94a0bd" font-family="monospace" font-size="15">B</text>';
    svg+='<text x="120" y="'+(yB-10)+'" fill="'+col(b)+'" font-family="monospace" font-size="14">'+b+'</text>';
  }
  // body
  var body='';
  var bubble=false;
  if(type==='and'||type==='nand'){ body='<path d="M150,'+(two?40:68)+' H190 A42,42 0 0 1 190,152 H150 Z"/>'; bubble=(type==='nand'); }
  else if(type==='or'||type==='nor'||type==='xor'||type==='xnor'){
    body='<path d="M150,'+(two?40:68)+' Q172,95 150,152 Q195,152 232,95 Q195,'+(two?40:68)+' 150,'+(two?40:68)+' Z"/>';
    if(type==='xor'||type==='xnor'){ body+='<path d="M140,'+(two?40:68)+' Q162,95 140,152" fill="none" stroke="#7c88a8" stroke-width="3"/>'; }
    bubble=(type==='nor'||type==='xnor');
  }
  else if(type==='not'){ body='<path d="M160,60 L160,130 L226,95 Z"/>'; bubble=true; }
  else { // custom — draw a rounded box
    body='<rect x="150" y="45" width="86" height="100" rx="16"/>';
  }
  svg+='<g fill="url(#gb)" stroke="#5eead4" stroke-width="2.5">'+body+'</g>';
  if(bubble) svg+='<circle cx="'+(type==='not'?234:242)+'" cy="95" r="7" fill="#0f1730" stroke="#5eead4" stroke-width="2.5"/>';
  // output wire
  var xout=(bubble?(type==='not'?241:249):234);
  svg+='<line x1="'+xout+'" y1="'+yO+'" x2="305" y2="'+yO+'" stroke="'+col(out)+'" stroke-width="3"/>';
  if(out!==null){
    svg+='<circle cx="305" cy="'+yO+'" r="8" fill="'+col(out)+'"/>';
    svg+='<text x="292" y="'+(yO-14)+'" fill="'+col(out)+'" font-family="monospace" font-size="14">'+out+'</text>';
  }
  svg+='</g></svg>';
  return svg;
}

/* ============================================================
   3. UNIVERSALITY
   ============================================================ */
function synthesize(prim){
  // closure of {x,y} under a single binary primitive; returns set of 4-bit tables
  var T=function(f){ return [f(0,0),f(0,1),f(1,0),f(1,1)].join(''); };
  var fromT=function(t){ return function(x,y){ return t[x*2+y]-'0'; }; };
  var built={};
  built[T(function(x,y){return x;})]='x';
  built[T(function(x,y){return y;})]='y';
  var changed=true, guard=0;
  while(changed && Object.keys(built).length<16 && guard++<50){
    changed=false;
    var keys=Object.keys(built);
    for(var i=0;i<keys.length;i++) for(var j=0;j<keys.length;j++){
      var f1=fromT(keys[i]), f2=fromT(keys[j]);
      var nt=T(function(x,y){ return prim(f1(x,y),f2(x,y)); });
      if(!built[nt]){ built[nt]='('+built[keys[i]]+' '+prim.label+' '+built[keys[j]]+')'; changed=true; }
    }
  }
  return built;
}
var primNand=function(x,y){return 1-Math.min(x,y);}; primNand.label='↑';
var primNor =function(x,y){return 1-Math.max(x,y);}; primNor.label='↓';

function initUniversal(){
  var box=document.getElementById('univCards');
  var base='nand';
  function render(){
    var prim=base==='nand'?primNand:primNor;
    var sym=base==='nand'?'↑':'↓';
    var notE=base==='nand'?'x ↑ x':'(x ↓ x)';
    var andE=base==='nand'?'(x ↑ y) ↑ (x ↑ y)':'(x ↓ x) ↓ (y ↓ y)';
    var orE =base==='nand'?'(x ↑ x) ↑ (y ↑ y)':'(x ↓ y) ↓ (x ↓ y)';
    box.innerHTML=
      card('NOT from '+base.toUpperCase(),'¬x = '+notE, base, 'not')+
      card('AND from '+base.toUpperCase(),'x ∧ y = '+andE, base, 'and')+
      card('OR from '+base.toUpperCase(),'x ∨ y = '+orE, base, 'or');
  }
  function card(title,formula,b,t){
    // compute the table live using the actual primitive
    var prim=b==='nand'?primNand:primNor;
    var f;
    if(t==='not') f=function(x,y){return prim(x,x);};
    if(t==='and') f=function(x,y){return prim(prim(x,y),prim(x,y));};
    if(t==='or')  f=function(x,y){return prim(prim(x,x),prim(y,y));};
    var rows='';
    [[0,0],[0,1],[1,0],[1,1]].forEach(function(p){
      var o=f(p[0],p[1]);
      rows+='<tr><td>'+p[0]+'</td><td>'+p[1]+'</td><td class="out'+o+'">'+o+'</td></tr>';
    });
    return '<div class="card"><h3>'+title+'</h3><p class="mono" style="color:var(--teal)">'+formula+'</p>'+
      '<table class="tt"><tr><th>x</th><th>y</th><th>out</th></tr>'+rows+'</table></div>';
  }
  [].forEach.call(document.querySelectorAll('[data-base]'),function(btn){
    btn.onclick=function(){ base=btn.dataset.base;
      [].forEach.call(document.querySelectorAll('[data-base]'),function(b2){b2.classList.remove('on');});
      btn.classList.add('on'); render(); };
  });
  document.getElementById('synthBtn').onclick=function(){
    var n=synthesize(primNand), r=synthesize(primNor);
    document.getElementById('synthOut').textContent='NAND → '+Object.keys(n).length+'/16 · NOR → '+Object.keys(r).length+'/16';
  };
  render();
}

/* ============================================================
   4. MANY LOGICS + LAW MATRIX
   ============================================================ */
var ML_ORDER=['classical','k3','l3','fuzzy','sql'];
function initManyLogics(){
  var input=document.getElementById('mlExpr');
  function render(){
    var box=document.getElementById('mlTables');
    var ast;
    try{ ast=parse(input.value); }catch(e){ box.innerHTML='<div class="card">⚠ '+e.message+'</div>'; return; }
    var html='';
    ML_ORDER.forEach(function(k){
      var L=LOGICS[k];
      var uv=Object.keys(usedVars(ast)).sort();
      var rows=combos(uv,L.vals);
      var t='<div class="card"><h3>'+L.label+'</h3><table class="tt"><tr>'+uv.map(function(v){return '<th>'+v+'</th>';}).join('')+'<th>out</th></tr>';
      rows.forEach(function(env){
        var o=ev(ast,env,L);
        t+='<tr>'+uv.map(function(v){return '<td>'+L.fmt(env[v])+'</td>';}).join('')+'<td class="out'+valClass(o)+'">'+L.fmt(o)+'</td></tr>';
      });
      t+='</table></div>'; html+=t;
    });
    box.innerHTML=html;
  }
  [].forEach.call(document.querySelectorAll('[data-sent]'),function(b){
    b.onclick=function(){ input.value=b.dataset.sent; render(); };
  });
  input.addEventListener('input',render);
  render();
  renderLawMatrix();
}

function tautology(ast,L){
  var uv=Object.keys(usedVars(ast)).sort();
  var rows=combos(uv,L.vals);
  return rows.every(function(env){ return ev(ast,env,L)===L.top; });
}
function identity(astA,astB,L){
  var uv=Object.keys(usedVars(astA)).concat(Object.keys(usedVars(astB)));
  uv=uv.filter(function(v,i){return uv.indexOf(v)===i;}).sort();
  var rows=combos(uv,L.vals);
  return rows.every(function(env){ return ev(astA,env,L)===ev(astB,env,L); });
}
function renderLawMatrix(){
  var laws=[
    {n:'Excluded middle  A ∨ ¬A', f:function(){return tautology(parse('A | !A'),LOGICS[arguments[0]]);}},
    {n:'Non-contradiction  ¬(A ∧ ¬A)', f:function(){return tautology(parse('!(A & !A)'),LOGICS[arguments[0]]);}},
    {n:'Identity  A → A', f:function(){return tautology(parse('A -> A'),LOGICS[arguments[0]]);}},
    {n:'De Morgan  ¬(A∧B) ≡ ¬A∨¬B', f:function(){return identity(parse('!(A & B)'),parse('!A | !B'),LOGICS[arguments[0]]);}}
  ];
  var tbl=document.getElementById('lawMatrix');
  var head='<tr><th style="text-align:left">law</th>'+ML_ORDER.map(function(k){return '<th>'+LOGICS[k].label.split(' ')[0]+'</th>';}).join('')+'</tr>';
  var body='';
  laws.forEach(function(law){
    body+='<tr><td style="text-align:left">'+law.n+'</td>';
    ML_ORDER.forEach(function(k){
      var ok=law.f(k);
      body+='<td class="'+(ok?'yes':'no')+'">'+(ok?'✓':'✗')+'</td>';
    });
    body+='</tr>';
  });
  tbl.innerHTML=head+body;
}

/* ============================================================
   5. SQL
   ============================================================ */
function initSQL(){
  var L=LOGICS.sql;
  var exprs=[['NULL AND FALSE',L.and_(null,0)],['NULL AND TRUE',L.and_(null,1)],
             ['NULL OR TRUE',L.or_(null,1)],['NULL OR FALSE',L.or_(null,0)],
             ['NOT NULL',L.not_(null)],['NULL = NULL',null]];
  var t='<tr><th style="text-align:left">expression</th><th>value</th></tr>';
  exprs.forEach(function(e){
    var v=e[1];
    t+='<tr><td style="text-align:left">'+e[0]+'</td><td class="out'+valClass(v)+'">'+(v===null?'NULL':(v?'TRUE':'FALSE'))+'</td></tr>';
  });
  document.getElementById('sqlTable').innerHTML=t;

  var ids=[1,2,3,4,5,6,7,8,9,10];
  function notIn(list){
    // count rows where id NOT IN (list) under Kleene 3VL
    return ids.filter(function(id){
      // id NOT IN list  ==  NOT( id IN list )  == NOT( OR over list of (id = x) )
      var eq=L.or_===null?null:null;
      var acc=0; // FALSE
      list.forEach(function(x){ acc=L.or_(acc, (x===null)?null:(id===x?1:0)); });
      var res=L.not_(acc);
      return res===1;
    }).length;
  }
  var msg=document.getElementById('notinMsg');
  function show(kind){
    var list=kind==='null'?[1,2,null]:[1,2];
    var c=notIn(list);
    document.getElementById('notinOut').textContent=c;
    msg.innerHTML = kind==='null'
      ? 'With NULL in the list the comparison <code>id = NULL</code> is never TRUE, so the whole OR is unknown and the row is dropped: <b>0 rows</b>.'
      : 'Drop the NULL and the same query returns <b>8 rows</b> (ids 3…10). One blank in the list silently swallowed the result.';
  }
  [].forEach.call(document.querySelectorAll('[data-notin]'),function(b){
    b.onclick=function(){ [].forEach.call(document.querySelectorAll('[data-notin]'),function(x){x.classList.remove('on');});
      b.classList.add('on'); show(b.dataset.notin); };
  });
  show('null');
}

/* ============================================================
   6. FUZZY
   ============================================================ */
function triangle(x,center,hw){ return Math.max(0,1-Math.abs(x-center)/hw); }
function initFuzzy(){
  var fa=document.getElementById('fa'), fb=document.getElementById('fb');
  function renderTable(){
    var a=parseFloat(fa.value), b=parseFloat(fb.value);
    document.getElementById('faVal').textContent=a.toFixed(2);
    document.getElementById('fbVal').textContent=b.toFixed(2);
    var n=function(x){return 1-x;}, and=Math.min, or=Math.max;
    var rows=[['A AND B',and(a,b)],['A OR B',or(a,b)],['NOT A',n(a)],['A XOR B',or(and(a,n(b)),and(n(a),b))],['A OR NOT A',or(a,n(a))]];
    var t='<tr><th style="text-align:left">expression</th><th>value</th></tr>';
    rows.forEach(function(r){ t+='<tr><td style="text-align:left">'+r[0]+'</td><td>'+r[1].toFixed(3)+'</td></tr>'; });
    document.getElementById('fuzzyTable').innerHTML=t;
  }
  fa.oninput=renderTable; fb.oninput=renderTable; renderTable();

  var temp=document.getElementById('temp');
  function renderFan(){
    var T=parseFloat(temp.value);
    document.getElementById('tempVal').textContent=T;
    var hot=triangle(T,90,30), mild=triangle(T,50,30);
    document.getElementById('hotFire').textContent=hot.toFixed(3);
    document.getElementById('mildFire').textContent=mild.toFixed(3);
    // centroid defuzzification over 0..100
    var lo=0,hi=100,N=1001,sumW=0,sumWX=0;
    for(var i=0;i<N;i++){
      var x=lo+(hi-lo)*i/(N-1);
      var agg=Math.max(Math.min(hot,triangle(x,85,35)), Math.min(mild,triangle(x,30,35)));
      sumW+=agg; sumWX+=x*agg;
    }
    var fan=sumW>0?sumWX/sumW:0;
    document.getElementById('fanOut').textContent=fan.toFixed(2);
    // svg
    var svg='<svg viewBox="0 0 420 200" width="100%">';
    svg+='<line x1="30" y1="170" x2="400" y2="170" stroke="#26314f"/>';
    svg+='<line x1="30" y1="20" x2="30" y2="170" stroke="#26314f"/>';
    var pathHot='', pathMild='';
    for(var i2=0;i2<=100;i2++){
      var xv=i2*3.7+30;
      pathHot += (i2?'L':'M')+xv.toFixed(1)+','+(170-triangle(i2,85,35)*140).toFixed(1);
      pathMild+= (i2?'L':'M')+xv.toFixed(1)+','+(170-triangle(i2,30,35)*140).toFixed(1);
    }
    svg+='<path d="'+pathMild+'" fill="none" stroke="#a78bfa" stroke-width="2"/>';
    svg+='<path d="'+pathHot+'" fill="none" stroke="#fb7185" stroke-width="2"/>';
    svg+='<line x1="'+(fan*3.7+30).toFixed(1)+'" y1="20" x2="'+(fan*3.7+30).toFixed(1)+'" y2="170" stroke="#5eead4" stroke-width="2" stroke-dasharray="4 3"/>';
    svg+='<text x="'+(fan*3.7+34).toFixed(1)+'" y="34" fill="#5eead4" font-family="monospace" font-size="12">fan '+fan.toFixed(1)+'</text>';
    svg+='<text x="34" y="188" fill="#6b7794" font-family="monospace" font-size="11">0</text>';
    svg+='<text x="378" y="188" fill="#6b7794" font-family="monospace" font-size="11">100</text>';
    svg+='<text x="300" y="188" fill="#fb7185" font-family="monospace" font-size="11">hot</text>';
    svg+='<text x="120" y="188" fill="#a78bfa" font-family="monospace" font-size="11">mild</text>';
    svg+='</svg>';
    document.getElementById('fanSvg').outerHTML=svg.replace('<svg','<svg id="fanSvg"');
  }
  temp.oninput=renderFan; renderFan();
}

/* ============================================================
   7. MODAL
   ============================================================ */
function initModal(){
  var worlds=[0,1,2];
  var sees={0:[],1:[],2:[]};
  var pval={0:false,1:false,2:false};
  var box=document.getElementById('worldsBox');
  function render(){
    var html='';
    worlds.forEach(function(w){
      html+='<div class="card" style="margin-bottom:12px"><div class="row" style="justify-content:space-between">'+
        '<b>world '+w+'</b>'+
        '<button class="chip'+(pval[w]?' on':'')+'" data-ptoggle="'+w+'">p = '+(pval[w]?'true':'false')+'</button>'+
        '</div><div class="row mt" style="gap:6px"><span class="tiny">sees →</span>';
      worlds.forEach(function(v){
        html+='<button class="chip'+(sees[w].indexOf(v)>=0?' on':'')+'" data-see="'+w+','+v+'">'+v+'</button>';
      });
      html+='</div></div>';
    });
    box.innerHTML=html;
    wire();
    renderTable();
  }
  function wire(){
    [].forEach.call(box.querySelectorAll('[data-ptoggle]'),function(b){
      b.onclick=function(){ var w=+b.dataset.ptoggle; pval[w]=!pval[w]; render(); }; });
    [].forEach.call(box.querySelectorAll('[data-see]'),function(b){
      b.onclick=function(){ var pr=b.dataset.see.split(','), w=+pr[0], v=+pr[1];
        var i=sees[w].indexOf(v); if(i>=0) sees[w].splice(i,1); else sees[w].push(v); render(); }; });
  }
  function renderTable(){
    var t='<tr><th>world</th><th>p</th><th>□p</th><th>◇p</th><th>◇p ≡ ¬□¬p</th></tr>';
    worlds.forEach(function(w){
      var bx=sees[w].every(function(v){return pval[v];});
      var dx=sees[w].some(function(v){return pval[v];});
      var bxneg=sees[w].every(function(v){return !pval[v];});
      var eq=(dx===(!bxneg));
      t+='<tr><td>'+w+'</td><td class="out'+(pval[w]?1:0)+'">'+(pval[w]?'1':'0')+'</td>'+
         '<td class="out'+(bx?1:0)+'">'+(bx?'1':'0')+'</td><td class="out'+(dx?1:0)+'">'+(dx?'1':'0')+'</td>'+
         '<td class="'+(eq?'yes':'no')+'">'+(eq?'✓':'✗')+'</td></tr>';
    });
    document.getElementById('modalTable').innerHTML=t;
  }
  document.getElementById('modalPreset').onclick=function(){
    sees={0:[1,2],1:[],2:[]}; pval={0:false,1:true,2:false}; render();
  };
  // default: the measured example
  sees={0:[1,2],1:[],2:[]}; pval={0:false,1:true,2:false};
  render();
}

/* ============================================================
   8. QUANTUM (2×2 real linear algebra)
   ============================================================ */
function line(a){ var t=a*Math.PI/180; return [Math.cos(t),Math.sin(t)]; }
function orthonormalize(vecs){
  var basis=[];
  vecs.forEach(function(v){
    var w=v.slice();
    basis.forEach(function(b){ var d=w[0]*b[0]+w[1]*b[1]; w=[w[0]-d*b[0],w[1]-d*b[1]]; });
    var n=Math.hypot(w[0],w[1]); if(n>1e-9) basis.push([w[0]/n,w[1]/n]);
  });
  return basis;
}
function complement(basis){
  if(basis.length===0) return [[1,0],[0,1]];
  if(basis.length>=2) return [];
  var b=basis[0]; return orthonormalize([[-b[1],b[0]]]);
}
function join(A,B){ return orthonormalize(A.concat(B)); }
function meet(A,B){ return complement(join(complement(A),complement(B))); }
function projMat(basis){ var P=[[0,0],[0,0]];
  basis.forEach(function(v){ P[0][0]+=v[0]*v[0]; P[0][1]+=v[0]*v[1]; P[1][0]+=v[1]*v[0]; P[1][1]+=v[1]*v[1]; }); return P; }
function matNorm(P){ return Math.sqrt(P[0][0]*P[0][0]+P[0][1]*P[0][1]+P[1][0]*P[1][0]+P[1][1]*P[1][1]); }
function matSub(A,B){ return [[A[0][0]-B[0][0],A[0][1]-B[0][1]],[A[1][0]-B[1][0],A[1][1]-B[1][1]]]; }

function initQuantum(){
  var pA=document.getElementById('pAng'), qA=document.getElementById('qAng'), rA=document.getElementById('rAng');
  function render(){
    var ap=+pA.value, aq=+qA.value, ar=+rA.value;
    document.getElementById('angP').textContent=ap+'°';
    document.getElementById('angQ').textContent=aq+'°';
    document.getElementById('angR').textContent=ar+'°';
    var P=orthonormalize([line(ap)]), Q=orthonormalize([line(aq)]), R=orthonormalize([line(ar)]);
    var lhs=projMat(meet(P,join(Q,R)));
    var rhs=projMat(join(meet(P,Q),meet(P,R)));
    var lhsDist=matNorm(matSub(lhs,projMat(P)));
    var rhsNorm=matNorm(rhs);
    document.getElementById('qLhs').textContent=lhsDist.toFixed(4);
    document.getElementById('qRhs').textContent=rhsNorm.toFixed(4);
    var v=document.getElementById('qVerdict');
    if(lhsDist<1e-6 && rhsNorm<1e-6){ v.textContent='distributivity HOLDS here (a degenerate case)'; v.className='badge t'; }
    else { v.textContent='distributivity FAILS — left ≠ right'; v.className='badge f'; }
    drawQ(ap,aq,ar);
  }
  function drawQ(ap,aq,ar){
    var cx=170,cy=170,R=130;
    var svg='<svg viewBox="0 0 340 340" width="100%">';
    svg+='<circle cx="'+cx+'" cy="'+cy+'" r="'+R+'" fill="none" stroke="#26314f"/>';
    svg+='<line x1="'+(cx-R-10)+'" y1="'+cy+'" x2="'+(cx+R+10)+'" y2="'+cy+'" stroke="#1c2540"/>';
    svg+='<line x1="'+cx+'" y1="'+(cy-R-10)+'" x2="'+cx+'" y2="'+(cy+R+10)+'" stroke="#1c2540"/>';
    function seg(a,col,lab){
      var t=a*Math.PI/180;
      var x2=cx+Math.cos(t)*R, y2=cy-Math.sin(t)*R;
      var x1=cx-Math.cos(t)*R, y1=cy+Math.sin(t)*R;
      return '<line x1="'+x1.toFixed(1)+'" y1="'+y1.toFixed(1)+'" x2="'+x2.toFixed(1)+'" y2="'+y2.toFixed(1)+'" stroke="'+col+'" stroke-width="3"/>'+
        '<text x="'+(cx+Math.cos(t)*(R+16)).toFixed(1)+'" y="'+(cy-Math.sin(t)*(R+16)).toFixed(1)+'" fill="'+col+'" font-family="monospace" font-size="14">'+lab+'</text>';
    }
    svg+=seg(ap,'#5eead4','p')+seg(aq,'#a78bfa','q')+seg(ar,'#fbbf24','r');
    svg+='<circle cx="'+cx+'" cy="'+cy+'" r="3" fill="#94a0bd"/></svg>';
    document.getElementById('qSvg').outerHTML=svg.replace('<svg','<svg id="qSvg"');
  }
  [pA,qA,rA].forEach(function(x){x.oninput=render;});
  render();
}

/* ============================================================
   9. BOOLEAN FUNCTION EXPLORER
   ============================================================ */
function permutations(arr){
  if(arr.length<=1) return [arr.slice()];
  var out=[];
  arr.forEach(function(x,i){
    var rest=arr.slice(0,i).concat(arr.slice(i+1));
    permutations(rest).forEach(function(p){ out.push([x].concat(p)); });
  });
  return out;
}
function popcount(x){ var c=0; while(x){ c+=x&1; x>>=1; } return c; }
function moebius(f){ var a=f.slice(), n=Math.log2(f.length);
  for(var i=0;i<n;i++) for(var x=0;x<f.length;x++) if((x>>i)&1) a[x]^=a[x^(1<<i)];
  return a; }
function propsOf(f,n){
  var size=1<<n, full=size-1;
  var mono=true;
  for(var a=0;a<size&&mono;a++) for(var b=0;b<size;b++) if((a&b)===a && f[a]>f[b]){ mono=false; break; }
  var selfdual=true;
  for(var x=0;x<size;x++) if(f[x]!==1-f[(~x)&full]){ selfdual=false; break; }
  var anf=moebius(f);
  var affine=anf.every(function(v,S){ return v===0 || popcount(S)<=1; });
  var linear=affine && f[0]===0;
  var perms=permutations(Array.from({length:n},function(_,i){return i;}));
  var symmetric=true;
  for(var pi=0;pi<perms.length&&symmetric;pi++){
    var perm=perms[pi];
    for(var x2=0;x2<size;x2++){
      var y=0; for(var i=0;i<n;i++){ var bit=(x2>>i)&1; y|=bit<<perm[i]; }
      if(f[x2]!==f[y]){ symmetric=false; break; }
    }
  }
  var dependsAll=true;
  for(var i2=0;i2<n;i2++){ var diff=false;
    for(var x3=0;x3<size;x3++) if(f[x3]!==f[x3^(1<<i2)]){ diff=true; break; }
    if(!diff){ dependsAll=false; break; } }
  return {monotone:mono,affine:affine,linear:linear,selfdual:selfdual,symmetric:symmetric,dependsAll:dependsAll};
}
var NAMES2={'0000':'FALSE','0001':'AND','0010':'A∧¬B','0011':'A','0100':'¬A∧B','0101':'B','0110':'XOR','0111':'OR',
  '1000':'NOR','1001':'XNOR','1010':'¬B','1011':'¬B∨A','1100':'¬A','1101':'A→B','1110':'NAND','1111':'TRUE'};

function initBoolean(){
  var nSel=document.getElementById('bfN'), fSel=document.getElementById('bfFilter');
  var cache={};
  function build(n){
    if(cache[n]) return cache[n];
    var size=1<<n, list=[];
    for(var id=0;id<size;id++){
      var f=[]; for(var x=0;x<size;x++) f.push((id>>x)&1);
      var pr=propsOf(f,n);
      list.push({id:id,f:f,p:pr});
    }
    // NPN classes
    var perms=permutations(Array.from({length:n},function(_,i){return i;}));
    var keys={};
    list.forEach(function(item){
      var best=null;
      for(var m=0;m<size;m++) for(var pi=0;pi<perms.length;pi++){
        var perm=perms[pi], g=[];
        for(var x=0;x<size;x++){ var y=0; for(var i=0;i<n;i++){ var bit=(x>>i)&1; if((m>>i)&1) bit^=1; y|=bit<<perm[i]; } g[x]=item.f[y]; }
        for(var o=0;o<2;o++){ var h=g.map(function(v){return o?v^1:v;}).join(''); if(best===null||h<best) best=h; }
      }
      keys[best]=(keys[best]||0)+1; item.npn=best;
    });
    var classIds=Object.keys(keys).sort();
    list.forEach(function(item){ item.npnId=classIds.indexOf(item.npn); });
    var res={list:list,nClasses:classIds.length,counts:keys};
    cache[n]=res; return res;
  }
  function render(){
    var n=(+nSel.value===3)?3:2, data=build(n), filt=fSel.value;
    var pred={all:function(){return true;},linear:function(i){return i.p.linear;},affine:function(i){return i.p.affine;},
      monotone:function(i){return i.p.monotone;},selfdual:function(i){return i.p.selfdual;},
      symmetric:function(i){return i.p.symmetric;},dependsall:function(i){return i.p.dependsAll;}}[filt]||function(){return true;};
    var shown=data.list.filter(pred);
    document.getElementById('bfCount').textContent=shown.length+' / '+data.list.length+' shown';
    var head='<tr><th>#</th><th>truth table</th>'+(n===2?'<th>name</th>':'')+'<th>lin</th><th>aff</th><th>mono</th><th>self-dual</th><th>sym</th><th>all inputs</th><th>NPN</th></tr>';
    var body='';
    shown.slice(0,256).forEach(function(it){
      var tt=it.f.join('');
      body+='<tr><td>'+it.id+'</td><td style="letter-spacing:2px">'+tt+'</td>'+
        (n===2?'<td>'+(NAMES2[tt]||'')+'</td>':'')+
        cell(it.p.linear)+cell(it.p.affine)+cell(it.p.monotone)+cell(it.p.selfdual)+cell(it.p.symmetric)+cell(it.p.dependsAll)+
        '<td>'+it.npnId+'</td></tr>';
    });
    document.getElementById('bfTable').innerHTML=head+body;
    function cell(v){ return '<td class="'+(v?'yes':'no')+'">'+(v?'✓':'·')+'</td>'; }
    var c=data.counts;
    document.getElementById('bfStats').innerHTML=
      '<span>NPN classes <b>'+data.nClasses+'</b></span>'+
      '<span>monotone <b>'+data.list.filter(function(i){return i.p.monotone;}).length+'</b></span>'+
      '<span>self-dual <b>'+data.list.filter(function(i){return i.p.selfdual;}).length+'</b></span>'+
      '<span>symmetric <b>'+data.list.filter(function(i){return i.p.symmetric;}).length+'</b></span>'+
      '<span>linear <b>'+data.list.filter(function(i){return i.p.linear;}).length+'</b></span>';
  }
  nSel.onchange=render; fSel.onchange=render; render();
}

/* ============================================================
   10. DFA
   ============================================================ */
function initDFA(){
  var inp=document.getElementById('dfaIn');
  function run(){
    var s=inp.value.toLowerCase().replace(/[^ab]/g,'');
    var state=0, trace=[];
    for(var i=0;i<s.length;i++){
      var x=(s[i]==='b')?1:0;
      var D=1-x;                 // next state = NOT x
      trace.push({sym:s[i],x:x,from:state,D:D});
      state=D;
    }
    var accept=(state===1);
    document.getElementById('dfaVerdict').textContent=accept?'ACCEPT':'REJECT';
    document.getElementById('dfaVerdict').className='badge '+(accept?'t':'f');
    var t='';
    trace.forEach(function(r){ t+='<div>'+r.sym+'  (x='+r.x+')  →  D = ¬'+r.x+' = '+r.D+'  → q'+r.D+'</div>'; });
    t+='<div style="margin-top:6px">final state q'+state+' · '+(accept?'<span class="v1">accept</span>':'<span class="v0">reject</span>')+'</div>';
    document.getElementById('dfaTrace').innerHTML=t||'<span class="tiny">empty string → q0 (reject)</span>';
    drawDFA(state);
  }
  function drawDFA(state){
    var svg='<svg viewBox="0 0 420 190" width="100%">';
    // circuit: x -> NOT -> D -> flip-flop -> S -> accept
    svg+='<text x="14" y="60" fill="#94a0bd" font-family="monospace" font-size="13">x</text>';
    svg+='<line x1="34" y1="55" x2="96" y2="55" stroke="#5eead4" stroke-width="2.5"/>';
    svg+='<path d="M96,40 L96,70 L130,55 Z" fill="#111a33" stroke="#5eead4" stroke-width="2"/>';
    svg+='<circle cx="138" cy="55" r="6" fill="#0f1730" stroke="#5eead4" stroke-width="2"/>';
    svg+='<text x="104" y="88" fill="#6b7794" font-family="monospace" font-size="11">NOT</text>';
    svg+='<line x1="144" y1="55" x2="180" y2="55" stroke="#a78bfa" stroke-width="2.5"/>';
    svg+='<text x="150" y="42" fill="#a78bfa" font-family="monospace" font-size="12">D</text>';
    // flip flop
    svg+='<rect x="180" y="32" width="86" height="46" rx="8" fill="#111a33" stroke="#a78bfa" stroke-width="2"/>';
    svg+='<text x="196" y="60" fill="#94a0bd" font-family="monospace" font-size="12">flip-flop</text>';
    svg+='<line x1="266" y1="55" x2="320" y2="55" stroke="#5eead4" stroke-width="2.5"/>';
    svg+='<text x="272" y="42" fill="#5eead4" font-family="monospace" font-size="12">S = q'+state+'</text>';
    svg+='<circle cx="326" cy="55" r="7" fill="'+(state===1?'#34d399':'#fb7185')+'"/>';
    svg+='<text x="300" y="86" fill="'+(state===1?'#34d399':'#fb7185')+'" font-family="monospace" font-size="12">'+(state===1?'accept':'reject')+'</text>';
    // feedback loop
    svg+='<path d="M320,120 Q250,150 200,120" fill="none" stroke="#26314f" stroke-width="2" stroke-dasharray="4 3"/>';
    svg+='<text x="240" y="150" fill="#6b7794" font-family="monospace" font-size="11">state feeds back</text>';
    svg+='</svg>';
    document.getElementById('dfaSvg').outerHTML=svg.replace('<svg','<svg id="dfaSvg"');
  }
  document.getElementById('dfaRun').onclick=run;
  inp.addEventListener('keydown',function(e){ if(e.key==='Enter') run(); });
  run();
}

/* ============================================================
   boot
   ============================================================ */
function boot(){
  try{ initGates(); }catch(e){ console.error('gates',e); }
  try{ initUniversal(); }catch(e){ console.error('univ',e); }
  try{ initManyLogics(); }catch(e){ console.error('many',e); }
  try{ initSQL(); }catch(e){ console.error('sql',e); }
  try{ initFuzzy(); }catch(e){ console.error('fuzzy',e); }
  try{ initModal(); }catch(e){ console.error('modal',e); }
  try{ initQuantum(); }catch(e){ console.error('quantum',e); }
  try{ initBoolean(); }catch(e){ console.error('bool',e); }
  try{ initDFA(); }catch(e){ console.error('dfa',e); }
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot);
else boot();
})();
