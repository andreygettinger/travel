/* Shared Spain-style country labels. Existing silhouettes, saved stars and galleries stay intact. */
function drawExternalLabels(svg, points, outline) {
  const NS = 'http://www.w3.org/2000/svg';
  const make = (tag, parent, attrs={}) => {
    const el=document.createElementNS(NS,tag);
    for(const [k,v] of Object.entries(attrs)) el.setAttribute(k,v);
    parent.appendChild(el);return el;
  };
  const group=make('g',svg,{id:'annotations'});
  const lines=make('g',group);
  const occupied=[];
  const inside=(x,y)=>{ try{return outline.isPointInFill(new DOMPoint(x,y));}catch{return false;} };
  const outside=(b)=>{
    const pad=7;
    const xs=[b.x-pad,b.x+b.width/2,b.x+b.width+pad];
    const ys=[b.y-pad,b.y+b.height/2,b.y+b.height+pad];
    return xs.every(x=>ys.every(y=>!inside(x,y)));
  };
  const overlaps=(a,b,pad=8)=>!(a.x+a.width+pad<b.x || b.x+b.width+pad<a.x || a.y+a.height+pad<b.y || b.y+b.height+pad<a.y);
  // Handle the dense northeast and north-coast groups first.
  const order=[];
  const sorted=[...points].sort((a,b)=>{
    const ia=order.indexOf(a.name),ib=order.indexOf(b.name);
    return (ia<0?100:ia)-(ib<0?100:ib);
  });
  for(const place of sorted){
    const [px,py]=place.xy;
    const link=make('a',group,{href:place.url||'#',target:'_blank',rel:'noopener noreferrer'});
    const text=make('text',link,{class:'atlas-name'});text.textContent=place.name;
    // Existing country-page stars are preserved; do not draw duplicates.
    make('title',link).textContent=place.name;
    const w=text.getComputedTextLength(),h=18;
    let best=null;
    // Search for the shortest tasteful leader, with labels close to the map edge.
    // Each candidate starts at the actual geographic location.
    for(const radius of [24,36,50,65,82,102,125,150,180,215,250,300,360,430]){
      for(let i=0;i<32;i++){
        const angle=i*Math.PI/16;
        const vx=Math.cos(angle),vy=Math.sin(angle);
        const x=px+radius*vx,y=py+radius*vy;
        const anchor=vx>.32?'start':vx<-.32?'end':'middle';
        const bx=anchor==='start'?x:anchor==='end'?x-w:x-w/2;
        const box={x:bx,y:y-h*.76,width:w,height:h};
        if(box.x<10||box.x+box.width>1190||box.y<8||box.y+box.height>772)continue;
        if(!outside(box))continue;
        if(occupied.some(other=>overlaps(box,other)))continue;
        // Favour short lines and modest radial spread; slight penalty for diagonal text crowding.
        const score=radius + (Math.abs(vy)<.22?8:0) + (Math.abs(vx)<.22?4:0);
        if(!best||score<best.score)best={x,y,box,anchor,score};
      }
      if(best)break;
    }
    if(!best){
      // Fallback for exceptionally crowded geography: don't hide the star.
      text.remove();continue;
    }
    occupied.push(best.box);
    text.setAttribute('x',best.x);text.setAttribute('y',best.y);text.setAttribute('text-anchor',best.anchor);
    const tx=Math.max(best.box.x,Math.min(px,best.box.x+best.box.width));
    const ty=Math.max(best.box.y,Math.min(py,best.box.y+best.box.height));
    const dx=tx-px,dy=ty-py,len=Math.hypot(dx,dy)||1;
    const sx=px+dx/len*10,sy=py+dy/len*10;
    const ex=tx-dx/len*4,ey=ty-dy/len*4;
    make('path',lines,{class:'atlas-line',d:`M${sx.toFixed(1)},${sy.toFixed(1)} L${ex.toFixed(1)},${ey.toFixed(1)}`});
  }
}

export function addAtlasLabels(svg, places, projection, d3) {
  const node=svg.node();
  const outline=svg.select('.outline').node();
  if(!node||!outline)return;
  const mapped=places.map(p=>({...p,xy:projection([p.lon,p.lat])})).filter(p=>p.xy&&p.xy.every(Number.isFinite));
  drawExternalLabels(node,mapped,outline);
}
