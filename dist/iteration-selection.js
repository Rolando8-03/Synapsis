import { node } from './matrix-input.js';

export function iterationSelection(indices) {
  let position = 0;
  const listeners = new Set();
  function select(index) {
    const next = indices.indexOf(index);
    if (next < 0) return;
    position = next;
    for (const listener of listeners) listener(index);
  }
  return {
    select,
    move(offset) {
      const next = Math.max(0, Math.min(position + offset, indices.length - 1));
      select(indices[next]);
    },
    subscribe(listener) {
      listeners.add(listener);
      listener(indices[position]);
    },
    controls() {
      const label = node('label', 'ws-iteration-control', 'Iteración ');
      const input = node('select');
      for (const index of indices) input.add(new Option(index, index));
      input.addEventListener('change', () => select(Number(input.value)));
      this.subscribe(index => { input.value = index; });
      label.append(input);
      return label;
    },
  };
}
