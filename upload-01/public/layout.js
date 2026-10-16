// Match the five-column Figma composition at narrower desktop widths.
// The artwork fragments retain their original coordinate system and crop ratios.
function sizeArtwork() {
  const width = document.documentElement.clientWidth;
  document.documentElement.style.setProperty('--desktop-scale', width >= 1100 && width < 1765 ? width / 1765 : 1);
}
sizeArtwork();
window.addEventListener('resize', sizeArtwork, { passive: true });
