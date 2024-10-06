<script>
    document.addEventListener("DOMContentLoaded", function () {
        const offsetsContainer = document.getElementById("offsets");
        const hexContainer = document.getElementById("hex");
        const decodedTextContainer = document.getElementById("decoded-text");
        let chunkIndex = 0;
        let loading = false;
        let loadedChunks = new Set();  // Track loaded chunks

        function loadNextChunk() {
            // if (loading) return;
            // loading = true;

            // Ensure the correct file_id is used in the fetch URL
            const fileId = {{ file_id }};

            fetch(`/hex/${fileId}?chunk_idx=${chunkIndex}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.offsets && data.hex_lines && data.decoded_text) {
                        // Append new chunk to each part of the hex viewer
                        data.offsets.forEach((offset, index) => {
                            const offsetElement = document.createElement("div");
                            offsetElement.textContent = offset;
                            offsetsContainer.appendChild(offsetElement);

                            const hexElement = document.createElement("div");
                            hexElement.textContent = data.hex_lines[index];
                            hexElement.id = offset;  // Assign the offset as the id of the hex element
                            hexContainer.appendChild(hexElement);
                        });

                        data.decoded_text.forEach(decoded => {
                            const decodedElement = document.createElement("div");
                            decodedElement.textContent = decoded;
                            decodedTextContainer.appendChild(decodedElement);
                        });

                        chunkIndex++; // Increase the chunk index for the next load
                    }
                    loading = false;
                })
                .catch(error => {
                    console.error("Error loading hex chunk:", error);
                    loading = false;
                });
        }


        // Event listener for scrolling
        const hexViewBody = document.querySelector('.hex-view-body');
        hexViewBody.addEventListener("scroll", function () {
            if (hexViewBody.scrollTop + hexViewBody.clientHeight >= hexViewBody.scrollHeight - 10) {
                loadNextChunk(); // Load next chunk when reaching the bottom
            }
        });

        // Initial load
        loadNextChunk();

        // Highlighting functionality
        document.querySelectorAll(".hex-link").forEach(link => {
            link.addEventListener("click", function (event) {
                event.preventDefault();

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

                const offset = Number(this.getAttribute("offset"));
                const totalLength = Number(this.getAttribute("length"));
                console.log("Offset:", offset, "totalLength:", totalLength);
                const toColor = createToColor(offset, totalLength);
                console.log(toColor)

                toColor.forEach(rowDict => {
                    const hex_row_id = rowDict.offset
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
            });
        });
    });

</script>
