export const terrainWidth = 1000;
export const terrainHeight = 500;

// Coordinates refer to the reference landscape. These describe separate
// surfaces so motion respects the shore, ridgeline and foreground occlusion.
const waterOutline = [
  'M 686 378 C 723 376 789 379 846 378',
  'C 832 381 814 381 807 385 C 801 389 817 394 833 395',
  'C 858 397 885 397 913 399 L 1000 394 L 1000 402',
  'C 955 399 925 403 896 407 L 830 419 L 784 427',
  'C 759 432 747 439 744 447 C 760 452 795 451 816 455',
  'C 874 458 931 453 1000 463 L 1000 500 L 658 500',
  'C 599 477 537 465 473 463 L 452 441 C 516 431 586 435 651 425',
  'C 677 420 708 414 727 408 C 749 402 754 398 738 394',
  'C 722 391 745 383 686 378 Z',
  'M 906 384 C 933 384 965 380 1000 375 L 1000 392',
  'C 982 391 959 392 944 394 L 909 389 Z',
].join(' ');
const ridgeOutline = [
  'M 0 310 L 70 305 L 122 295 L 167 283 L 188 294 L 230 287 L 251 282',
  'L 280 301 L 326 294 L 355 282 L 388 268 L 413 274 L 442 281 L 463 281',
  'L 505 271 L 532 256 L 554 246 L 573 239 L 608 226 L 629 230 L 649 240',
  'L 673 250 L 696 267 L 715 267 L 743 276 L 771 277 L 795 293 L 811 290',
  'L 845 309 L 876 304 L 915 314 L 948 306 L 976 316 L 1000 308',
  'L 1000 411 L 0 383 Z',
].join(' ');
const foregroundOutline = [
  'M 0 323 L 34 331 L 51 316 L 70 354 L 92 326 L 112 367 L 145 377',
  'L 159 354 L 183 393 L 214 402 L 234 391 L 261 429 L 288 416',
  'L 317 447 L 377 450 L 412 415 L 433 443 L 455 438 L 487 470',
  'L 525 472 L 559 463 L 581 477 L 611 482 L 647 470 L 670 490',
  'L 730 496 L 792 481 L 817 488 L 853 474 L 883 483 L 912 474 L 948 481',
  'L 972 477 L 1000 465 L 1000 500 L 0 500 Z',
].join(' ');

export function paths() {
  return {
    water: new Path2D(waterOutline),
    ridge: new Path2D(ridgeOutline),
    foreground: new Path2D(foregroundOutline),
  };
}

export function landscapeMap() {
  const canvas = document.createElement('canvas');
  canvas.width = terrainWidth;
  canvas.height = terrainHeight;
  const context = canvas.getContext('2d');
  const outline = paths();
  const depth = context.createLinearGradient(0, 0, 0, terrainHeight);
  for (const [stop, value] of [[0, 8], [.40, 12], [.58, 29], [.75, 58], [.85, 94], [1, 150]]) {
    depth.addColorStop(stop, `rgb(0,${value},0)`);
  }
  context.fillStyle = depth;
  context.fillRect(0, 0, terrainWidth, terrainHeight);
  context.globalCompositeOperation = 'lighter';
  context.filter = 'blur(5px)';
  context.fillStyle = 'rgb(0,49,0)';
  context.fill(outline.ridge);
  context.fillStyle = 'rgb(0,95,0)';
  context.fill(outline.foreground);
  context.filter = 'blur(1.8px)';
  context.fillStyle = 'rgb(255,0,0)';
  context.fill(outline.water);
  return canvas;
}

export function fitLandscape(width, height, compact) {
  const h = Math.max(height, width / 2) * 1.135;
  const w = h * 2;
  return {
    x: (width - w) * (compact ? .73 : .62),
    y: (height - h) * .54,
    w, h,
  };
}
