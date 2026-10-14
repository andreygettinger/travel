/* Atlas-style external labels. Keep existing country geometry and saved places. */
export function addAtlasLabels(svg, places, projection, d3) {
  const W=1200,H=780;
  svg.attr('viewBox',`0 0 ${W} ${H}`);
  const nodes=places.map(p=>({p,xy:projection([p.lon,p.lat])})).filter(v=>v.xy&&v.xy.every(Number.isFinite));
  if(!nodes.length)return;
  const layer=svg.append('g').attr('class','atlas-label-layer');
  const bb=svg.select('.outline').node().getBBox();
  const cx=bb.x+bb.width/2,cy=bb.y+bb.height/2;
  // Labels live in four open gutters, never inside the country silhouette.
  const lanes={top:[],right:[],bottom:[],left:[]};
  nodes.forEach(n=>{
    const [x,y]=n.xy;
    const dx=(x-cx)/(bb.width/2||1),dy=(y-cy)/(bb.height/2||1);
    // Choose a side based on direction from country center; balance congestion.
    const scores={left:-dx,right:dx,top:-dy,bottom:dy};
    const order=Object.keys(scores).sort((a,b)=>scores[b]-scores[a]);
    const side=order.find(s=>lanes[s].length < (s==='top'||s==='bottom'?9:17))||order[0];
    lanes[side].push(n);
  });
  const pad=18, font=15, lineHeight=23;
  function spread(vals,low,high,minGap){
    vals.sort((a,b)=>a.coord-b.coord);
    if(vals.length===1){vals[0].pos=Math.max(low,Math.min(high,vals[0].coord));return;}
    const gap=Math.min(minGap,(high-low)/Math.max(1,vals.length-1));
    vals.forEach((v,i)=>v.pos=Math.max(low,Math.min(high,v.coord)));
    for(let i=1;i<vals.length;i++) vals[i].pos=Math.max(vals[i].pos,vals[i-1].pos+gap);
    if(vals.at(-1).pos>high){const diff=vals.at(-1).pos-high;vals.forEach(v=>v.pos-=diff);}
    if(vals[0].pos<low){const diff=low-vals[0].pos;vals.forEach(v=>v.pos+=diff);}
  }
  const leftEdge=Math.max(220,bb.x-22),rightEdge=Math.min(W-220,bb.x+bb.width+22);
  const topEdge=Math.max(105,bb.y-26),bottomEdge=Math.min(H-100,bb.y+bb.height+26);
  for(const side of ['top','right','bottom','left']){
    const horizontal=side==='top'||side==='bottom';
    const list=lanes[side].map(n=>({...n,coord:horizontal?n.xy[0]:n.xy[1]}));
    if(!list.length)continue;
    spread(list,horizontal?175:95,horizontal?W-175:H-90,horizontal?105:lineHeight);
    for(const n of list){
      const [px,py]=n.xy;
      let tx,ty,anchor;
      if(side==='left'){tx=pad+5;ty=n.pos;anchor='start';}
      else if(side==='right'){tx=W-pad-5;ty=n.pos;anchor='end';}
      else if(side==='top'){tx=n.pos;ty=43;anchor='middle';}
      else {tx=n.pos;ty=H-36;anchor='middle';}
      const group=layer.append('g').attr('class','atlas-callout');
      const label=group.append('a').attr('href',n.p.url||'#');
      if(n.p.url)label.attr('target','_blank').attr('rel','noopener noreferrer');
      const text=label.append('text').attr('class','atlas-callout-text').attr('x',tx).attr('y',ty).attr('text-anchor',anchor).text(n.p.name);
      label.append('title').text(n.p.name);
      const box=text.node().getBBox();
      let ex,ey;
      if(side==='left'){ex=box.x+box.width+7;ey=ty-5;}
      else if(side==='right'){ex=box.x-7;ey=ty-5;}
      else if(side==='top'){ex=tx;ey=box.y+box.height+7;}
      else {ex=tx;ey=box.y-7;}
      const dist=Math.hypot(ex-px,ey-py)||1;
      const sx=px+(ex-px)/dist*10,sy=py+(ey-py)/dist*10;
      // No arrows. Lines finish 7px from the real rendered name.
      const elbow=side==='left'||side==='right'?`L${ex+(side==='left'?13:-13)},${ey}`:`L${ex},${ey+(side==='top'?12:-12)}`;
      group.insert('path','a').attr('class','atlas-callout-line').attr('d',`M${sx},${sy} ${elbow} L${ex},${ey}`);
      group.append('circle').attr('cx',px).attr('cy',py).attr('r',2.5).attr('fill','#e7bd6d').attr('pointer-events','none');
    }
  }
}
