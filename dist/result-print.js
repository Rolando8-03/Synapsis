import { node } from './matrix-input.js';

export function reportSection(title, content) {
  const section = node('section', 'pdf-section');
  section.append(node('h2','',title), content);
  return section;
}

export async function printReport(title, content) {
  const previous = document.querySelector('#synapsis-print');
  previous?.remove();
  const report = node('article','pdf-report');
  report.id = 'synapsis-print';
  report.setAttribute('aria-hidden','true');
  report.append(node('p','pdf-masthead','Synapsis'), node('h1','',title), ...content);
  document.body.append(report);
  await document.fonts.ready;
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  if (!report.isConnected) return;
  for (const view of report.querySelectorAll('canvas')) {
    view.redrawPlot?.();
    const image = node('img','pdf-graph');
    image.alt = view.getAttribute('aria-label') || 'Gráfica del cálculo';
    try {
      image.src = view.toDataURL('image/png');
      await image.decode();
      view.replaceWith(image);
    } catch {
      // Algunos gráficos dibujados con WebGL deben permanecer en su lienzo.
    }
  }
  if (!report.isConnected) return;
  if (window.SynapsisPrint?.printReport) {
    window.SynapsisPrint.printReport();
    return;
  }
  const oldTitle = document.title;
  const cleanup = () => {
    report.remove();
    document.title = oldTitle;
  };
  window.addEventListener('afterprint', cleanup, {once:true});
  document.title = 'Synapsis · ' + title;
  window.print();
}
