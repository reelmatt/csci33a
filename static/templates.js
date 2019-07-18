// Add a new post with given contents to DOM.
const message_template = Handlebars.compile(document.querySelector('#post').innerHTML);
function add_message(contents) {

    // Create new post.
    const post = post_template({'contents': contents});

    // Add post to DOM.
    document.querySelector('#messageList').innerHTML += post;
}
