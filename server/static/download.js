async function saveFile() {
    const ptm = document.getElementById("ptmSelect").value;
    const format = document.getElementById("downloadSelect").value;
    fetch(
        "/ptmkb/download",
        {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(
                {
                    "ptm": ptm,
                    "format": format,
                    "rounded": true,
                }
            )
        }
    ).then((res) => {
        if (!res.ok) {
            throw new Error("Failed somewhere");
        }
        return res.blob();
    }).then((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${ptm}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }).catch((error) => {
        console.log(error);
    });
}