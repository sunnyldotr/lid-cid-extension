document.getElementById("start-scraping").addEventListener("click", async () => {
  const searchTerm = document.getElementById("search-term").value.trim();
  const status = document.getElementById("status");

  if (!searchTerm) {
    status.textContent = "Please enter a search term.";
    return;
  }

  status.textContent = "Scraping in progress...";
  
  try {
    const response = await fetch("http://127.0.0.1:5000/scrape", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ search_term: searchTerm })
    });

    if (response.ok) {
      const { file_url } = await response.json();
      status.innerHTML = `Scraping completed. <a href="${file_url}" download>Download CSV</a>`;
    } else {
      status.textContent = "Scraping failed. Try again.";
    }
  } catch (error) {
    status.textContent = "Error connecting to the scraper server.";
  }
});
