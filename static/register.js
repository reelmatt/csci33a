/**
 *  register.js
 *  Logic for displaying form to register a user's display name
 */

document.addEventListener('DOMContentLoaded', () => {
    // Grab the displayNameSection
    let displayNameSection = document.querySelector('#displayNameSection');

    // If no user stored locally, present form for them to register
    if ( ! localStorage.getItem('user') ) {
        displayNameSection.style.display = "inherit";

        // By default, submit button is disabled
        document.querySelector('#displayNameSubmit').disabled = true;

        // Enable button only if there is text in the input field
        // Modified from code in CSCI s33a lecture 5        
        document.querySelector('#displayName').onkeyup = () => {
            if (document.querySelector('#displayName').value.length > 0) {
                document.querySelector('#displayNameSubmit').disabled = false;
            } else {
                document.querySelector('#displayNameSubmit').disabled = true;
            }
        };

        // Store the display name value in local storage and remove the form
        document.querySelector('#displayNameForm').onsubmit = () => {
            // Store the name
            let name = document.querySelector("#displayName").value;
            localStorage.setItem('user', name);

            // Remove the section
            displayNameSection.remove();

            // Stop form from submitting
            return false;
        };

        return;
    }

    displayNameSection.remove();
});
