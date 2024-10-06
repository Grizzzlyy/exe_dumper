document.addEventListener("DOMContentLoaded", function () {
    const offsetsContainer = document.getElementById("offsets");
    const hexContainer = document.getElementById("hex");
    const decodedTextContainer = document.getElementById("decoded-text");
    let chunkIndex = 0;
    let loading = false;
    let loadedChunks = new Set(); // Track loaded chunks

    // Function to initialize the hex viewer with the file ID
    function initializeHexViewer(fileId) {
        function loadChunk(chunkIndex, clearHex = false, callback = null) {
            // if (loading) return;
            // loading = true;

            fetch(`/hex/${fileId}?chunk_idx=${chunkIndex}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (clearHex) {
                        offsetsContainer.innerHTML = '';
                        hexContainer.innerHTML = '';
                        decodedTextContainer.innerHTML = '';
                        loadedChunks.clear(); // Clear the loaded chunks set
                    }

                    if (data.offsets && data.hex_lines && data.decoded_text) {
                        data.offsets.forEach((offset, index) => {
                            const offsetElement = document.createElement("div");
                            offsetElement.textContent = offset;
                            offsetsContainer.appendChild(offsetElement);

                            const hexElement = document.createElement("div");
                            hexElement.textContent = data.hex_lines[index];
                            hexElement.id = offset; // Assign the offset as the id of the hex element
                            hexContainer.appendChild(hexElement);
                        });

                        data.decoded_text.forEach(decoded => {
                            const decodedElement = document.createElement("div");
                            decodedElement.textContent = decoded;
                            decodedTextContainer.appendChild(decodedElement);
                        });

                        loadedChunks.add(chunkIndex); // Mark the chunk as loaded
                    }
                    loading = false;

                    // Execute callback if provided
//                    if (callback) {
//                        callback();
//                    }
                })
                .catch(error => {
                    console.error("Error loading hex chunk:", error);
                    loading = false;
                });
        }

        function loadTargetChunks(targetOffset) {
            const chunkSize = 1024; // Assuming each chunk is 256 bytes
            const targetChunkIndex = Math.floor(targetOffset / chunkSize);

            // Clear the existing hex data and load target, previous, and next chunks
            let chunksLoaded = 0;

            function onChunkLoaded() {
                chunksLoaded++;
                if (chunksLoaded === 3) {
                    // Once all chunks are loaded, highlight the target element
                    highlightHex(targetOffset, Number(targetLink.getAttribute("length")));
                }
            }

            loadChunk(targetChunkIndex - 1, true, onChunkLoaded);
            loadChunk(targetChunkIndex, false, onChunkLoaded);
            loadChunk(targetChunkIndex + 1, false, onChunkLoaded);
        }

        // Event listener for scrolling
        const hexViewBody = document.querySelector('.hex-view-body');
        hexViewBody.addEventListener("scroll", function () {
            if (hexViewBody.scrollTop + hexViewBody.clientHeight >= hexViewBody.scrollHeight - 10) {
                loadChunk(chunkIndex++);
            }
        });

        // Initial load
        loadChunk(chunkIndex++);

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
                    loadTargetChunks(offset);
                    highlightHex(offset, totalLength);
                } else {
                    // Proceed with highlighting as the target chunk is already loaded
                    highlightHex(offset, totalLength);
                }
            });
        });

        function highlightHex(offset, totalLength) {
            // Remove all existing <span> tags with yellow background
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

            function colorElement(rowDict, element) {
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

            const toColor = createToColor(offset, totalLength);

            toColor.forEach(rowDict => {
                const hex_row = document.getElementById(rowDict.offset);
                if (hex_row) {
                    const coloredHexRow = colorElement(rowDict, hex_row.textContent);

                    hex_row.innerHTML = coloredHexRow;

                    // Scroll to the element
                    hex_row.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });
                }
            });
        }
    }

    // Export the function to be used externally
    window.initializeHexViewer = initializeHexViewer;
});
