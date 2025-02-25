window.addEventListener('resize', positionIcon);
window.addEventListener('load', positionIcon);

function positionIcon() {
    const icon = document.querySelector('.icone');
    const footerBackground = document.querySelector('.footer-background');
    const footerRect = footerBackground.getBoundingClientRect();
    icon.style.bottom = `${window.innerHeight - footerRect.top}px`; // Adjusted to be 20px lower
}