/**
 *  messages.js
 *  Logic for displaying form to send messages to channels
 */

document.addEventListener('DOMContentLoaded', () => {
    // Grab the displayNameSection
    let messageForm = document.querySelector('#messageForm');


    document.querySelector('#messageForm > button').disabled = true;
    // If no user stored locally, present form for them to register
    if ( localStorage.getItem('channel') ) {
        messageForm.style.display = "inherit";

        // By default, submit button is disabled
        // document.querySelector('#messageForm > button').disabled = true;

        // Enable button only if there is text in the input field
        // Modified from code in CSCI s33a lecture 5
        document.querySelector('#messageContents').onkeyup = () => {
            if (document.querySelector('#messageContents').value.length > 0) {
                document.querySelector('#messageForm > button').disabled = false;
            } else {
                document.querySelector('#messageForm > button').disabled = true;
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
    //
    // messageForm.remove();
});
