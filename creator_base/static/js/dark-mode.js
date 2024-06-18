<script>
  const toggleButton = document.getElementById('dark-mode-toggle');
  
  toggleButton.addEventListener('change', () => {
    if (toggleButton.checked) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  });
  
  // Check the toggle button based on the user's OS preference
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
  if (prefersDarkScheme.matches) {
    toggleButton.checked = true;
    document.body.classList.add('dark-mode');
  }
</script>
