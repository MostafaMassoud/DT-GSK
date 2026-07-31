const input = document.querySelector('.nav-search');
if (input) {
  input.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();
    document.querySelectorAll('.nav-link').forEach((link) => {
      const visible = !query || link.textContent.toLowerCase().includes(query);
      link.style.display = visible ? '' : 'none';
    });
  });
}
