document.addEventListener('DOMContentLoaded', () => {
  send_query(); // este es el que ya había, para buscar por cosas al clicar en los que están cargados
});

function send_query() {


  document.getElementById('results').innerHTML = '';
  document.getElementById("results_not_found").style.display = "none";

  const filters = document.querySelectorAll('#filters input, #filters select, #filters [type="radio"]');

  filters.forEach(filter => {
    filter.addEventListener('input', () => {
      const csrfToken = document.getElementById('csrf_token').value;

      const searchCriteria = {
        csrf_token: csrfToken,
        title: document.querySelector('#title').value,
        tags_str: document.querySelector('#tags_str').value,
        publication_type: document.querySelector('#publication_type').value,
        sorting: document.querySelector('[name="sorting"]:checked').value,
        author_name: document.querySelector('#author_name').value,
      };

      console.log('criteria: ', searchCriteria);

      fetch('/explore', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchCriteria),
      })
        .then(response => {
          return response.json()
        })
        .then(data => {

          console.log('data', data);
          document.getElementById('results').innerHTML = '';

          // results counter
          const resultCount = data.length;
          const resultText = resultCount === 1 ? 'dataset' : 'datasets';
          document.getElementById('results_number').textContent = `${resultCount} ${resultText} found`;

          if (resultCount === 0) {
            document.getElementById("results_not_found").style.display = "block";
          } else {
            document.getElementById("results_not_found").style.display = "none";
          }

          const existingButtons = document.querySelectorAll('.btn-download-all');
          console.log('existingButtons', existingButtons);
          existingButtons.forEach(button => button.remove());

          const downloadButton = document.createElement('button');
          downloadButton.className = 'btn btn-outline-primary btn-sm mb-3 btn-download-all';
          downloadButton.textContent = 'Download All Datasets';
          downloadButton.addEventListener('click', () => {
            for (let i = 0; i < data.length; i++) {
              window.open(`/dataset/download/${data[i].id}`);
            }
          });

          document.getElementById('results').insertAdjacentElement('beforebegin', downloadButton);


          data.forEach(dataset => {
            let card = document.createElement('div');
            card.className = 'col-12';
            card.innerHTML = `
                            <div class="card">
                                <div class="card-body">
                                    <div class="d-flex align-items-center justify-content-between">
                                        <h3><a href="${dataset.url}">${dataset.title}</a></h3>
                                        <div>
                                            <span class="badge bg-primary" style="cursor: pointer;" onclick="set_publication_type_as_query('${dataset.publication_type}')">${dataset.publication_type}</span>
                                        </div>
                                    </div>
                                    <p class="text-secondary">${formatDate(dataset.created_at)}</p>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Description
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            <p class="card-text">${dataset.description}</p>
                                        </div>

                                    </div>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Authors
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            ${dataset.authors.map(author => `
                                                <p class="p-0 m-0">${author.name}${author.affiliation ? ` (${author.affiliation})` : ''}${author.orcid ? ` (${author.orcid})` : ''}</p>
                                            `).join('')}
                                        </div>

                                    </div>

                                    <div class="row mb-2">

                                        <div class="col-md-4 col-12">
                                            <span class=" text-secondary">
                                                Tags
                                            </span>
                                        </div>
                                        <div class="col-md-8 col-12">
                                            ${dataset.tags.map(tag => `<span class="badge bg-primary me-1" style="cursor: pointer;" onclick="set_tag_as_query('${tag}')">${tag}</span>`).join('')}
                                        </div>

                                    </div>

                                    <div class="row">

                                        <div class="col-md-4 col-12">

                                        </div>
                                        <div class="col-md-8 col-12">
                                            <a href="${dataset.url}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                View dataset
                                            </a>
                                            <a href="/dataset/download/${dataset.id}" class="btn btn-outline-primary btn-sm" id="search" style="border-radius: 5px;">
                                                Download (${dataset.total_size_in_human_format})
                                            </a>
                                        </div>


                                    </div>

                                </div>
                            </div>
                        `;

            document.getElementById('results').appendChild(card);
          });
        });
    });
  });
}

function formatDate(dateString) {
  const options = { day: 'numeric', month: 'long', year: 'numeric', hour: 'numeric', minute: 'numeric' };
  const date = new Date(dateString);
  return date.toLocaleString('en-US', options);
}

function set_tag_as_query(tagName) {
  clearFilters()
  const tagInput = document.getElementById('tags_str');
  tagInput.value = tagName.trim();
  tagInput.dispatchEvent(new Event('input', { bubbles: true }));
}

function set_publication_type_as_query(publicationType) {
  clearFilters()
  const publicationTypeSelect = document.getElementById('publication_type');
  for (let i = 0; i < publicationTypeSelect.options.length; i++) {
    if (publicationTypeSelect.options[i].text === publicationType.trim()) {
      // Set the value of the select to the value of the matching option
      publicationTypeSelect.value = publicationTypeSelect.options[i].value;
      break;
    }
  }
  publicationTypeSelect.dispatchEvent(new Event('input', { bubbles: true }));
}

document.getElementById('clear-filters').addEventListener('click', clearFilters);

function clearFilters() {

  // Reset the search query
  let titleInput = document.querySelector('#title');
  titleInput.value = "";
  // queryInput.dispatchEvent(new Event('input', {bubbles: true}));

  // Reset the publication type to its default value
  let publicationTypeSelect = document.querySelector('#publication_type');
  publicationTypeSelect.value = "any"; // replace "any" with whatever your default value is
  // publicationTypeSelect.dispatchEvent(new Event('input', {bubbles: true}));

  // Reset the sorting option
  let sortingOptions = document.querySelectorAll('[name="sorting"]');
  sortingOptions.forEach(option => {
    option.checked = option.value == "newest"; // replace "default" with whatever your default value is
    // option.dispatchEvent(new Event('input', {bubbles: true}));
  });

  // Perform a new search with the reset filters
  titleInput.dispatchEvent(new Event('input', { bubbles: true }));
}

document.addEventListener('DOMContentLoaded', () => {

  //let queryInput = document.querySelector('#query');
  //queryInput.dispatchEvent(new Event('input', {bubbles: true}));
  let urlParams = new URLSearchParams(window.location.search);
  let titleParam = urlParams.get('query');

  if (titleParam && titleParam.trim() !== '') {

    const titleInput = document.getElementById('title');
    titleInput.value = titleParam
    titleInput.dispatchEvent(new Event('input', { bubbles: true }));

  } else {
    const titleInput = document.getElementById('title');
    titleInput.dispatchEvent(new Event('input', { bubbles: true }));
  }
});

