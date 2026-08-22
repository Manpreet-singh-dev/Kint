# Modern Vanilla JavaScript & HTML5 Web Application Patterns

## HTML5 Canvas Animation Loop & High-DPI Scaling
When building Canvas games (e.g. Snake, Pong, Arcade) or charts, always handle devicePixelRatio for sharp rendering and use `requestAnimationFrame`:

```javascript
function setupSharpCanvas(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  return { ctx, width: rect.width, height: rect.height };
}

class GameLoop {
  constructor(updateFn, renderFn) {
    this.update = updateFn;
    this.render = renderFn;
    this.lastTime = 0;
    this.running = false;
  }

  start() {
    this.running = true;
    this.lastTime = performance.now();
    requestAnimationFrame(this.loop.bind(this));
  }

  loop(currentTime) {
    if (!this.running) return;
    const delta = (currentTime - this.lastTime) / 1000;
    this.lastTime = currentTime;
    this.update(delta);
    this.render();
    requestAnimationFrame(this.loop.bind(this));
  }

  stop() {
    this.running = false;
  }
}
```

## Web Audio API Sound Generator
Generate synthetic sound effects (beeps, chimes, alerts) without external audio files:

```javascript
class SoundFX {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  playBeep(freq = 440, duration = 0.15, type = 'sine') {
    this.init();
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = type;
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

    gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.start();
    osc.stop(this.ctx.currentTime + duration);
  }
}
```

## HTML5 Drag and Drop Kanban Pattern
Implement smooth drag and drop without third-party libraries:

```javascript
function initKanbanDragAndDrop() {
  const cards = document.querySelectorAll('.kanban-card');
  const columns = document.querySelectorAll('.kanban-column');

  cards.forEach(card => {
    card.setAttribute('draggable', 'true');
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', card.id);
      card.classList.add('dragging');
    });
    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
    });
  });

  columns.forEach(col => {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      col.classList.add('drag-over');
    });
    col.addEventListener('dragleave', () => {
      col.classList.remove('drag-over');
    });
    col.addEventListener('drop', (e) => {
      e.preventDefault();
      col.classList.remove('drag-over');
      const cardId = e.dataTransfer.getData('text/plain');
      const draggedCard = document.getElementById(cardId);
      if (draggedCard) {
        col.querySelector('.card-list').appendChild(draggedCard);
      }
    });
  });
}
```
