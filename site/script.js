// Draw 15 slightly jittered coordinates on the canvas per load (retro simple)
(function(){
  const canvas = document.getElementById('mapCanvas');
  if(!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.fillStyle = '#fff';
  ctx.fillRect(0,0,w,h);
  ctx.strokeStyle = '#000';
  // draw a simple grid
  ctx.lineWidth = 1;
  for(let x=0;x<w;x+=80){ ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,h); ctx.stroke(); }
  for(let y=0;y<h;y+=60){ ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); }

  // generate 15 points roughly across the canvas
  const pts = [];
  for(let i=0;i<15;i++){
    const gx = Math.floor((i%5)/4 * (w-40)) + 20 + (i%5)*10;
    const gy = Math.floor((i/5)|0 * (h-40)) + 20 + ((i/5)|0)*6;
    const jx = gx + (Math.random()*40 -20);
    const jy = gy + (Math.random()*24 -12);
    pts.push([jx,jy]);
  }

  ctx.fillStyle = '#000';
  for(let i=0;i<pts.length;i++){
    const [x,y] = pts[i];
    ctx.beginPath();
    ctx.arc(x,y,3,0,Math.PI*2);
    ctx.fill();
    ctx.fillText(String(i+1), x+6, y+4);
  }
})();
