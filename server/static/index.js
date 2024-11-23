// Some contants - don't ask me why I'm declaring here.

var ptmSites = null;
var currentSequence = null;

const ptmColorMapping = {
    // Classical colors for more commonly occurring PTMs
    "Acetylation": "#D94F37",  // Slightly darker Tomato
    "Phosphorylation": "#1A7EC7",  // Slightly darker Dodger Blue
    "Ubiquitination": "#2A8B2A",  // Slightly darker Lime Green
    "Methylation": "#D33600",  // Slightly darker Orange Red
    "Oxidation": "#D10000",  // Slightly darker Red
    "Sumoylation": "#1E6B1E",  // Slightly darker Forest Green
    "Dephosphorylation": "#6A1DB0",  // Slightly darker Blue Violet

    // Lighter, pastel-like colors for others
    "ADP-ribosylation": "#F28C9D",  // Slightly darker Light Pink
    "Amidation": "#F13E9C",  // Slightly darker Hot Pink
    "AMPylation": "#E4007D",  // Slightly darker Deep Pink
    "Biotinylation": "#C085C7",  // Slightly darker Plum
    "Blocked amino end": "#D16ED2",  // Slightly darker Violet
    "Butyrylation": "#C155C0",  // Slightly darker Orchid
    "C-linked Glycosylation": "#A850C0",  // Slightly darker Medium Orchid
    "Carbamidation": "#8826B9",  // Slightly darker Dark Orchid
    "Carboxyethylation": "#7326B0",  // Slightly darker Blue Violet
    "Carboxylation": "#6A4FD5",  // Slightly darker Medium Slate Blue
    "Cholesterol ester": "#3A5BAE",  // Slightly darker Royal Blue
    "Citrullination": "#6FA8D7",  // Slightly darker Sky Blue
    "Crotonylation": "#96BFE7",  // Slightly darker Light Blue
    "D-glucuronoylation": "#A2C8D9",  // Slightly darker Powder Blue
    "Deamidation": "#9BDBDB",  // Slightly darker Pale Turquoise
    "Deamination": "#00B0A5",  // Slightly darker Dark Turquoise
    "Decanoylation": "#34D0BD",  // Slightly darker Turquoise
    "Decarboxylation": "#3EACB2",  // Slightly darker Medium Turquoise
    "Disulfide bond": "#00BFBF",  // Slightly darker Aqua
    "Farnesylation": "#00E466",  // Slightly darker Spring Green
    "Formation of an isopeptide bond": "#72E700",  // Slightly darker Chartreuse
    "Formylation": "#9BEB2F",  // Slightly darker Green Yellow
    "Gamma-carboxyglutamic acid": "#8CEB8C",  // Slightly darker Pale Green
    "Geranylgeranylation": "#7ADA7A",  // Slightly darker Light Green
    "Glutarylation": "#00D98D",  // Slightly darker Medium Spring Green
    "Glutathionylation": "#2FB932",  // Slightly darker Lime Green
    "GPI-anchor": "#329756",  // Slightly darker Medium Sea Green
    "Hydroxyceramide ester": "#58B69E",  // Slightly darker Medium Aquamarine
    "Hydroxylation": "#1B9C91",  // Slightly darker Light Sea Green
    "Iodination": "#7C9B86",  // Slightly darker Light Olive Green
    "Lactoylation": "#D1F2D1",  // Slightly darker Honeydew
    "Lactylation": "#D9F8F3",  // Slightly darker Mint Cream
    "Lipoylation": "#C2FFFF",  // Slightly darker Light Cyan
    "Malonylation": "#D1E8FF",  // Slightly darker Alice Blue
    "Myristoylation": "#E4E4E4",  // Slightly darker White Smoke
    "N-carbamoylation": "#FFE3F0",  // Slightly darker Lavender Blush
    "N-linked Glycosylation": "#F0C9D0",  // Slightly darker Misty Rose
    "N-palmitoylation": "#F7E68A",  // Slightly darker Lemon Chiffon
    "Neddylation": "#F6E497",  // Slightly darker Light Goldenrod Yellow
    "Nitration": "#FFFFB3",  // Slightly darker Light Yellow
    "O-linked Glycosylation": "#E2C300",  // Slightly darker Gold
    "O-palmitoleoylation": "#E1D45A",  // Slightly darker Khaki
    "O-palmitoylation": "#E2C300",  // Slightly darker Gold
    "Octanoylation": "#F2D093",  // Slightly darker Moccasin
    "Phosphatidylethanolamine amidation": "#F7E1DD",  // Slightly darker Seashell
    "Propionylation": "#F7D0D0",  // Slightly darker Pink Lavender
    "Pyrrolidone carboxylic acid": "#E8C08D",  // Slightly darker Wheat
    "Pyrrolylation": "#F1C397",  // Slightly darker Navajo White
    "Pyruvate": "#F4D0A9",  // Slightly darker Blanched Almond
    "S-archaeol": "#D1E8FF",  // Slightly darker Alice Blue
    "S-carbamoylation": "#E1D45A",  // Slightly darker Khaki
    "S-Cyanation": "#C9A7D9",  // Slightly darker Thistle
    "S-cysteinylation": "#D1C9E6",  // Slightly darker Lavender
    "S-diacylglycerol": "#B8B8B8",  // Slightly darker Light Gray
    "S-linked Glycosylation": "#A1B7D1",  // Slightly darker Light Steel Blue
    "S-nitrosylation": "#A3A3A3",  // Slightly darker Gray
    "S-palmitoylation": "#A8A8A8",  // Slightly darker Silver
    "Serotonylation": "#C7C7C7",  // Slightly darker Gainsboro
    "Stearoylation": "#F2F2F2",  // Slightly darker Ghost White
    "Succinylation": "#E5E5E5",  // Slightly darker Very Light Gray
    "Sulfation": "#A7C8D9",  // Slightly darker Powder Blue
    "Sulfhydration": "#C7C7C7",  // Slightly darker Gainsboro
    "Sulfoxidation": "#B8B8B8",  // Slightly darker Light Gray
    "Thiocarboxylation": "#D9F8F3",  // Slightly darker Mint Cream
    "Ubiquitination": "#2A8B2A",  // Slightly darker Lime Green
    "UMPylation": "#A3A3A3"  // Slightly darker Gray
};

document.addEventListener("DOMContentLoaded", () => {
    // Populate checkboxes.
    // populateCheckboxes();
    // populateCheckboxesExpanded();
    // Set up an autocomplete function
    $('#form_value').on('input', async function() {
        const requestTerm = $(this).val();
        if (requestTerm.length < 1) {
            $('#suggestions').hide();
            return;
        }

        try {
            const res = await fetch(`/ptmkb/autofill?_id=${requestTerm}`);
            const data = await res.json();
            const suggestions = data['ids'];
            
            const suggestionsBox = $('#suggestions');
            suggestionsBox.empty();
            
            if (suggestions.length > 0) {
                suggestions.forEach(item => {
                    const suggestionItem = $(`<div class="suggestion-item">${item}</div>`);
                    
                    suggestionItem.on('click', function() {
                        $('#form_value').val(item);
                        suggestionsBox.hide();
                    });

                    suggestionsBox.append(suggestionItem);
                });
                suggestionsBox.show();
            } else {
                suggestionsBox.hide();
            }
        } catch (error) {
            console.error("Error: ", error);
            $('#suggestions').hide();
        }
    });

    $(document).on('click', function(event) {
        if (!$(event.target).closest('.input-group').length) {
            $('#suggestions').hide();
        }
    });

    $('#form_value').on('keydown', function(event) {
        if (document.getElementById('form_submit').disabled)
            return;
        if (event.key === 'Enter') {
            search();
        }
    });
});

// Split the sequence like it is done in UniProt
function splitSequence(sequence) {
    const splits = [];
    for (let i = 0; i < sequence.length; i += 10) {
        splits.push(sequence.slice(i, i + 10));
    }
    let total = 0;
    const response = splits.map(split => {
        total += split.length;
        const result = [split, total];
        return result;
    });
    return response;
}

// Function to display additional details about the clicked block
function displayBlockDetails(event) {
    // Get the clicked block element
    const clickedBlock = event.target.closest('.sequence-block'); // Closest ensures we get the right parent div if the span is clicked

    // Retrieve the sequence chunk and block number from the clicked block
    const sequenceText = clickedBlock.querySelector('.sequence-text').textContent;
    const blockNumber = clickedBlock.querySelector('.block-number').textContent;

    // Get additional details for the chunk if available (example: could be fetched from an API or a database)
    const details = `Block Number: ${blockNumber}\nSequence: ${sequenceText}`;

    // Update the content inside the details panel
    const chunkDetailsPanel = document.getElementById('chunkDetails');
    chunkDetailsPanel.textContent = details; // Update the panel with details about the clicked block

    // Show the details panel
    document.getElementById('detailsPanel').style.display = 'block';

    // Remove the 'clicked' class from all blocks
    const allBlocks = document.querySelectorAll('.sequence-block');
    allBlocks.forEach(block => {
        block.classList.remove('clicked');
    });

    // Add the 'clicked' class to the currently clicked block
    clickedBlock.classList.add('clicked');
}

// Function to initialize the sequence blocks and attach event listeners
function initializeBlockClickListeners() {
    const blocks = document.querySelectorAll('.sequence-block');

    // Attach the click event listener to each sequence block
    blocks.forEach(block => {
        block.addEventListener('click', displayBlockDetails);
    });
}

// Function to display the protein sequence with color-coded PTM highlights
function displayProteinSequence(sequence, modificationData) {
    const container = document.getElementById("sequenceDisplayer");

    // Clear any previous content in the container
    container.innerHTML = "";

    // Split the sequence into blocks of 10 characters
    let blocks = splitSequence(sequence);

    // Iterate over each block in the sequence
    blocks.forEach((block, blockIndex) => {
        // Create a block div for each individual block
        const blockDiv = document.createElement("div");
        blockDiv.classList.add("sequence-block");

        // Create a span for each character in the block
        let sequenceText = document.createElement("span");
        sequenceText.classList.add("sequence-text");

        // Create an object to track PTMs at each position
        const ptmsAtPositions = {};

        // Iterate over the characters in the block
        block[0].split('').forEach((char, index) => {
            // Create a span for each character
            const charSpan = document.createElement("span");
            charSpan.textContent = char;

            // Get the global 0-indexed position of this character
            const charIndex = blockIndex * 10 + index;  // Global 0-indexed position

            // Look for all matching modification data entries (first element is index, second is PTM)
            modificationData.forEach((mod, index) => {
                if (mod[0] === charIndex + 1) { // Convert to 1-indexed

                    // Add PTM to the object if it's not already added for this position
                    if (!ptmsAtPositions[charIndex]) {
                        ptmsAtPositions[charIndex] = [];
                    }
                    ptmsAtPositions[charIndex].push(mod[1]);

                    // Get the current 'data-ptm' value from the dataset (if exists)
                    let existingPtms = charSpan.getAttribute('data-ptm') || ''; // Retrieve data-ptm from the dataset

                    // If there are already PTMs, append the new PTM (separate by a semicolon)
                    if (existingPtms !== '') {
                        // Append the new PTM, ensuring no duplicates (separated by semicolons)
                        if (!existingPtms.split(';').includes(mod[1])) {
                            existingPtms += `;${mod[1]}`;
                        }
                        charSpan.setAttribute('data-ptm', existingPtms);
                    } else {
                        // Otherwise, just set the current PTM type
                        charSpan.setAttribute('data-ptm', mod[1]);
                    }
                }
            });

            // // After collecting all PTMs for the character, handle highlighting
            // const ptmsForThisPosition = ptmsAtPositions[charIndex] || [];

            // ptmsForThisPosition.forEach(ptmType => {
            //     const checkbox = document.getElementById(ptmType);
            //     if (checkbox && checkbox.checked && !checkbox.disabled) {
            //         // Add highlight class if checkbox is checked
            //         charSpan.classList.add("highlighted");

            //         // Apply the PTM color from the mapping (multiple PTMs will stack their background)
            //         const color = ptmColorMapping[ptmType] || '#f39c12';  // Default color if PTM not in map
            //         charSpan.style.backgroundColor = color;  // Apply the color
            //     }
            // });

            // After collecting all PTMs for the character, handle highlighting
            const ptmsForThisPosition = ptmsAtPositions[charIndex] || [];

            // Handle multiple PTMs at the same position (apply gradient background)
            if (ptmsForThisPosition.length > 0) {
                // Get colors from ptmColorMapping
                const ptmColors = ptmsForThisPosition.map(ptmType => ptmColorMapping[ptmType] || '#f39c12');

                // Add 'highlighted' class for styling (always add this class)
                charSpan.classList.add("highlighted");

                // If there are multiple PTMs, apply the gradient background class
                if (ptmColors.length > 1) {
                    // Create the gradient using the colors from ptmColorMapping
                    const gradient = ptmColors
                        .map((color, idx) => `${color} ${idx * (100 / ptmColors.length)}%`)
                        .join(', ');

                    // Apply the gradient as a style to the charSpan
                    charSpan.style.background = `linear-gradient(to bottom, ${gradient})`;
                    charSpan.style.backgroundSize = '100% 100%'; // Ensure the gradient covers the entire span

                    // Add the gradient-bg class to indicate that this span has a gradient
                    // charSpan.classList.add("gradient-bg");
                } else {
                    // If only one PTM, apply the single PTM color class
                    charSpan.style.backgroundColor = ptmColors[0];
                }
            }

            // Add a hover event to show the custom tooltip
            charSpan.addEventListener("mouseenter", (e) => {
                const ptmsForThisChar = ptmsAtPositions[charIndex] || [];
                if (ptmsForThisChar.length > 0) {
                    // Create a tooltip element
                    const tooltip = document.createElement("div");
                    tooltip.classList.add("custom-tooltip");
                    tooltip.textContent = ptmsForThisChar.join(", ");  // Display all PTMs for this position

                    // Append the tooltip to the body
                    document.body.appendChild(tooltip);

                    // Position the tooltip near the character
                    const rect = e.target.getBoundingClientRect(); // Get the character's position
                    tooltip.style.position = "absolute";
                    tooltip.style.left = `${rect.left + window.scrollX}px`; // Adjust for any page scroll
                    tooltip.style.top = `${rect.top + window.scrollY - 30}px`; // Position above the character
                    tooltip.style.zIndex = 10; // Ensure it's above other content

                    // Add the 'visible' class to the tooltip to show it
                    setTimeout(() => {
                        tooltip.classList.add("visible");
                    }, 10); // Small delay for the transition to kick in

                    // Store tooltip for later removal
                    e.target.tooltip = tooltip;
                }
            });

            // Add mouseleave event to remove the tooltip
            charSpan.addEventListener("mouseleave", (e) => {
                const tooltip = e.target.tooltip;
                if (tooltip) {
                    tooltip.remove(); // Remove the tooltip when the mouse leaves
                    delete e.target.tooltip; // Clean up the tooltip reference
                }
            });

            // Append the character span to the sequence text span
            sequenceText.appendChild(charSpan);
        });

        // Set the block number
        const blockNumber = document.createElement("span");
        blockNumber.classList.add("block-number");
        blockNumber.textContent = block[1]; // The block number (block[1])

        // Append both the sequence chunk and the block number to the block div
        blockDiv.appendChild(sequenceText);
        blockDiv.appendChild(blockNumber);

        // Append the block div to the main container
        container.appendChild(blockDiv);
    });

    // After blocks are created, initialize the click event listeners
    initializeBlockClickListeners();
}

function updateStats(ptmData) {
    const totalSites = ptmData.length;
    const uniquePTMs = new Set(ptmData.map(ptm => ptm[1])); // Extract unique PTM types
    
    // Count all string values from the third element (semicolon-separated)
    let totalStrings = 0;
    ptmData.forEach(ptm => {
        const strings = ptm[2].split(';'); // Split the third element by semicolon
        totalStrings += strings.length; // Count the number of strings in this list
    });

    // Populate the HTML with the calculated values
    document.getElementById('total-sites').textContent = `${totalSites}`;
    document.getElementById('unique-ptms').textContent = `${uniquePTMs.size}`;
    document.getElementById('experimentally-verified').textContent = `${totalStrings}`;
}

// Function to handle PTM highlighting (this is where you can remove highlights if unchecked)
function colorPTMs(checkbox) {
    const ptmType = checkbox.value;  // PTM type from the checkbox value
    const isChecked = checkbox.checked;

    // Find all highlighted spans in the sequence
    const highlightedSpans = document.getElementById('sequenceDisplayer').querySelectorAll('span');

    highlightedSpans.forEach(span => {
        // Get the list of PTMs applied to the current span (separated by semicolons)
        const ptmsForThisChar = span.getAttribute('data-ptm') ? span.getAttribute('data-ptm').split(';') : [];

        // Check if the span has the corresponding PTM type
        if (ptmsForThisChar.includes(ptmType)) {
            // If unchecked, we need to check if all associated PTM checkboxes are unchecked
            if (!isChecked) {
                // Check if all PTMs for this span are unchecked
                const allOtherPTMUnchecked = ptmsForThisChar.every(ptm => {
                    const checkbox = document.getElementById(ptm);
                    return checkbox && !checkbox.checked;  // Return true if the PTM checkbox is unchecked
                });

                if (allOtherPTMUnchecked) {
                    // Remove the highlight if all PTMs are unchecked
                    span.style.backgroundColor = '';  // Remove the background color (or reset it)
                    span.classList.remove('highlighted');  // Remove the 'highlighted' class
                    span.style.background = '';  // Remove the gradient
                    span.style.backgroundSize = '';  // Remove the background size
                }
            } else if (isChecked) {
                // If the checkbox is checked, add the highlight and handle gradient
                // Check if there are multiple PTMs and apply a gradient
                const ptmsForThisChar = span.getAttribute('data-ptm').split(';');
                if (ptmsForThisChar.length > 1) {
                    const ptmColors = ptmsForThisChar.map(ptm => ptmColorMapping[ptm] || '#f39c12');
                    const gradient = ptmColors
                        .map((color, idx) => `${color} ${idx * (100 / ptmColors.length)}%`)
                        .join(', ');

                    // Apply the gradient as a style to the charSpan
                    span.style.background = `linear-gradient(to bottom, ${gradient})`;
                    span.style.backgroundSize = '100% 100%'; // Ensure the gradient covers the entire span
                } else {
                    // If only one PTM, apply the single PTM color
                    span.style.backgroundColor = ptmColorMapping[ptmType] || '#f39c12';
                }
                span.classList.add('highlighted');  // Add the 'highlighted' class
            }
        }
    });
}

// Function to fetch the PDB file from AlphaFold and render it inside the specified div
async function fetchProteinStructure(uniprotAccession) {
    document.getElementById('protein3DStructure').classList.add('lds-dual-ring')
    const apiUrl = `https://alphafold.ebi.ac.uk/api/prediction/${uniprotAccession}`;

    try {
        // Fetch the list of JSON objects with prediction data
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch prediction data: ${response.statusText}`);
        }

        const data = await response.json();

        // If the response contains multiple entries, you can iterate over them
        for (let entry of data) {
            // Check if the 'pdbUrl' exists in the response entry
            if (entry.pdbUrl) {
                // Fetch the raw PDB file from the pdbUrl
                await fetchAndRenderPDB(entry.pdbUrl);
                break; // Assuming we want to display the first model with a valid pdbUrl
            }
        }

    } catch (error) {
        console.error("Error fetching protein structure:", error);
    }
}

async function fetchAndRenderPDB(pdbUrl) {
    try {
        // Fetch the raw PDB file as bytes
        const response = await fetch(pdbUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch PDB file: ${response.statusText}`);
        }

        const pdbData = await response.text();  // Read as text (PDB format)

        // Remove the loading spinner if present
        document.getElementById('protein3DStructure').classList.remove('lds-dual-ring');

        // Create the viewer inside the #protein3DStructure div
        const viewer = $3Dmol.createViewer("protein3DStructure", { defaultcolors: $3Dmol.rasmolElementColors });

        // Add the model to the viewer
        viewer.addModel(pdbData, "pdb");

        // Apply the visualization style (cartoon representation with color spectrum)
        viewer.setStyle({}, { cartoon: { color: 'spectrum' } });

        // Zoom and render the model
        viewer.zoomTo();
        viewer.render();
        viewer.zoom(1.2, 1000);

        // Access the canvas element created by 3Dmol.js
        const canvas = viewer.getCanvas();

        // Assign a CSS class to the canvas
        canvas.classList.add('top-right-window');  // Add a custom class to the canvas

    } catch (error) {
        console.error("Error rendering PDB file:", error);
    }
}

// USE THIS to populate ONLY APPLICABLE CHECKBOXES
function populateCheckboxesFromResult(data) {
    console.log(data);
    const uniquePTMs = new Set(data.map(ptm => ptm[1]));
    const checkboxContainer = document.getElementById('checkboxContainer');
    // const arr = data['ptms'];

    const checkboxList = [];

    // For each PTM, create a checkbox
    for (let ptm of uniquePTMs.values()) {
        const checkboxWrapper = document.createElement('label');
        checkboxWrapper.htmlFor = ptm;
        checkboxWrapper.innerHTML = `
            <li>
                <input type="checkbox" id="${ptm}" name="${ptm}" value="${ptm}" checked="true">
                <label for="${ptm}">${ptm}</label>
            </li>
        `;

        const color = ptmColorMapping[ptm] || "#FFFFFF";
        const checkboxLabel = checkboxWrapper.querySelector('label');
        checkboxLabel.style.border = `2px solid ${color}`;
        checkboxLabel.style.padding = '5px';
        checkboxLabel.style.marginBottom = '10px';
        checkboxLabel.style.display = 'inline-block';
        checkboxLabel.style.backgroundColor = 'black';
        checkboxLabel.style.color = 'white';

        // Event listener for checkbox change
        checkboxWrapper.querySelector('input').addEventListener('change', (e) => {
            if (e.target.checked) {
                checkboxLabel.style.backgroundColor = 'black';
                checkboxLabel.style.color = 'white';
            } else {
                checkboxLabel.style.backgroundColor = 'white';
                checkboxLabel.style.color = 'black';
            }

            // Call colorPTMs function to update the highlights based on checked boxes
            colorPTMs(e.target);
        });

        checkboxList.push(checkboxWrapper);
        checkboxContainer.appendChild(checkboxWrapper);
    }

    // Filter checkboxes based on search query
    function filterCheckboxes() {
        const query = searchBox.value.toLowerCase();
        checkboxList.forEach(wrapper => {
            const labelText = wrapper.innerText.toLowerCase();
            if (labelText.includes(query)) {
                wrapper.style.display = ''; // Show if it matches
            } else {
                wrapper.style.display = 'none'; // Hide if it doesn't match
            }
        });
    }

    // searchBox.addEventListener('input', filterCheckboxes);
    // filterCheckboxes();
}

// Function for getting the subsequence for vector calculation
function sliceWithPadding(sequenceArray, index, length = 10) {
    const totalLength = 2 * length + 1; // Total items including the index itself
    let start = index - length;
    let end = index + length + 1; // +1 to include the item at `index`

    // Handle cases where the start or end is out of bounds
    if (start < 0) {
        const padding = new Array(-start).fill('-');
        const slice = sequenceArray.slice(0, end);
        return [...padding, ...slice];
    } else if (end > sequenceArray.length) {
        const slice = sequenceArray.slice(start);
        const padding = new Array(end - sequenceArray.length).fill('-');
        return [...slice, ...padding];
    } else {
        return sequenceArray.slice(start, end);
    }
}

async function fetchOptions() {
    const response = await fetch("/api/options");
    const options = await response.json();

    const select = document.getElementById("ptmSelect");

    options.forEach(option => {
        const opt = document.createElement("option");
        opt.value = option;
        opt.textContent = option;
        select.appendChild(opt);
    });
}

// Function's used to add hyperlinks
function convertPubMedReferences(text) {
    const pubMedRegex = /PubMed:(\d+)/g; // Regex to match PubMed references

    return text.replace(pubMedRegex, (match, id) => {
        const url = `https://www.ncbi.nlm.nih.gov/pubmed/?term=${id}`; // Construct the URL
        return `<a href="${url}" target="_blank">${match}</a>`; // Create the link
    });
}

async function search() {
    const id = document.getElementById('form_value').value;
    if (id) {
        document.getElementById('proteinStatisticsContainer').style.display = 'none';
        // document.getElementById('ptmSearch').style.display = 'none';
        document.getElementById('giantCheckboxContainer').style.display = 'none';
        document.getElementById('form_submit').disabled = true;
        const table = document.getElementById('proteinInfo');
        table.innerHTML = ''
        document.getElementById('foundProtein').style.display = 'none';
        document.getElementById('checkboxContainer').style.display = 'none';
        document.getElementById('iframeContainer').setAttribute('style', "display: block;");
        document.getElementById('iframeLoader').setAttribute('class', 'lds-dual-ring');
        document.getElementById('sequenceDisplayer').style.display = "none";
        document.getElementById('sequenceDisplayer').innerHTML = '';
        document.getElementById("tableHead").innerHTML = '';
        document.getElementById("tableBody").innerHTML = '';
        document.getElementById("xlabel").innerHTML = "";
        document.createElement("strong").textContent = '';
        document.getElementById('ptmSiteInfo').style.display = 'none';
        document.getElementById('iframeData').textContent = "Searching protein...";
        document.getElementById('iframeData2').textContent = "";
        document.getElementById('iframeData2Info').textContent = "";
        document.getElementById('iframeData3').textContent = "";
        try {
            const response = await fetch("/ptmkb/search_result", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ "id": id })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.found) {
                    ptmSites = data.result['PTMs']
                    document.getElementById('iframeData').textContent = "Loading protein info...";
                    const proteinInfo = await fetch("/ptmkb/fetch_uniprot", {
                        method: "POST",
                        headers: {
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ "id": id })
                    }).then((res) => {
                        return res.json();
                    }).then((json) => {
                        // Now do something with that JSON.
                        if (json.message === "") {
                            // Time to fill the table
                            for (var [key, value] of Object.entries(json)) {
                                if (key !== "message") {
                                    const row = document.createElement('tr');
                                    const keyCell = document.createElement('td');
                                    const valueCell = document.createElement('td');
                                    keyCell.textContent = key
                                                            .replace(/([a-z](?=[A-Z]))/g, '$1 ')
                                                            .replace(/^./, function(str){ return str.toUpperCase(); })
                                                            .replace('Uni Prot', 'UniProt');
                                    keyCell.className = 'key';
                                    // Special case #1
                                    if (key === 'proteinFunction') {
                                        valueCell.innerHTML = convertPubMedReferences(value);
                                    } else if (key === 'uniProtID' || key === 'uniProtAC') {
                                        valueCell.innerHTML = `<a href="https://www.uniprot.org/uniprotkb/${value}">${value}</a>`;
                                    } else
                                        valueCell.textContent = value;
                                    // Special case #2 (this is admittedly just for fun)
                                    valueCell.className = 'value';
                                    row.appendChild(keyCell);
                                    row.appendChild(valueCell);
                                    table.appendChild(row);
                                }
                            }
                            currentSequence = json.proteinSequence;
                            // Now highlight the protein text in the new page

                            // Script for drag-text
                            // highlightableText = document.getElementById('scrollableTextContainer');

                            // let isMouseDown = false;
                            // let startX, scrollLeft;

                            // highlightableText.addEventListener('mousedown', (e) => {
                            //     isMouseDown = true;
                            //     startX = e.pageX - highlightableText.offsetLeft;
                            //     scrollLeft = highlightableText.scrollLeft;
                            //     // console.log(startX, scrollLeft);
                            // });

                            // highlightableText.addEventListener('mouseleave', () => {
                            //     isMouseDown = false;
                            // });

                            // highlightableText.addEventListener('mouseup', () => {
                            //     isMouseDown = false;
                            // });

                            // highlightableText.addEventListener('mousemove', (e) => {
                            //     if (!isMouseDown) return; // Stop the fn from running
                            //     e.preventDefault(); // Prevent text selection
                            //     const x = e.pageX - highlightableText.offsetLeft;
                            //     const walk = (x - startX) * 1; // Scroll-fast
                            //     highlightableText.scrollLeft = scrollLeft - walk;
                            // });

                            // // And code for highlighting text
                            // for (let index = 0; index < json.proteinSequence.length; index++) {
                            //     const char = json.proteinSequence[index];
                            //     const span = document.createElement('span');
                            //     span.textContent = char;
                            //     span.className = 'highlightable-text';
                            //     span.style.fontFamily = 'monospace'

                            //     // Check if the index is equal to any of the PTM modification positions
                            //     const matched = ptmSites.find(i => i[0] === (index+1))
                            //     // If the value is matched, well time to highlight that text~
                            //     if (matched) {
                            //         if (isEnabled(matched[1]))
                            //             span.style.color = 'red';
                            //         else
                            //             span.style.color = 'black';
                            //         span.title = `${matched[1]}; Position ${matched[0]}`;
                            //         span.setAttribute('data-ptm', matched[1]);
                            //         // This is where the magic happens
                            //         span.addEventListener('click', (e) => {
                            //             // This works - time to add a new popup window
                            //             // Remove the previous highlighted blue one
                            //             // And assign the selected amino acid the color blue
                            //             // If you click on it again, it becomes red
                            //             // Important since I will show another HTML subpage
                            //             // if an amino acid's color is changed
                            //             const s = e.currentTarget
                            //             // This is very stupid logic, yeah
                            //             ptm = s.title.split(';')[0];
                            //             if (isEnabled(ptm)) {
                            //                 if (s.style.color === 'red') {
                            //                     // First, remove any green text
                            //                     const sequences = document.getElementById('scrollableTextContainer').getElementsByTagName('span')
                            //                     for (i = 0; i < sequences.length; i++) {
                            //                         if (sequences[i].style.color === 'green')
                            //                             sequences[i].style.color = 'red'
                            //                     }
                            //                     // now assign that color haha
                            //                     s.style.color = 'green';
                            //                     // First, fill up the Vector table
                            //                     // Logic's going to be a bit complex for the above stuff
                            //                     var sequenceArray = [];
                            //                     for (i = 0; i < sequences.length; i++)
                            //                         sequenceArray.push(sequences[i].textContent);
                            //                     var subsequence = sliceWithPadding(sequenceArray, index);
                            //                     var aa = subsequence[10];
                            //                     // Okay I guess not too complex.

                            //                     // Then the reference data table (whose function is already made!)
                            //                     loadFile(subsequence, matched, aa);
                            //                     // highlightableText.querySelectorAll('span').forEach((cs) => {
                            //                     //     if (cs.style.color === 'green') {
                            //                     //         cs.style.color = 'red';
                            //                     //     }
                            //                     // });
                            //                     // s.style.color = 'green';
                            //                     // // console.log(ptm, index);

                            //                     // also going to center that text
                            //                     const containerRect = highlightableText.getBoundingClientRect();
                            //                     const spanRect = s.getBoundingClientRect();

                            //                     // Calculate the scroll position to center the clicked character
                            //                     const scrollPosition = spanRect.left - containerRect.left + highlightableText.scrollLeft - (containerRect.width / 2) + (spanRect.width / 2);
                                                
                            //                     // Scroll the container
                            //                     highlightableText.scrollTo({
                            //                         left: scrollPosition,
                            //                         behavior: 'smooth'
                            //                     });
                            //                     document.getElementById('ptmSiteInfo').style.display = 'block';
                            //                 } else {
                            //                     s.style.color = 'red';
                            //                     document.getElementById('ptmSiteInfo').style.display = 'none';
                            //                 }
                            //                 index = (s.title.match(/\d+$/)[0]) - 1;   
                            //             }
                            //         });
                            //     }
                            //     else {
                            //         // Handle every other case (we still show log odd scores and whatnot... maybe?)
                            //     }
                            //     highlightableText.appendChild(span);
                            // }
                            
                            fetchProteinStructure(json.uniProtAC);
                            populateCheckboxesFromResult(data.result.PTMs)
                            updateStats(data.result.PTMs)
                            displayProteinSequence(json.proteinSequence, data.result.PTMs);
                            document.getElementById('sequenceDisplayer').setAttribute('style', "display: block;");
                            document.getElementById('iframeData').textContent = "Protein Info";
                            document.getElementById('iframeData2').textContent = "Modification Sites";
                            document.getElementById('iframeData2Info').textContent = "Hover on a highlighted amino acid to view the PTM; click on a highlighted amino acid to view details of the PTM below."
                            document.getElementById('iframeData3').textContent = "You can click on the boxes below to highlight certain PTMs in the above sequence. They are all enabled by default.";
                            document.getElementById('foundProtein').style.display = 'block';
                            document.getElementById('checkboxContainer').style.display = 'block';
                            document.getElementById('giantCheckboxContainer').style.display = 'block';
                            // document.getElementById('ptmSearch').style.display = 'block';
                            document.getElementById('proteinStatisticsContainer').style.display = 'block';
                        }
                        else {
                            alert(json.message);
                            document.getElementById('iframeData').textContent = `${json.message}`;
                        }
                        document.getElementById('iframeLoader').setAttribute('class', '');
                    });
                } else {
                    document.getElementById('iframeData').textContent = "No protein found";
                }
            } else {
                console.error("Response not OK: ", response.statusText);
                document.getElementById('iframeData').textContent = `${response.statusText}`;
            }
        } catch (e) {
            console.error("Error: ", e);
            document.getElementById('iframeData').textContent = `${e}`;
        }
    }
    document.getElementById('form_submit').disabled = false;
    document.getElementById('iframeLoader').setAttribute('class', '');
}

async function loadFile(subsequence, matched, aa) {
    console.log(matched[1], aa);
    const response = await fetch("/ptmkb/api/data?selection=" + matched[1] + "&aa=" + aa, {
        method: 'GET'
    });

    if (response.ok) {
        const jsonData = await response.json();
        displayVector(jsonData, subsequence, matched);
        displayTable(jsonData, matched[1]);
    } else {
        console.error("Error fetching data:", response.statusText);
    }
}

async function fetch_ptm_scores(vectorData, result, middle) {
    let scores = {};
    try {
        const response = await fetch('/ptmkb/get_protein_log', {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(vectorData)
        });
        scores = await response.json();
    } catch (err) {
        scores = {};
    }
    return scores
}

async function displayVector(data, subsequence, result) {
    const KEYS = Object.keys(data);
    var values = new Array();
    KEYS.sort((l, s) => {
        return parseInt(l) - parseInt(s);
    });
    KEYS.forEach((key, index) => {
        if (data[key].hasOwnProperty(subsequence[index])) {
            values.push(
                Math.round(data[key][subsequence[index]] * 100) / 100
            );
        }
        else
            values.push('-inf');
    });

    const middle = values[10];
    // That was easy - Now comes the hard part
    // HTML manupulation...

    // Display the vector first so I can get over this
    var vectorData = new Object();
    KEYS.forEach((key, index) => {
        var item = new Object();
        item[subsequence[index]] = values[index];
        vectorData[key] = item;
    });
    
    const vectorTag = document.getElementById('dataVector');
    const vectorHead = document.getElementById('vectorHead');
    const vectorBody = document.getElementById('vectorBody');
    vectorHead.innerHTML = ''
    vectorBody.innerHTML = ''

    KEYS.forEach((key, index) => {
        const header = document.createElement("th");
        header.textContent = key;
        header.setAttribute("style", "border: 1px solid black; background-color: #A0C4FF;")
        for (let [in_key, value] of Object.entries(vectorData[key])) {
            const cell = document.createElement("td");
            cell.textContent = vectorData[key][in_key];
            if (index == 10)
                cell.style.backgroundColor = '#F2C998';
            vectorBody.appendChild(cell);
        }
        vectorHead.appendChild(header);
    });

    // Now let's calculate the additive and multiplicative scores
    // here...
    // I know, this is a bad idea. I should make an API out of this.
    var scores = await fetch_ptm_scores(vectorData, result, middle)
                .then(json => {
                    return json;
                });
    var json = {
        "modificationType": result[1],
        "modificationPosition": result[0],
        "evidence": result[2],
        "additiveScore": scores['a_score'],
        "multiplicativeScore": scores['m_score'],
        "*-MultiplicativeScore": scores['*_m_score']
    }

    // Now I'll work on the general info on the PTM
    const table = document.getElementById('ptmInfo');
    table.innerHTML = '';
    for (var [key, value] of Object.entries(json)) {
        const row = document.createElement('tr');
        const keyCell = document.createElement('td');
        keyCell.style.fontWeight = 1000;
        const valueCell = document.createElement('td');
        keyCell.textContent = key
                                .replace(/([a-z](?=[A-Z]))/g, '$1 ')
                                .replace(/^./, function(str){ return str.toUpperCase(); })
        keyCell.className = 'key';
        valueCell.className = 'value';
        if (key !== "evidence") {
            valueCell.textContent = value;
        } else {
            splits = json[key].split(';').map(item => "PubMed:" + item.trim());
            var totalText = new String();
            for (i = 0; i < splits.length; i++)
                totalText += convertPubMedReferences(splits[i]) + '; ';
            valueCell.innerHTML = totalText;
        }
        row.appendChild(keyCell);
        row.appendChild(valueCell);
        const notes = document.createElement('td');
        notes.className = 'notes';

        if (key === "additiveScore" || key === "multiplicativeScore" || key === "*-MultiplicativeScore") {
            // Make notes
            var tag = new String();
            if (key === "additiveScore") {
                tag = "<math><munderover><mo>∑</mo><mn>i=1</mn><mi>n</mi></munderover><msub><mi>x</mi><mi>i</mi></msub><mtext>, where&nbsp;</mtext><msub><mi>x</mi><mi>i</mi></msub><mo>≠</mo><mtext>'-inf'</mtext></math>";
            }
            else if (key === "multiplicativeScore") {
                tag = "<math><munderover><mo>∏</mo><mi>i=1</mi><mn>n</mn></munderover><msub><mi>x</mi><mi>i</mi></msub><mtext>, where&nbsp;</mtext><msub><mi>x</mi><mi>i</mi></msub><mo>≠</mo><mtext>'-inf' and&nbsp;</mtext><msub><mi>x</mi><mi>i</mi></msub><mo>≠</mo><mtext>0</mtext></math>";
            }
            else {
                tag = "<math><mrow><mo>ln</mo><mo>(</mo><mfrac><mn>1</mn><mrow><mrow><mn>-1</mn><mo>×</mo></mrow><munderover><mo>∏</mo><mi>i=1</mi><mn>n</mn></munderover><msub><mi>x</mi><mi>i</mi></msub></mrow></mfrac><mo>)</mo></mrow><mtext>, where&nbsp;</mtext><msub><mi>x</mi><mi>i</mi></msub><mo>≠</mo><mtext>'-inf' and&nbsp;</mtext><msub><mi>x</mi><mi>i</mi></msub><mo>≠</mo><mtext>0</mtext></math>";
            }
            notes.innerHTML = tag;
            row.appendChild(notes);
        } else {
            notes.innerHTML = '';
            row.appendChild(notes);
        }
        table.appendChild(row);
    }

    vectorTag.style.display = 'block';
}

function displayTable(data, ptm) {
    const tableHead = document.getElementById("tableHead");
    const tableBody = document.getElementById("tableBody");
    tableHead.innerHTML = "";
    tableBody.innerHTML = "";

    const xlabel = document.getElementById("xlabel");
    xlabel.innerHTML = "";

    const label_x = document.createElement("strong")
    label_x.textContent = `${ptm} - Position Relative to Modification Site`
    
    xlabel.appendChild(label_x);

    const dataTable = document.getElementById("dataTable");

    const AA = "A C D E F G H I K L M N P Q R S T V W Y".split(' ');
    const KEYS = Object.keys(data);
    KEYS.sort((l, s) => {
        return parseInt(l) - parseInt(s);
    });

    AA.forEach(aa => {
        const row = document.createElement("tr");
        row.setAttribute("id", aa);
        const colHeader = document.createElement("th");
        colHeader.textContent = aa;
        colHeader.setAttribute("style", "background-color: #D0E0E3; border: 3px solid black;");
        row.appendChild(colHeader);
        tableBody.appendChild(row);
    });

    // Create a new table from scratch
    const introRow = document.createElement("tr");
    const introHeader = document.createElement("th");
    introHeader.textContent = "Amino Acid";
    introHeader.setAttribute("style", "border: 3px solid black;");
    introRow.appendChild(introHeader);
    tableHead.appendChild(introRow);
    
    var site_index = 0;

    KEYS.forEach((key, index) => {
        const header = document.createElement("th");
        header.textContent = key;
        if (parseInt(key) == 0) {
            site_index = index;
        }
        header.setAttribute("style", "border: 3px solid black; background-color: #A0C4FF;")
        tableHead.children[0].appendChild(header);
    })

    AA.forEach((aa, outer) => {
        
        aaHeader = document.getElementById(aa);

        KEYS.forEach((key, index)=> {
            const cell = document.createElement("td");
            const value = data[key][aa];
            // Set value
            if (typeof value === 'number')
                cell.textContent = value.toFixed(2);
            else
                cell.textContent = "-inf";
            // Set border lines for table
            if (index == Object.keys(KEYS).length - 1)
                cell.setAttribute("style", "border-right: 3px solid black;")
            if (outer == AA.length - 1)
                cell.setAttribute("style", "border-bottom: 3px solid black;")
            if (index == Object.keys(KEYS).length - 1 && outer == AA.length - 1)
                cell.setAttribute("style", "border-right: 3px solid black; border-bottom: 3px solid black;")
            // Set colour
            if (outer%2 == 0)
                cell.style.backgroundColor = '#F0F0F0';
            else
                cell.style.backgroundColor = '#FFFFFF'
            if (index == site_index) {
                cell.style.backgroundColor = '#F2C998';
                cell.style.borderRight = "2px solid black";
                cell.style.borderLeft = "2px solid black";
            }
            cell.style.fontWeight = 700;
            aaHeader.appendChild(cell);
        })
    });

    dataTable.style.display = "table"; // Show the table
}
