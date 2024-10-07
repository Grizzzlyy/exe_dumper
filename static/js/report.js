document.addEventListener("DOMContentLoaded", function () {
    const offsetsContainer = document.getElementById("offsets");
    const hexContainer = document.getElementById("hex");
    const decodedTextContainer = document.getElementById("decoded-text");

    let loadedChunks = new Set(); // Track loaded chunks
    let highlighting = false; // Flag to track highlighting state

    // Function to initialize the hex viewer with the file ID
    function initializeHexViewer(fileId) {
        // Load chunk
        function loadChunk(chunkIndex, append = "down", clearHex = false, callback = null) {
            // If chunk is loaded or index out of range
            if (loadedChunks.has(chunkIndex) || chunkIndex < 0) return;

            // Fetch new chunk
            fetch(`/hex/${fileId}?chunk_idx=${chunkIndex}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Clear hex-view
                    if (clearHex) {
                        offsetsContainer.innerHTML = '';
                        hexContainer.innerHTML = '';
                        decodedTextContainer.innerHTML = '';
                        loadedChunks.clear(); // Clear the loaded chunks set
                    }

                    let hexElementToScroll; // Track where we were before loading new element above, to scroll later

                    if (data.offsets && data.hex_lines && data.decoded_text) {
                        // Save where to scroll after prepending new chunk
                        const hexContainerElement = document.getElementById("hex");
                        if (append === "up") {
                            hexElementToScroll = hexContainerElement.firstElementChild; // Get the first child element before adding new elements
                        }

                        // Append or prepend data
                        data.offsets.forEach((offset, index) => {
                            const offsetElement = document.createElement("div");
                            offsetElement.textContent = offset;

                            const hexElement = document.createElement("div");
                            hexElement.textContent = data.hex_lines[index];
                            hexElement.id = offset;

                            const decodedElement = document.createElement("div");
                            decodedElement.textContent = data.decoded_text[index];
                            decodedElement.id = "decoded_" + offset;

                            if (append === "up") {
                                offsetsContainer.prepend(offsetElement);
                                hexContainer.prepend(hexElement);
                                decodedTextContainer.prepend(decodedElement);
                            } else {
                                offsetsContainer.appendChild(offsetElement);
                                hexContainer.appendChild(hexElement);
                                decodedTextContainer.appendChild(decodedElement);
                            }
                        });

                        loadedChunks.add(chunkIndex); // Mark the chunk as loaded
                    }

                    // Scroll back to the first element if it exists
                    if (append === "up") {
                        if (hexElementToScroll) {
                            hexElementToScroll.scrollIntoView({
                                behavior: "auto",
                                block: "start"
                            });
                        }
                    }

                    // Execute callback if provided
                    if (callback) {
                        callback();
                    }
                })
                .catch(error => {
                    console.error("Error loading hex chunk:", error);
                });
        }

        // Load far chunks
        function loadTargetChunks(targetOffset, totalLength) {
            const chunkSize = 1024;
            const targetChunkIndex = Math.floor(targetOffset / chunkSize);

            highlighting = true; // Set highlighting flag

            if (targetChunkIndex == 0) {
                loadChunk(targetChunkIndex, "down", true, () => {
                    loadChunk(targetChunkIndex + 1, "down", false, () => {
                        // Once all chunks are loaded, highlight the target element
                        highlightHex(targetOffset, totalLength);
                        highlighting = false; // Reset highlighting flag
                    });
                });
            } else {
                loadChunk(targetChunkIndex - 1, "down", true, () => {
                    loadChunk(targetChunkIndex, "down", false, () => {
                        loadChunk(targetChunkIndex + 1, "down", false, () => {
                            // Once all chunks are loaded, highlight the target element
                            highlightHex(targetOffset, totalLength);
                            highlighting = false; // Reset highlighting flag
                        });
                    });
                });
            }
        }

        // Load next chunk when scrolling through hex-view
        const hexViewBody = document.querySelector('.hex-view-body');
        hexViewBody.addEventListener("scroll", function () {
            if (highlighting) return; // Prevent loading new chunks during highlighting

            if (hexViewBody.scrollTop + hexViewBody.clientHeight >= hexViewBody.scrollHeight - 10) {
                // Scroll down: load the next chunk
                const maxChunkIndex = Math.max(...loadedChunks);
                loadChunk(maxChunkIndex + 1, "down");
            } else if (hexViewBody.scrollTop <= 10) {
                // Scroll up: load the previous chunk
                const minChunkIndex = Math.min(...loadedChunks);
                loadChunk(minChunkIndex - 1, "up");
            }
        });

        // Initial load
        loadChunk(0);

        // Highlighting functionality
        document.querySelectorAll(".hex-link").forEach(link => {
            link.addEventListener("click", function (event) {
                event.preventDefault();

                const offset = Number(this.getAttribute("offset"));
                const totalLength = Number(this.getAttribute("length"));

                // Determine the chunk index for the given offset
                const chunkSize = 1024;
                const targetChunkIndex = Math.floor(offset / chunkSize);

                if (!loadedChunks.has(targetChunkIndex)) {
                    // Target chunk is not loaded, load required chunks and clear current view
                    loadTargetChunks(offset, totalLength);
                } else {
                    // Proceed with highlighting as the target chunk is already loaded
                    highlightHex(offset, totalLength);
                }
            });
        });

        function highlightHex(offset, totalLength) {
            // Remove existing highlighting
            document.querySelectorAll('.hex-view-table .hex-view-body span').forEach(span => {
                const parent = span.parentNode;
                parent.replaceChild(document.createTextNode(span.textContent), span);
            });

            // Define what to color
            function createToColor(offset, totalLength) {
                const initPos = offset % 16;
                const initOffset = (offset - initPos).toString(16).padStart(9, '0').toUpperCase();
                let initLen;
                if (totalLength <= 16 - initPos) {
                    initLen = totalLength;
                } else {
                    initLen = 16 - initPos;
                }
                totalLength -= initLen;
                let idx = 1;

                const toColor = [
                    { offset: initOffset, pos: initPos, len: initLen }
                ];

                while (totalLength > 0) {
                    const pos = 0;
                    offset = (parseInt(toColor[idx - 1].offset, 16) + 16).toString(16).padStart(9, '0').toUpperCase();
                    const len = Math.min(16, totalLength);

                    totalLength -= len;
                    idx += 1;

                    toColor.push({ offset: offset, pos: pos, len: len });
                }

                return toColor;
            }

            // Highlight something in hex row
            function colorHexRow(rowDict, element) {
                const bytes = element.split(" ");
                const beforeColored = bytes.slice(0, rowDict.pos).join(" ");
                const afterColored = bytes.slice(rowDict.pos + rowDict.len).join(" ");

                const colored = `<span style="background-color: yellow;">${bytes.slice(rowDict.pos, rowDict.pos + rowDict.len).join(" ")}</span>`;

                let res = colored;
                if (beforeColored !== '') {
                    res = beforeColored + ' ' + res;
                }
                if (afterColored !== '') {
                    res += ' ' + afterColored;
                }

                return res;
            }

            // Highlight something in decoded row
            function colorDecodedRow(rowDict, element) {
                const beforeColored = element.slice(0, rowDict.pos);
                const afterColored = element.slice(rowDict.pos + rowDict.len);

                const colored = `<span style="background-color: yellow;">${element.slice(rowDict.pos, rowDict.pos + rowDict.len)}</span>`;

                return beforeColored + colored + afterColored;
            }

            const toColor = createToColor(offset, totalLength);

            toColor.forEach(rowDict => {
                const hex_row = document.getElementById(rowDict.offset);
                const decoded_row = document.getElementById("decoded_"+rowDict.offset);
                if (hex_row) {
                    // Color hex
                    const coloredHexRow = colorHexRow(rowDict, hex_row.textContent);
                    hex_row.innerHTML = coloredHexRow;

                    // Color decoded
                    if (decoded_row) {
                        const coloredDecodedRow = colorDecodedRow(rowDict, decoded_row.textContent);
                        decoded_row.innerHTML = coloredDecodedRow;
                    }
                    // Scroll to the element
                    setTimeout(() => {
                        hex_row.scrollIntoView({
                            behavior: "auto",
                            block: "center"
                        });
                    }, 100);
                } else {
                    console.error("Hex row not found for offset:", rowDict.offset);
                }
            });
        }
    }

    // Export the function to be used externally
    window.initializeHexViewer = initializeHexViewer;
});
