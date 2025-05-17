import { Uppy, Dashboard, XHRUpload } from "https://releases.transloadit.com/uppy/v4.15.0/uppy.min.mjs"
import { frLocale } from "/static/assets/js/fr_FR.min.js";

// Track if the user has uploaded a file
let hasUploadedFile = false;
let uploadedFileData = null;

var form = document.getElementById("form_upload");


const uppy = new Uppy({
    debug: true,
    locale: frLocale || {},
    restrictions: {
        maxFileSize: 1000000,
        allowedFileTypes: ['.pdf', '.png', '.jpg', '.jpeg'],
        maxNumberOfFiles: 1,
    }
});

uppy.use(Dashboard, {
    target: '#files-drag-drop', inline: true,
})

uppy.use(XHRUpload, {
    endpoint: 'http://127.0.0.1:5000/upload',  // This is your Flask route
    fieldName: 'file',                         // This matches request.files.getlist('file')
    formData: true,
    bundle: true                               // Sends multiple files in one request
})

// Optional: handle upload success/failure
uppy.on('complete', (result) => {
    alert("test")
    console.log('Upload complete! We’ve uploaded these files:', result.successful)
})

uppy.on('file-added', (file) => {
    console.log('Added file', file);
    hasUploadedFile = true;
    uploadedFileData = file;
});

document.querySelector('#form_upload').addEventListener('submit', async function (e) {
    e.preventDefault();
    const spinner = document.getElementById('spinner-submit');
    // const languageSelect = document.querySelector('select');
    // const detectOrientationCheckbox = document.querySelector('#chkIsDetectOrientation');
    var uploadedFile = null;

    spinner.classList.remove("d-none");

    // Check if user uploaded a file via Uppy
    if (hasUploadedFile) {
        const result = await uppy.upload();
        if (result.successful.length > 0) {
            uploadedFile = result.successful[0].name;

            // Do something with the uploaded file response (e.g., send form data via AJAX)
            console.log('Uploaded file info:', uploadedFile);
            // Submit form data + file metadata here
        }
    } else {
        // Check if a file was selected from the table
        const selected = document.querySelector('input[name="existing_file"]:checked');
        console.log(selected)
        if (selected) {
            uploadedFile = selected.value;
            console.log('Using existing file ID:', uploadedFile);

            // const formData = new FormData();
            // formData.append('language', languageSelect.value);
            // formData.append('detect_orientation', detectOrientationCheckbox.checked);
            // formData.append('existing_file_id', fileId);


            // try {
            //     const response = await fetch("/blank", {
            //         method: "POST",
            //         // Set the FormData instance as the request body
            //         body: formData,
            //     });
            //     console.log(await response.json());
            // } catch (e) {
            //     console.error(e);
            // }
            // const result = await response.json();
            // console.log(result);
        } else {
            alert("Veuillez téléverser un fichier ou en sélectionner un existant.");
        }
    }

    if (uploadedFile) {
        // Inject the uploaded/selected file into the form
        let hiddenInput = document.querySelector('input[name="uploaded_file"]');
        if (!hiddenInput) {
            hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "uploaded_file";
            form.appendChild(hiddenInput);
        }
        hiddenInput.value = uploadedFile;
        form.submit();
    }
    spinner.classList.add("d-none");
});

document.querySelectorAll('.select-file-btn').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault();

        // 1. Get the selected filename from the data attribute
        const filename = button.getAttribute('data-filename');

        // 2. Set it in the hidden form field
        document.getElementById('selected_existing_file').value = filename;

        // 3. Visually indicate selection (optional)
        document.querySelectorAll('.select-file-btn').forEach(btn => btn.classList.remove('btn-success'));
        button.classList.add('btn-success');

        // 4. Clear uploaded file (optional, if one exists)
        // Uppy's internal file state could be reset here if needed
        // uppy.reset();
    });
});