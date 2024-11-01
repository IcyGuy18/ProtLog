var ptmSites = null;

document.addEventListener("DOMContentLoaded", () => {
    // Populate checkboxes.
    populateCheckboxes();
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

// Required for highlighting PTMs
function isEnabled(ptm) {
    const checkboxContainer = document.getElementById('checkboxContainer');
    inputs = checkboxContainer.querySelectorAll('input')
    for (i = 0; i < inputs.length; i++) {
        if (ptm == inputs[i].value && inputs[i].checked) {
            return true;
        }
    }
    return false;
}

// We color those amino acids here which can be clicked on
// This function will be called very frequenctly due to its
// extreme dependency
function colorPTMs(e) {
    const sequences = document.getElementById('scrollableTextContainer').getElementsByTagName('span')
    for (i = 0; i < sequences.length; i++) {
        // Check for all spans
        if (sequences[i].title) { // check if a title is assigned first
            if (sequences[i].style.color === 'green') {
                const ptmType = document.getElementById(sequences[i].getAttribute('data-ptm'));
                if (e.value === ptmType.value) {
                    document.getElementById('ptmSiteInfo').style.display = 'none';
                    sequences[i].style.color = 'black';
                }
            } else {
                // Fetch the input tag
                const ptmType = document.getElementById(sequences[i].getAttribute('data-ptm'));
                if (ptmType.checked) { // Now use that input tag to check if it's enabled
                    sequences[i].style.color = 'red';
                } else {
                    sequences[i].style.color = 'black';
                }
            }
        }
    }
}

// Here to popular checkboxes.
function populateCheckboxes() {
    fetch('/ptmkb/api/ptms').then(res => {
        return res.json();
    }).then(data => {
        const checkboxContainer = document.getElementById('checkboxContainer');
        var arr = data['ptms'];
        ptmSites = arr;
        for (i = 0; i < arr.length; i++) {
            const checkboxWrapper = document.createElement('label');
            checkboxWrapper.htmlFor = arr[i];
            checkboxWrapper.innerHTML = `
                <li>
                    <input type="checkbox" id="${arr[i]}" name="${arr[i]}" value="${arr[i]}" checked="true" onchange="colorPTMs(this)">
                    <label for="${arr[i]}">${arr[i]}</label>
                </li>
            `;
            
            checkboxContainer.appendChild(checkboxWrapper);
        }
    });
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
        document.getElementById('form_submit').disabled = true;
        const table = document.getElementById('proteinInfo');
        table.innerHTML = ''
        document.getElementById('foundProtein').style.display = 'none';
        document.getElementById('checkboxContainer').style.display = 'none';
        document.getElementById('iframeContainer').setAttribute('style', "display: block;");
        document.getElementById('iframeLoader').setAttribute('class', 'lds-dual-ring');
        document.getElementById('scrollableTextContainer').style.display = "none";
        document.getElementById('scrollableTextContainer').innerHTML = '';
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
                                    } else
                                        valueCell.textContent = value;
                                    // Special case #2 (this is admittedly just for fun)
                                    valueCell.className = 'value';
                                    row.appendChild(keyCell);
                                    row.appendChild(valueCell);
                                    table.appendChild(row);
                                }
                            }
                            // Now highlight the protein text in the new page

                            // Script for drag-text
                            highlightableText = document.getElementById('scrollableTextContainer');

                            let isMouseDown = false;
                            let startX, scrollLeft;

                            highlightableText.addEventListener('mousedown', (e) => {
                                isMouseDown = true;
                                startX = e.pageX - highlightableText.offsetLeft;
                                scrollLeft = highlightableText.scrollLeft;
                                // console.log(startX, scrollLeft);
                            });

                            highlightableText.addEventListener('mouseleave', () => {
                                isMouseDown = false;
                            });

                            highlightableText.addEventListener('mouseup', () => {
                                isMouseDown = false;
                            });

                            highlightableText.addEventListener('mousemove', (e) => {
                                if (!isMouseDown) return; // Stop the fn from running
                                e.preventDefault(); // Prevent text selection
                                const x = e.pageX - highlightableText.offsetLeft;
                                const walk = (x - startX) * 1; // Scroll-fast
                                highlightableText.scrollLeft = scrollLeft - walk;
                            });

                            // And code for highlighting text
                            for (let index = 0; index < json.proteinSequence.length; index++) {
                                const char = json.proteinSequence[index];
                                const span = document.createElement('span');
                                span.textContent = char;
                                span.className = 'highlightable-text';
                                span.style.fontFamily = 'monospace'

                                // Check if the index is equal to any of the PTM modification positions
                                const matched = ptmSites.find(i => i[0] === (index+1))
                                // If the value is matched, well time to highlight that text~
                                if (matched) {
                                    if (isEnabled(matched[1]))
                                        span.style.color = 'red';
                                    else
                                        span.style.color = 'black';
                                    span.title = `${matched[1]}; Position ${matched[0]}`;
                                    span.setAttribute('data-ptm', matched[1]);
                                    // This is where the magic happens
                                    span.addEventListener('click', (e) => {
                                        // This works - time to add a new popup window
                                        // Remove the previous highlighted blue one
                                        // And assign the selected amino acid the color blue
                                        // If you click on it again, it becomes red
                                        // Important since I will show another HTML subpage
                                        // if an amino acid's color is changed
                                        const s = e.currentTarget
                                        // This is very stupid logic, yeah
                                        ptm = s.title.split(';')[0];
                                        if (isEnabled(ptm)) {
                                            if (s.style.color === 'red') {
                                                // First, remove any green text
                                                const sequences = document.getElementById('scrollableTextContainer').getElementsByTagName('span')
                                                for (i = 0; i < sequences.length; i++) {
                                                    if (sequences[i].style.color === 'green')
                                                        sequences[i].style.color = 'red'
                                                }
                                                // now assign that color haha
                                                s.style.color = 'green';
                                                // First, fill up the Vector table
                                                // Logic's going to be a bit complex for the above stuff
                                                var sequenceArray = [];
                                                for (i = 0; i < sequences.length; i++)
                                                    sequenceArray.push(sequences[i].textContent);
                                                var subsequence = sliceWithPadding(sequenceArray, index);
                                                // Okay I guess not too complex.

                                                // Then the reference data table (whose function is already made!)
                                                loadFile(subsequence, matched);
                                                // highlightableText.querySelectorAll('span').forEach((cs) => {
                                                //     if (cs.style.color === 'green') {
                                                //         cs.style.color = 'red';
                                                //     }
                                                // });
                                                // s.style.color = 'green';
                                                // // console.log(ptm, index);

                                                // also going to center that text
                                                const containerRect = highlightableText.getBoundingClientRect();
                                                const spanRect = s.getBoundingClientRect();

                                                // Calculate the scroll position to center the clicked character
                                                const scrollPosition = spanRect.left - containerRect.left + highlightableText.scrollLeft - (containerRect.width / 2) + (spanRect.width / 2);
                                                
                                                // Scroll the container
                                                highlightableText.scrollTo({
                                                    left: scrollPosition,
                                                    behavior: 'smooth'
                                                });
                                                document.getElementById('ptmSiteInfo').style.display = 'block';
                                            } else {
                                                s.style.color = 'red';
                                                document.getElementById('ptmSiteInfo').style.display = 'none';
                                            }
                                            index = (s.title.match(/\d+$/)[0]) - 1;   
                                        }
                                    });
                                }
                                else {
                                    // Handle every other case (we still show log odd scores and whatnot... maybe?)
                                }
                                highlightableText.appendChild(span);
                            }
                            document.getElementById('scrollableTextContainer').setAttribute('style', "display: block;");
                            document.getElementById('iframeData').textContent = "Protein Info";
                            document.getElementById('iframeData2').textContent = "Modification Sites";
                            document.getElementById('iframeData2Info').textContent = "Hover on a highlighted amino acid to view the PTM; click on a highlighted amino acid to view details of the PTM below."
                            document.getElementById('iframeData3').textContent = "You can click on the boxes below to highlight certain PTMs in the above sequence. They are all enabled by default.";
                            document.getElementById('foundProtein').style.display = 'block';
                            document.getElementById('checkboxContainer').style.display = 'block';
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

async function loadFile(subsequence, matched) {
    const response = await fetch("/ptmkb/api/data?selection=" + matched[1], {
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
        "logOddAtModificationPosition": middle,
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
                tag = "<math><munderover><mo>∑</mo><mn>i=1</mn><mi>n</mi></munderover><mtext>, where i</mtext><mo>≠</mo><mtext>'-inf'</mtext></math>";
            }
            else if (key === "multiplicativeScore") {
                tag = "<math><munderover><mo>∏</mo><mi>i=1</mi><mn>n</mn></munderover><mi>i</mi><mtext>, where i</mtext><mo>≠</mo><mtext>'-inf' and i</mtext><mo>≠</mo><mtext>0</mtext></math>";
            }
            else {
                tag = "<math><mrow><mo>ln</mo><mo>(</mo><mfrac><mn>1</mn><mrow><mrow><mn>-1</mn><mo>×</mo></mrow><munderover><mo>∏</mo><mi>i=1</mi><mn>n</mn></munderover><mi>i</mi></mrow></mfrac><mo>)</mo></mrow><mtext>, where i</mtext><mo>≠</mo><mtext>'-inf' and i</mtext><mo>≠</mo><mtext>0</mtext></math>";
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
            aaHeader.appendChild(cell);
        })
    });

    dataTable.style.display = "table"; // Show the table
}
