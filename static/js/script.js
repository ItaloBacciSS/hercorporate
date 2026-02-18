document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('expanded');
    });

    // Accordion dos módulos
    document.querySelectorAll('.modulo-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const capitulos = btn.nextElementSibling;
            capitulos.style.display = (capitulos.style.display === 'block') ? 'none' : 'block';
        });
    });
});
